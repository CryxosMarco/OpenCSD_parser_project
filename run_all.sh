#!/bin/bash
# run_all.sh - A wrapper script that:
#   1. Checks for the file files/tbr.data and, if present, renames it to files/<PROJECT>.data.
#   2. Updates cpu_0.ini and trace.ini by replacing the entire file= line with a new filepath.
#      - In cpu_0.ini, the new line will be: file=files/<PROJECT>.out
#      - In trace.ini, the new line will be: file=files/<PROJECT>.data
#   3. Calls the trace packet lister (/usr/bin/trc_pkt_lister).
#   4. Moves and renames trc_pkt_lister.ppl to files/<PROJECT>.ppl.
#   5. Runs python3 parse_traces.py using files/<PROJECT>.disasm and files/<PROJECT>.ppl,
#      writing the output to parsed_trace_<PROJECT>.txt.
#
# Usage: ./run_all.sh <project_name>
# Example: ./run_all.sh freertos

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <project_name>"
  exit 1
fi

PROJECT="$1"

echo "Checking for files/tbr.data..."
if [ -f "files/tbr.data" ]; then
  echo "Found files/tbr.data, renaming to files/${PROJECT}.data"
  mv "files/tbr.data" "files/${PROJECT}.data"
else
  echo "files/tbr.data not found. Assuming it has already been renamed."
fi

echo "Updating cpu_0.ini..."
# Replace any line beginning with "file=" (allowing optional spaces) with the new value.
sed -i.bak -E "s|^(file\s*=\s*).*$|\1files/${PROJECT}.out|" cpu_0.ini

echo "New cpu_0.ini contents:"
cat cpu_0.ini
echo "------------------------"

echo "Updating trace.ini..."
sed -i.bak -E "s|^(file\s*=\s*).*$|\1files/${PROJECT}.data|" trace.ini

echo "New trace.ini contents:"
cat trace.ini
echo "------------------------"

echo "Calling /usr/bin/trc_pkt_lister..."
/usr/bin/trc_pkt_lister

echo "Moving trc_pkt_lister.ppl to files/${PROJECT}.ppl..."
mv trc_pkt_lister.ppl "files/${PROJECT}.ppl"

echo "Calling python3 parse_traces.py with files/${PROJECT}.disasm and files/${PROJECT}.ppl..."
python3 parse_traces.py "files/${PROJECT}.disasm" "files/${PROJECT}.ppl" > "parsed_trace_${PROJECT}.txt"

echo "Done. Parsed trace saved as parsed_trace_${PROJECT}.txt"
