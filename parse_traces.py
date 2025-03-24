#!/usr/bin/env python3
"""
Copyright (c) 2024 IBV - Echtzeit- und Embedded GmbH & Co. KG
SPDX-License-Identifier: Apache-2.0

PROJECT: MASTER THESIS
MODULE: CoreSght-Trace parser
CONTENTS: 
This script parses a disassembly file and a decoded (OpenCSD) trace file from a
Croesight trace, and maps trace events onto disassembled instructions via a
state-machine simulation.

The disassembly parser uses a strict “whitelist” approach - only lines matching

    ^([0-9a-f]+):\s+([0-9a-f ]+)\s+([A-Za-z].*)$

are accepted as valid disassembly lines. All other lines (for example, source code or debug
symbols) are rejected.

A synchronization event (e.g. from a BRANCH_ADDRESS/I_SYNC trace) resets the simulation pointer.
Then each P_HDR event's payload (a string of 'E' and/or 'N') is processed sequentially –
for each payload letter exactly one disassembled instruction (as parsed from the file) is “executed.”
For an executed step ("E"), if the instruction is a branch and a branch target is available,
then the simulation pointer is updated to that target (using a small-offset tolerant lookup);
for a non-executed step ("N"), the pointer simply advances.

In addition, the output now integrates the function context: each P_HDR event group prints the payload
along with the function name (taken from the first executed instruction in that group).

Usage:
    python parse_traces.py <disasm_file> <trace_file> > output_file
"""

import re
import sys
import argparse

# ----- smart_open() -----
def smart_open(filename):
    with open(filename, 'rb') as f:
        raw = f.read(4)
    if raw.startswith(b'\xff\xfe') or raw.startswith(b'\xfe\xff'):
        encoding = 'utf-16'
    elif raw.startswith(b'\xef\xbb\xbf'):
        encoding = 'utf-8-sig'
    else:
        encoding = 'utf-8'
    return open(filename, 'r', encoding=encoding, errors='replace')

# ----- Instruction class -----
class Instruction:
    def __init__(self, address, text, mnemonic, operands, branch_target=None, is_branch=False, function_name=""):
        self.address = address          # integer address
        self.text = text                # the full original line
        self.mnemonic = mnemonic        # e.g. "ldrb", "bic.w", "bl", etc.
        self.operands = operands        # the remainder of the disassembled text
        self.branch_target = branch_target  # integer address or None
        self.is_branch = is_branch      # boolean flag
        self.function_name = function_name  # derived from the last function label line

    def __str__(self):
        return f"{self.address:08x}: {self.text}"

# ----- parse_disassembly() -----
def parse_disassembly(disasm_file):
    instructions = []
    current_function = ""
    
    # Function label lines, e.g.: 700004e8 <tm_pmu_profile_start>:
    label_pattern = re.compile(r'^([0-9a-f]+)\s+<([^>]+)>:$', re.IGNORECASE)
    # Strict instruction pattern:
    strict_inst_pattern = re.compile(r'^([0-9a-f]+):\s+([0-9a-f ]+)\s+([A-Za-z].*)$', re.IGNORECASE)
    
    with smart_open(disasm_file) as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            m_label = label_pattern.match(line)
            if m_label:
                current_function = m_label.group(2)
                continue
            m_inst = strict_inst_pattern.match(line)
            if m_inst:
                addr = int(m_inst.group(1), 16)
                # Group(2) are the hex bytes (ignored here); group(3) is the disassembled instruction.
                inst_text = m_inst.group(3).strip()
                parts = inst_text.split(None, 1)
                if not parts:
                    continue
                mnemonic = parts[0]
                operands = parts[1] if len(parts) > 1 else ""
                lower_mnem = mnemonic.lower()
                # Mark as branch if mnemonic starts with any of these prefixes.
                is_branch = lower_mnem.startswith(("b", "cbnz", "cbz", "tbnz", "tbz"))
                branch_target = None
                if is_branch:
                    m_bt = re.search(r'\b(?:0x)?([0-9a-f]+)\b', operands, re.IGNORECASE)
                    if m_bt:
                        branch_target = int(m_bt.group(1), 16)
                instructions.append(Instruction(addr, line, mnemonic, operands, branch_target, is_branch, current_function))
    instructions.sort(key=lambda inst: inst.address)
    return instructions

# ----- parse_trace() -----
def parse_trace(trace_file):
    events = []
    disasm_line_pattern = re.compile(r'^[0-9a-f]+:\s', re.IGNORECASE)
    with smart_open(trace_file) as f:
        for line in f:
            line = line.rstrip()
            if not line:
                continue
            if disasm_line_pattern.match(line):
                continue
            if "BRANCH_ADDRESS" in line or "I_SYNC" in line:
                m = re.search(r'Addr=(0x[0-9A-Fa-f]+)', line)
                if m:
                    addr = int(m.group(1), 16)
                    events.append({'type': 'sync', 'address': addr, 'raw': line})
                    continue
            if "P_HDR" in line:
                m = re.search(r'P_HDR\s*:\s*Atom P-header\.\s*;\s*([EN]+)', line)
                if m:
                    payload = m.group(1)
                    events.append({'type': 'p_hdr', 'payload': payload, 'raw': line})
                    continue
                else:
                    parts = line.split(';')
                    if parts:
                        payload = parts[-1].strip()
                        events.append({'type': 'p_hdr', 'payload': payload, 'raw': line})
                        continue
    return events

# ----- get_idx() -----
def get_idx(event):
    raw = event.get('raw', '')
    m = re.search(r'Idx:(\d+)', raw)
    return m.group(1) if m else "N/A"

# ----- adjust_jump_target() -----
def adjust_jump_target(instructions, target_addr):
    # First try to find the exact target address.
    for i, inst in enumerate(instructions):
        if inst.address == target_addr:
            return i
    # If not found, try to find the next instruction after the target address.
    candidate = target_addr + 2
    for i, inst in enumerate(instructions):
        if inst.address == candidate:
            return i
    return None

# ----- simulate_execution() -----
def simulate_execution(current_index, payload, instructions, current_function):
    steps = []
    for letter in payload:
        if current_index >= len(instructions):
            break
        inst = instructions[current_index]
        steps.append(inst)
        if letter.upper() == 'E':
            if inst.is_branch and inst.branch_target is not None:
                new_index = adjust_jump_target(instructions, inst.branch_target)
                if new_index is not None:
                    current_index = new_index
                    current_function = instructions[new_index].function_name
                else:
                    current_index += 1
            else:
                current_index += 1
        else:
            current_index += 1
    return steps, current_index, current_function

# ----- map_trace_to_disassembly() -----
def map_trace_to_disassembly(instructions, trace_events):
    groups = []
    current_index = 0  # Global simulation pointer into instructions
    current_function = ""
    for event in trace_events:
        etype = event.get('type')
        if etype == 'sync':
            target_addr = event.get('address')
            new_index = adjust_jump_target(instructions, target_addr)
            if new_index is not None:
                current_index = new_index
                current_function = instructions[new_index].function_name
            else:
                for i, inst in enumerate(instructions):
                    if inst.address == target_addr:
                        current_index = i
                        current_function = inst.function_name
                        break
            groups.append((get_idx(event), event, None))
        elif etype == 'p_hdr':
            payload = event.get('payload', '')
            steps, current_index, current_function = simulate_execution(current_index, payload, instructions, current_function)
            groups.append((get_idx(event), event, steps))
    return groups

# ----- main() -----
def main():
    parser = argparse.ArgumentParser(description="State-machine based trace-to-disassembly mapping")
    parser.add_argument("disasm_file", help="Path to the disassembly file")
    parser.add_argument("trace_file", help="Path to the decoded trace file")
    args = parser.parse_args()

    instructions = parse_disassembly(args.disasm_file)
    print(f"Parsed {len(instructions)} valid disassembly lines.\n")

    trace_events = parse_trace(args.trace_file)
    print(f"Parsed {len(trace_events)} trace events.\n")

    groups = map_trace_to_disassembly(instructions, trace_events)

    for idx, event, steps in groups:
        event_type = event.get('type')
        if event_type == 'sync':
            print("Sync: " + event.get('raw', ''))
        elif event_type == 'p_hdr':
            payload = event.get('payload', '')
            # Integrate function name from the first executed instruction (if available)
            func_name = steps[0].function_name if steps and steps[0].function_name else "<unknown>"
            print(f"P_HDR Event: Idx:{idx} (Pattern: {payload}, Function: {func_name})")
            if steps:
                print("Executed Assembly Steps:")
                for i, inst in enumerate(steps, start=1):
                    print(f"  {i}. {inst.text}")
            else:
                print(" This should not happen: no steps executed.")
        print("")

if __name__ == "__main__":
    main()
