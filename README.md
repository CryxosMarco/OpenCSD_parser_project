# Trace Analysis Workflow (OpenCSD-based)

This folder contains scripts and tools for handling ARM CoreSight trace data (ETB/ETM) on the AM243x device (R5F core), using OpenCSD (`trc_pkt_lister`) for decoding and Python for post-processing. This is work in progress and not in any means a final version. You may encounter errors or issues using this repository.

---
## Prerequisites
This work was primarily written for use with TI's CodeComposerStudio and the AM24x EVM Platform
- You need to setup a working directory within CCS and attach the debugger to the Core
- You need to get and install the [OpenCSD Project](https://github.com/Linaro/OpenCSD.git)
- If you want to use this parser with another Board/Core you need to adjust the settings within the .ini files. cpu_0.ini and device_6.ini for the device registers you can refer to the section "Setting up OpenCSD".
- This was done on a Windows machine with use of WSL. It's not tested on other Systems


## Setting up OpenCSD
The .inis here are tuned to work with the AM24x and the R5F Core. I you want to use different Hardware here you have to setup it by yourself.
- Either way I recommend on first use to run in the CCS "Scripting console" after attaching the debugger to the core and starting the CoreSight trace module:
```
print("ETMCR(id:0x0)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C000).toString(16))
print("ETMCCR(id:0x1)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C004).toString(16))
print("ETMASICCR(id:0x3)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C00C).toString(16))
print("ETMSCR(id:0x5)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C014).toString(16))
print("ETMTSSCR(id:0x6)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C018).toString(16))
print("ETMTEEVR(id:0x8)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C020).toString(16))
print("ETMFFLR(id:0xB)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C02C).toString(16))
print("ETMVDCR1(id:0xD)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C034).toString(16))
print("ETMVDCR2(id:0xE)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C038).toString(16))
print("ETMVDCR3(id:0xF)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C03C).toString(16))
print("ETMACVR1(id:0x10)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C040).toString(16))
print("ETMACVR2(id:0x11)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C044).toString(16))
print("ETMACVR3(id:0x12)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C048).toString(16))
print("ETMACVR4(id:0x13)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C04C).toString(16))
print("ETMACVR5(id:0x14)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C050).toString(16))
print("ETMACVR6(id:0x15)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C054).toString(16))
print("ETMACVR7(id:0x16)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C058).toString(16))
print("ETMACVR8(id:0x17)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C05C).toString(16))
print("ETMACVR9(id:0x18)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C060).toString(16))
print("ETMACVR14(id:0x1D)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C074).toString(16))
print("ETMACVR15(id:0x1E)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C078).toString(16))
print("ETMACVR16(id:0x1F)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C07C).toString(16))
print("ETMACTR1(id:0x20)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C080).toString(16))
print("ETMACTR2(id:0x21)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C084).toString(16))
print("ETMACTR3(id:0x22)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C088).toString(16))
print("ETMACTR4(id:0x23)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C08C).toString(16))
print("ETMACTR5(id:0x24)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C090).toString(16))
print("ETMACTR6(id:0x25)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C094).toString(16))
print("ETMACTR7(id:0x26)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C098).toString(16))
print("ETMACTR8(id:0x27)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C09C).toString(16))
print("ETMACTR9(id:0x28)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0A0).toString(16))
print("ETMACTR10(id:0x29)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0A4).toString(16))
print("ETMACTR11(id:0x2A)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0A8).toString(16))
print("ETMACTR12(id:0x2B)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0AC).toString(16))
print("ETMACTR13(id:0x2C)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0B0).toString(16))
print("ETMACTR14(id:0x2D)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0B4).toString(16))
print("ETMACTR15(id:0x2E)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0B8).toString(16))
print("ETMACTR16(id:0x2F)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0BC).toString(16))
print("ETMDCVR0(id:0x30)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0C0).toString(16))
print("ETMDCVR1(id:0x31)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0C4).toString(16))
print("ETMDCVR2(id:0x32)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0C8).toString(16))
print("ETMDCVR3(id:0x33)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0CC).toString(16))
print("ETMDCVR4(id:0x34)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0D0).toString(16))
print("ETMDCVR5(id:0x35)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0D4).toString(16))
print("ETMDCVR6(id:0x36)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0D8).toString(16))
print("ETMDCVR7(id:0x37)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0DC).toString(16))
print("ETMDCVR8(id:0x38)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0E0).toString(16))
print("ETMDCVR9(id:0x39)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C0E4).toString(16))
print("ETMCNTRLDVR1(id:0x50)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C140).toString(16))
print("ETMCNTRLDVR2(id:0x51)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C144).toString(16))
print("ETMCNTRLDVR3(id:0x52)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C148).toString(16))
print("ETMCNTRLDVR4(id:0x53)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C14C).toString(16))
print("ETMCNTENR1(id:0x54)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C150).toString(16))
print("ETMCNTENR2(id:0x55)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C154).toString(16))
print("ETMCNTENR3(id:0x56)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C158).toString(16))
print("ETMCNTENR4(id:0x57)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C15C).toString(16))
print("ETMCNTVR1(id:0x5C)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C170).toString(16))
print("ETMCNTVR2(id:0x5D)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C174).toString(16))
print("ETMCNTVR3(id:0x5E)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C178).toString(16))
print("ETMCNTVR4(id:0x5F)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C17C).toString(16))
print("ETMSQ12EVR(id:0x60)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C180).toString(16))
print("ETMSQ31EVR(id:0x63)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C18C).toString(16))
print("ETMSQ32EVR(id:0x64)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C190).toString(16))
print("ETMSQ13EVR(id:0x65)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C194).toString(16))
print("ETMCIDCVR1(id:0x6C)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1B0).toString(16))
print("ETMCIDCVR2(id:0x6D)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1B4).toString(16))
print("ETMCIDCVR3(id:0x6E)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1B8).toString(16))
print("ETMIDR(id:0x79)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1E4).toString(16))
print("ETMCCER(id:0x7A)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1E8).toString(16))
print("ETMTESSEICR(id:0x7C)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1F0).toString(16))
print("ETMTSEVR(id:0x7E)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1F8).toString(16))
print("ETMAUXCR(id:0x7F)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C1FC).toString(16))
print("ETMTRACEIDR(id:0x80)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C200).toString(16))
print("ETMVMIDCVR(id:0x81)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C204).toString(16))
print("ETMIDR2(id:0x82)=0x"    + debugSessionDAP.memory.readWord(1, 0x9D41C208).toString(16))
```
Paste the outputs of this into the device_6.ini [regs] section.

## 🔄 General Workflow

1. **Run Benchmark Test & Capture Trace**
   - Use Code Composer Studio (CCS) and the scripting console to capture trace data into `tbr.data`:
     See last Section. You have to adjust the device6.ini file for your specific hardware.

   - Execute `dumptbr()` to dump the ETB trace buffer:
     ```js
     dumptbr()
     ```

2. **Copy Trace & Binaries**
   - Use `copy_over.bat` to:
     - Copy `.out`/`.elf` files from CCS `Debug` folders
     - Rename selected RTOS builds (e.g., `freertos.out`, `threadx.out`)
     - Copy the captured `tbr.data` to the working `files/` folder

     ⚠️ Adjust the following paths in `copy_over.bat` as needed:
     - `SOURCE` — your CCS workspace directory
     - `DEST` — the destination trace processing directory
   - You don't need this file, you can just copy over the files manually

3. **Disassemble Executables**
   - Disassemble binaries using the respective tool:
     - For TI toolchain: `tiarm_objdump.bat`
     - For Zephyr/GCC: `gccarm_objdump.sh` (run under WSL)

     Example:
     ```bash
     ./gccarm_objdump.sh files/zephyr.elf
     ```

4. **Parse Trace Data**
   - Run the `run_all.sh` script from WSL:
     ```bash
     ./run_all.sh freertos
     ```

   This script:
   - Renames `tbr.data` → `freertos.data`
   - Updates `cpu_0.ini` and `trace.ini` paths
   - Runs `/usr/bin/trc_pkt_lister`
   - Produces `.ppl` packet trace
   - Runs `parse_trace.py` and outputs `parsed_trace_freertos.txt`

   ⚠️ Adjust:
   - `run_all.sh`: Paths to binaries and trace files if your layout differs
   - Ensure `cpu_0.ini` and `trace.ini` exist and match your setup

5. **Post-Processing**
   - Use `execution_order.py` to extract simplified function entry/exit sequences from parsed traces.

---

## 🧩 Notes

    The workflow assumes:

        CCS is configured for CoreSight access on AM243x/R5F

        `trc_pkt_lister` is installed at `/usr/bin/trc_pkt_lister`

        Scripts are executed in the correct order from WSL or cmd

    All intermediate files are placed in the `files/` subfolder

## ⚙️ CCS Scripting Console Setup (AM243x R5F Only)

To capture trace data from the ETB on the AM243x R5F, run the following once per CCS session in the Scripting Console:
```bash
// Open DAP session
debugSessionDAP = ds.openSession("*", "CS_DAP_0");
debugSessionDAP.target.connect();

// Set ETM to programming mode
debugSessionDAP.memory.writeWord(1, 0x9d41c000,
    debugSessionDAP.memory.readWord(1, 0x9d41c000) | 0x400);

// Disable trace capture (ETB Control Register)
debugSessionDAP.memory.writeWord(1, 0x9c025020, 0x0);

// Reset write pointer
var wptr = debugSessionDAP.memory.readWord(1, 0x9c025018);
debugSessionDAP.memory.writeWord(1, 0x9c025014, wptr);

// Helper to convert 32-bit values to byte arrays
function longtoba(value) {
    var byteArray = [0, 0, 0, 0];
    for (var i = 0; i < 4; i++) {
        byteArray[i] = value & 0xff;
        value >>= 8;
    }
    return byteArray;
}

// Dump ETB contents to file
function dumptbr() {
    var fos = new java.io.FileOutputStream("E:\\tbr.data");
    var dos = new java.io.DataOutputStream(fos);

    for (var i = 0; i < 16384; i++) {
        var value = debugSessionDAP.memory.readData(1, 0x9c025010, 32, false);
        var index = debugSessionDAP.memory.readData(1, 0x9c025014, 32, false);

        var valba = longtoba(value);
        var idxba = longtoba(index);

        dos.write(valba[0]);
        dos.write(valba[1]);
        dos.write(valba[2]);
        dos.write(valba[3]);
    }

    dos.close();
    fos.close();
    delete dos;
    delete fos;
}
```
* ### Note that dumptbr() copies the trace data to ```E:\\tbr.data``` change this if needed.
After setup, dump the trace by running:
```bash
dumptbr()
```
### 📌 Note: This script is specific to the AM243x device and R5F core. If you are using another board or core (e.g., A53 or C66), the register addresses and procedure will differ and must be adapted accordingly. Refere to "Setting up OpenCSD"

## Licence
Copyright (c) Marco Milenkovic 2024 IBV - Echtzeit- und Embedded GmbH & Co. KG
SPDX-License-Identifier: Apache-2.0

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the 
rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software 
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all 
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR 
A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN 
AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION 
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.