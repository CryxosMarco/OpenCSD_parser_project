---
Copyright (c) Marco Milenkovic 2024 IBV - Echtzeit- und Embedded GmbH & Co. KG
SPDX-License-Identifier: Apache-2.0
---
# Trace Analysis Workflow (OpenCSD-based)

This folder contains scripts and tools for handling ARM CoreSight trace data (ETB/ETM) on the AM243x device (R5F core), using OpenCSD (`trc_pkt_lister`) for decoding and Python for post-processing.

---

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
After setup, dump the trace by running:
```bash
dumptbr()
```
### 📌 Note: This script is specific to the AM243x device and R5F core. If you are using another board or core (e.g., A53 or C66), the register addresses and procedure will differ and must be adapted accordingly.
