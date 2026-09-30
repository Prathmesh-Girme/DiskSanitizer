# DiskSanitizer - Automated File Cleanup & Storage Optimization Utility

**DiskSanitizer** is a Python-based system automation tool built to clean up directories, remove zero-byte (empty) files, and log file metrics with precise timestamps.

---

## Motivation & Thought Process

In modern operating systems and developer environments, temporary processes, aborted applications, and background routines frequently leave behind empty zero-byte files. Over time, these unneeded files can clutter workspace searches, fragment folder structures, and complicate system navigation.

`DiskSanitizer` was created as an automated background utility to replace manual housekeeping. The goal was to build a script that:
- Runs quietly in the background on a customizable schedule.
- Performs recursive scans across deeply nested folder structures.
- Generates clear, timestamped audit logs for administrative verification.
- Solves pathing and privilege challenges safely without interrupting other system tasks.

---

## Architecture & System Flow

```
+------------------+     +------------------------+     +--------------------------+
|  User Command /  | --> | Path & CLI Argument    | --> | Create Timestamped       |
|  Scheduled Job   |     | Validation             |     | Audit Log File           |
+------------------+     +------------------------+     +--------------------------+
                                                                     |
                                                                     v
+------------------+     +------------------------+     +--------------------------+
| Close Log File   | <-- | Delete Zero-Byte Files | <-- | Traverse Directory Tree  |
| & Wait for Loop  |     | & Write Stats to Log   |     | (`os.walk`)              |
+------------------+     +------------------------+     +--------------------------+
```

1. **Immediate Initial Pass:** Runs one cleanup cycle immediately upon initiation so the user doesn't have to wait for the first scheduled timer tick.
2. **Path Guarding:** Verifies the existence (`os.path.exists`) and type (`os.path.isdir`) of the user-provided target directory before attempting file operations.
3. **Recursive Inspection:** Uses `os.walk` to traverse all subdirectories and inspect individual file sizes using `os.path.getsize`.
4. **Targeted Purging:** Identifies zero-byte files and safely removes them with `os.remove`.
5. **Detailed Logging:** Captures all metrics and outcomes in dynamically named log files (`DiskSanitizer_Log_<timestamp>.log`).

---

## Technical Challenges & Solutions

### 1. OS-Safe Timestamped Filenames
* **Challenge:** Raw date strings returned by `time.ctime()` contain spaces and colons (`:`) which are illegal filename characters on Windows systems.
* **Solution:** Applied string sanitation rules to replace spaces and colons with underscores (`.replace(" ", "_").replace(":", "_")`), guaranteeing safe log creation across Windows, macOS, and Linux.

### 2. File Lockouts & Permission Errors
* **Challenge:** System files or files locked by active background processes caused unhandled `PermissionError` or `FileNotFoundError` exceptions during scans.
* **Solution:** Encapsulated individual file removal logic within `try-except` blocks. If an individual file fails to open or delete, the error is written to the audit log while the main scan continues smoothly.

### 3. Graceful Termination of Continuous Loops
* **Challenge:** Stopping the continuous background scheduling loop (`while True`) with `Ctrl + C` generated ugly stack traces in standard terminals.
* **Solution:** Wrapped the schedule execution loop inside a `KeyboardInterrupt` exception block, ensuring a clean exit prompt when canceled by the user.

---

## Features

- **Recursive Subdirectory Scanning:** Traverses entire directory structures recursively using native OS methods.
- **Zero-Byte File Purging:** Safely frees up file system records by removing empty files.
- **Timestamped Execution Audits:** Writes structured execution statistics into custom log files.
- **Background Task Scheduling:** Built-in cron-style background runner powered by Python's `schedule` library.
- **CLI Options:** Features user-friendly flags (`--h` for Help, `--u` for Usage).

---

## Directory Structure

```
DiskSanitizer/
├── DiskSanitizer.py      # Main automation script
├── requirements.txt      # Project dependencies
├── README.md             # Documentation
├── LICENSE               # Open-source license (MIT)
└── .gitignore            # Git ignore configuration
```

---

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/DiskSanitizer.git
   cd DiskSanitizer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage Examples

### 1. View Help Flags

```bash
python DiskSanitizer.py --h
```

**Output:**
```text
--------------------------------------------------
      DiskSanitizer - Automated File Cleanup Service
--------------------------------------------------
Help: This script scans a directory recursively, logs file sizes, and deletes zero-byte empty files.
Use option '--u' for usage instructions.
--------------------------------------------------
 Thank you for using DiskSanitizer Automation Service 
--------------------------------------------------
```

### 2. View Usage Guide

```bash
python DiskSanitizer.py --u
```

**Output:**
```text
--------------------------------------------------
      DiskSanitizer - Automated File Cleanup Service
--------------------------------------------------
Usage Guide:
  python DiskSanitizer.py <Absolute_Directory_Path>
Example:
  python DiskSanitizer.py C:\Users\Public\Downloads
--------------------------------------------------
 Thank you for using DiskSanitizer Automation Service 
--------------------------------------------------
```

### 3. Real-World Execution Walkthrough

#### **Before Execution (Directory Structure):**
```text
/home/user/project_builds/
├── main.py (2048 bytes)
├── config.env (128 bytes)
├── temp/
│   ├── build_cache.tmp (0 bytes)
│   └── active.log (512 bytes)
└── debug_logs/
    └── crash_dump.log (0 bytes)
```

#### **Run Command:**
```bash
python DiskSanitizer.py /home/user/project_builds
```

#### **Terminal Output:**
```text
--------------------------------------------------
      DiskSanitizer - Automated File Cleanup Service
--------------------------------------------------
[+] Starting periodic cleanup job for: /home/user/project_builds
[+] Job scheduled every 1 minute. Press Ctrl+C to stop.

[+] Creating log file: DiskSanitizer_Log_Wed_Sep_30_10_30_00_2026.log
```

#### **Generated Audit Log Content (`DiskSanitizer_Log_Wed_Sep_30_10_30_00_2026.log`):**
```text
--------------------------------------------------
         DiskSanitizer Directory & Storage Management Script
--------------------------------------------------

Scanned files and sizes:

--------------------------------------------------
/home/user/project_builds/main.py : 2048 bytes
/home/user/project_builds/config.env : 128 bytes
/home/user/project_builds/temp/build_cache.tmp : 0 bytes
   [DELETED] Empty file removed: /home/user/project_builds/temp/build_cache.tmp
/home/user/project_builds/temp/active.log : 512 bytes
/home/user/project_builds/debug_logs/crash_dump.log : 0 bytes
   [DELETED] Empty file removed: /home/user/project_builds/debug_logs/crash_dump.log
--------------------------------------------------
Total files scanned: 5
Total zero-byte files deleted: 2
--------------------------------------------------
Execution timestamp: Wed Sep 30 10:30:00 2026
--------------------------------------------------
```

#### **After Execution (Directory Structure):**
```text
/home/user/project_builds/
├── main.py (2048 bytes)
├── config.env (128 bytes)
├── temp/
│   └── active.log (512 bytes)
└── debug_logs/
```

---

## Author

**Prathmesh Girme**
* GitHub: [@your-username](https://github.com/<your-username>)

## License

This project is licensed under the [MIT License](LICENSE).