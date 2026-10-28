# DiskSanitizer - Automated Empty File Cleanup using Python & schedule

This project demonstrates an **automated file system cleanup utility** that scans a directory recursively, records every file size in a timestamped audit log, and **deletes zero-byte (empty) files** on a configurable schedule.

It follows **industrial best practices** by:

- Automating periodic cleanups with the **schedule** library
- Providing a **dry-run mode** to preview deletions before anything is removed
- Never following or deleting **symbolic links**
- Protecting its own log files and refusing to run on a **filesystem root**
- Handling locked or protected files with **exception handling**, so one failure never stops a run
- Writing audit reports **atomically** (temp file, then rename), so a log is never half-written
- Using Python's **logging** module and a standard **argparse CLI** with input validation and exit codes
- Shutting down cleanly on **Ctrl + C** and **SIGTERM**

---

## Dependencies

Requires **Python 3.8+**. Install the required Python package before running the project:

```bash
pip install -r requirements.txt
```

or directly:

```bash
pip install schedule
```

`os`, `sys`, `stat`, `logging`, `argparse`, `signal`, `threading`, `pathlib`, `datetime` and `dataclasses` are part of the Python standard library and need no installation.

---

## File Information

**Source:** Any local directory given on the command line

**Cleanup Rule:**

- Regular files of **0 bytes** are deleted
- All other files are only measured and logged

**Never Touched:**

1. Symbolic links (skipped and logged)
2. Other non-regular files (sockets, devices)
3. The tool's own log folder and report files
4. Directories (empty folders are kept)

**Output:**

- One audit report per run: `DiskSanitizer_Log_YYYY-MM-DD_HH-MM-SS.log`

---

## Workflow

### Argument Parsing

- Parse arguments with `argparse`
- `directory`: folder to scan and clean
- Optional: `--interval` (minutes, default 1), `--log-folder` (default `DiskSanitizerLogs`), `--dry-run`, `--once`, `--verbose`, `--version`

### Path Validation

- Exit with an error if the directory does not exist or is not a directory
- Refuse to run on a filesystem root (for example `/` or `C:\`)

### Recursive Scanning

- Walk the whole tree using `os.walk` (symbolic links are not followed)
- Read each file's size with `lstat`
- Skip the log folder and non-regular files

### Cleanup

- **Step 1:** Write the file path and size to the report
- **Step 2:** If the size is 0 bytes, delete it (or only report it in dry-run mode)
- **Step 3:** If deletion fails (locked or protected file), record the error and continue

### Report Writing

- Write the header, per-file lines and a summary of counters (scanned, found, deleted, skipped, errors)
- Save to a temporary file, then rename it to the final name
- A report is never overwritten (a counter is added if the name already exists)

### Scheduling

- Run **one cleanup immediately**, then repeat using `schedule.every(interval).minutes`
- A failed run is logged with its traceback and does **not** stop the scheduler
- Press **Ctrl + C** (or send SIGTERM) to stop cleanly, with no stack trace

---

## Running the Project

### Show Help

```bash
python DiskSanitizer.py --help
```

### Preview First (Recommended)

```bash
python DiskSanitizer.py /home/user/project_builds --dry-run --once
```

Nothing is deleted. The report lists the files that would be removed.

### Start Cleanup Service

```bash
python DiskSanitizer.py /home/user/project_builds --interval 5
```

Expected output:

```text
2026-10-28 11:20:00 [INFO] Target directory: /home/user/project_builds
2026-10-28 11:20:00 [INFO] Mode: LIVE (empty files will be deleted)
2026-10-28 11:20:00 [INFO] Cleanup scheduled every 5 minute(s). Press Ctrl + C to stop.
2026-10-28 11:20:00 [INFO] Run complete: 5 scanned, 2 empty, 2 deleted, 0 errors. Report: /home/user/DiskSanitizerLogs/DiskSanitizer_Log_2026-10-28_11-20-00.log
```

### Run Once and Exit

```bash
python DiskSanitizer.py /home/user/project_builds --once
```

Useful for cron jobs and Windows Task Scheduler. Exit code is `0` on success and `1` on failure.

### Stop the Service

Press **Ctrl + C**:

```text
2026-10-28 11:27:41 [INFO] Received SIGINT. Shutting down...
2026-10-28 11:27:41 [INFO] DiskSanitizer stopped.
```

### Error Handling Examples

```text
$ python DiskSanitizer.py /does/not/exist
2026-10-28 11:20:00 [ERROR] Directory does not exist: /does/not/exist

$ python DiskSanitizer.py /
2026-10-28 11:20:00 [ERROR] Refusing to clean a filesystem root: /

$ python DiskSanitizer.py /home/user/project_builds --interval 0
DiskSanitizer.py: error: argument -i/--interval: value must be at least 1
```

---

## Visualizations

- Not applicable. The output is a structured text report that can be read directly or parsed by other tools.

---

## Log Storage

- Reports are saved in the folder given by `--log-folder` (default `DiskSanitizerLogs/`)
- Each run creates a new file, so earlier reports are never overwritten
- File name format: `DiskSanitizer_Log_YYYY-MM-DD_HH-MM-SS.log`

```text
DiskSanitizerLogs/
├── DiskSanitizer_Log_2026-10-28_11-20-00.log
├── DiskSanitizer_Log_2026-10-28_11-25-00.log
└── DiskSanitizer_Log_2026-10-28_11-30-00.log
```

---

## Sample Run

Before:

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

Audit report:

```text
--------------------------------------------------
         DiskSanitizer Directory & Storage Management
--------------------------------------------------
Target Directory : /home/user/project_builds
Mode             : LIVE (empty files are deleted)
Started At       : 2026-10-28 11:20:00
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
Total files scanned          : 5
Zero-byte files found        : 2
Zero-byte files deleted      : 2
Skipped (not regular files)  : 0
Errors                       : 0
--------------------------------------------------
Finished At : 2026-10-28 11:20:00 (0.01s)
--------------------------------------------------
```

After:

```text
/home/user/project_builds/
├── main.py (2048 bytes)
├── config.env (128 bytes)
├── temp/
│   └── active.log (512 bytes)
└── debug_logs/
```

> **Warning:** Deleted files are **not** moved to the recycle bin and cannot be recovered. Always run with `--dry-run` first on a new directory. A file that is empty at scan time may be a placeholder or lock file that another program expects to exist.

---

## Author

**Prathmesh Girme**
GitHub: [@Prathmesh-Girme](https://github.com/Prathmesh-Girme)
**Date:** 20/10/2026
