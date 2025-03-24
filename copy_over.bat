@echo off
REM copy_outputs.bat - Copy .out or .elf files from each Debug folder in the workspace,
REM rename certain .out files to a shorter name (suppressing the original),
REM and finally copy E:\tbr.data to the destination folder.
REM Usage: Run the script from the command line or double-click it.

REM Set the source root (adjust if needed)
set "SOURCE=C:\Users\ibv-user\workspace_v12"
REM Set the destination folder
set "DEST=E:\IBV\PROJEKTE\MASTER_ARBEIT\WORKSPACE\Traces\work\files"

echo Copying .out and .elf files from Debug folders in %SOURCE% to %DEST%
echo.

REM --- Process .out files ---
for /d %%D in ("%SOURCE%\*") do (
    REM Check if a Debug folder exists inside this project folder
    if exist "%%D\Debug" (
        echo Found Debug folder in %%D
        REM Loop through all .out files in the Debug folder.
        for %%F in ("%%D\Debug\*.out") do (
            if exist "%%F" (
                REM Check for special names using nested IFs
                if /I "%%~nxF"=="threadx_hello_world_am243x-evm_r5fss0-0_threadx_ti-arm-clang.out" (
                    echo Copying and renaming %%F to threadx.out
                    copy /Y "%%F" "%DEST%\threadx.out"
                ) else (
                    if /I "%%~nxF"=="task_switch_am243x-lp_r5fss0-0_freertos_ti-arm-clang.out" (
                        echo Copying and renaming %%F to freertos.out
                        copy /Y "%%F" "%DEST%\freertos.out"
                    ) else (
                        echo Copying %%F
                        copy /Y "%%F" "%DEST%"
                    )
                )
            )
        )
    )
)

echo.
REM --- Process .elf files ---
for /d %%D in ("%SOURCE%\*") do (
    REM Check if a Debug folder exists inside this project folder
    if exist "%%D\Debug" (
        echo Found Debug folder in %%D
        REM Loop through all .elf files in the Debug folder.
        for %%F in ("%%D\Debug\*.elf") do (
            if exist "%%F" (
                echo Copying %%F
                copy /Y "%%F" "%DEST%"
            )
        )
    )
)

echo.
REM --- Copy tbr.data from E:\ to the destination folder ---
echo Copying E:\tbr.data to %DEST%
copy /Y "E:\tbr.data" "%DEST%"

echo.
echo Done.
