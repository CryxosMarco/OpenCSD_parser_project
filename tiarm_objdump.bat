@echo off
REM disassemble.bat - Run tiarmobjdump to disassemble a binary file.
REM Usage: disassemble.bat <binary_file>

IF "%~1"=="" (
    echo Usage: %~nx0 ^<binary_file^>
    goto :EOF
)

"C:\ti\ti-cgt-armllvm_4.0.1.LTS\bin\tiarmobjdump.exe" -d -S "%~1" > "files\%~n1.disasm"
