import re
import argparse

def parse_trace(trace_lines):
    """
    Parse the trace lines and extract the function call/return order.

    The parser looks for lines like:
       P_HDR Event: ... Function: <functionName>
    It then merges consecutive duplicate events (which occur when a function’s
    block is split into multiple events due to a maximum block size).
    Finally, it simulates a call stack:
      - When a new function appears that is not the current top of the stack,
        it is considered an "enter" (a call).
      - When a function reappears that is already in the stack (but not on top),
        that is taken as a return (pop inner calls) back to that function.
    """
    # Regular expression to match lines with a function field.
    func_re = re.compile(r'Function:\s*([^\)]+)')

    events = []
    current_event = None

    # Go line by line looking for "P_HDR Event:" lines.
    for line in trace_lines:
        line = line.strip()
        if line.startswith("P_HDR Event:"):
            # When a new event is encountered, append the current event if exists.
            if current_event is not None:
                events.append(current_event)
            current_event = {"func": None, "instr_count": 0}
            # Look for a "Function:" in the header line.
            m = func_re.search(line)
            if m:
                current_event["func"] = m.group(1).strip()
        else:
            # Non-header lines (assumed assembly instructions) increment the instruction count.
            if current_event is not None:
                current_event["instr_count"] += 1

    # Append the last event if any.
    if current_event is not None:
        events.append(current_event)

    # Merge contiguous events that are from the same function.
    merged_funcs = []
    for event in events:
        func = event["func"]
        if func is None:
            continue
        if merged_funcs and merged_funcs[-1] == func:
            # Assume a continuation of a very long function.
            continue
        merged_funcs.append(func)

    # Simulate a call stack to record "enter" and "exit" events.
    call_stack = []
    exec_order = []  # List of strings describing call/return events.

    for func in merged_funcs:
        if not call_stack:
            # No function is active; push this function.
            call_stack.append(func)
            exec_order.append(f"Enter {func}")
        else:
            if func == call_stack[-1]:
                # Same function block continuation; no new event.
                continue
            elif func in call_stack:
                # The function is already in the stack; pop until it's on top.
                while call_stack and call_stack[-1] != func:
                    exited = call_stack.pop()
                    exec_order.append(f"Exit {exited}")
                # Now 'func' is at the top.
            else:
                # New function call.
                call_stack.append(func)
                exec_order.append(f"Enter {func}")

    # At the end, record the exit for all remaining functions.
    while call_stack:
        exited = call_stack.pop()
        exec_order.append(f"Exit {exited}")

    return exec_order

def main():
    parser = argparse.ArgumentParser(
        description='Parse a trace file and output the execution order of function calls.'
    )
    parser.add_argument('filepath', help='Path to the trace file (text format).')
    args = parser.parse_args()

    try:
        with open(args.filepath, 'r') as f:
            trace_lines = f.readlines()
    except IOError as e:
        print(f"Error reading file: {e}")
        return

    execution_order = parse_trace(trace_lines)
    print("Execution order:")
    for event in execution_order:
        print(event)

if __name__ == "__main__":
    main()
