"""
Copyright (c) Marco Milenkovic 2024 IBV - Echtzeit- und Embedded GmbH & Co. KG
SPDX-License-Identifier: Apache-2.0
"""
import re
import argparse

def parse_trace(trace_lines):
    """
    Parse the trace lines and extract the function call/return order,
    including calls made via 'bl' or 'blx' instructions that don't
    generate their own P_HDR events.
    """
    # Matches the header lines
    hdr_re  = re.compile(r'^P_HDR Event:.*Function:\s*([^\)]+)')
    # Matches assembly call instructions, e.g.  bl 0x700003c8 <tm_memory_pool_deallocate>
    call_re = re.compile(r'\bblx?\s+[0-9A-Fxa-fx]+\s+<([^>]+)>')

    # First pass: collect raw events with their instructions
    events = []
    current = None
    for line in trace_lines:
        if line.startswith("P_HDR Event:"):
            if current:
                events.append(current)
            m = hdr_re.search(line)
            current = {"func": m.group(1).strip() if m else None,
                       "instrs": []}
        elif current:
            # record every non-header line under the current event
            current["instrs"].append(line.strip())
    if current:
        events.append(current)

    # Gather all functions that do get their own P_HDR event
    hdr_funcs = {ev["func"] for ev in events if ev["func"]}

    # Now simulate a call stack, emitting Enter/Exit,
    # and also synthetically emit for bl/blx calls to functions _not_ in hdr_funcs
    call_stack = []
    exec_order = []

    for ev in events:
        f = ev["func"]
        # 1) Handle header-driven enters/exits
        if not call_stack:
            call_stack.append(f)
            exec_order.append(f"Enter {f}")
        else:
            if f == call_stack[-1]:
                # same function continuing
                pass
            elif f in call_stack:
                # we’re returning up to an ancestor
                while call_stack and call_stack[-1] != f:
                    exited = call_stack.pop()
                    exec_order.append(f"Exit {exited}")
                # now f is on top again; no new “Enter”
            else:
                # a genuine new call
                call_stack.append(f)
                exec_order.append(f"Enter {f}")

        # 2) Scan this event’s instructions for calls
        for ins in ev["instrs"]:
            cm = call_re.search(ins)
            if cm:
                called = cm.group(1)
                # only synthetic-enter if that function has _no_ P_HDR of its own
                if called not in hdr_funcs:
                    exec_order.append(f"Enter {called}")
                    exec_order.append(f"Exit {called}")

    # finally, unwind any remaining stack
    while call_stack:
        exited = call_stack.pop()
        exec_order.append(f"Exit {exited}")

    return exec_order

def main():
    parser = argparse.ArgumentParser(
        description='Parse a trace file and output the execution order of function calls.'
    )
    parser.add_argument('filepath', help='Path to the trace file.')
    args = parser.parse_args()

    with open(args.filepath) as f:
        trace_lines = f.readlines()

    for evt in parse_trace(trace_lines):
        print(evt)

if __name__ == "__main__":
    main()
