#!/bin/bash
# disassemble.sh - Run arm-none-eabi-objdump to disassemble a binary file.
# Usage: ./disassemble.sh <binary_file>

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <binary_file>"
  exit 1
fi

# Remove the extension (everything after the last dot) from the input filename
base="${1%.*}"

arm-none-eabi-objdump -d -S "$1" > "${base}.disasm"
