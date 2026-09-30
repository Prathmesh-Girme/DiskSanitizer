##########################################################
#
#   Importing required libraries
#
##########################################################

import sys
import os
import time
import schedule

##########################################################
#
#   Function name :     directory_cleaner
#   Input :             Name of Directory
#   Description :       Scans directory, logs files, and deletes empty files periodically
#   Author :            Prathmesh Sunil Girme
#
##########################################################

def directory_cleaner(directory_path):
    border = "-" * 50

    timestamp = time.ctime()
    
    log_file_name = f"DiskSanitizer_Log_{timestamp}.log"
    log_file_name = log_file_name.replace(" ", "_").replace(":", "_")

    if not os.path.exists(directory_path):
        print(f"DiskSanitizer Error: Directory does not exist -> {directory_path}")
        return
    
    if not os.path.isdir(directory_path):
        print(f"DiskSanitizer Error: Path is not a directory -> {directory_path}")
        return
    
    print(f"[+] Creating log file: {log_file_name}")

    try:
        with open(log_file_name, "w") as fobj:
            fobj.write(border + "\n")
            fobj.write("         DiskSanitizer Directory & Storage Management Script\n")
            fobj.write(border + "\n\n")

            fobj.write("Scanned files and sizes:\n\n")
            fobj.write(border + "\n")

            total_files = 0
            empty_files = 0

            for folder_name, sub_folder, file_names in os.walk(directory_path):
                for fname in file_names:
                    total_files += 1
                    file_full_path = os.path.join(folder_name, fname)

                    try:
                        file_size = os.path.getsize(file_full_path)
                        fobj.write(f"{file_full_path} : {file_size} bytes\n")

                        if file_size == 0:
                            empty_files += 1
                            os.remove(file_full_path)
                            fobj.write(f"   [DELETED] Empty file removed: {file_full_path}\n")
                    except Exception as e:
                        fobj.write(f"   [ERROR] Could not process {file_full_path}: {e}\n")

            fobj.write(border + "\n")
            fobj.write(f"Total files scanned: {total_files}\n")
            fobj.write(f"Total zero-byte files deleted: {empty_files}\n")

            fobj.write(border + "\n")
            fobj.write(f"Execution timestamp: {timestamp}\n")
            fobj.write(border + "\n")

    except Exception as e:
        print(f"DiskSanitizer Error: Failed to write log file -> {e}")


##########################################################
#
#   Function name :     main
#   Input :             Command line arguments
#   Description :       Controls script execution and argument handling
#   Author :            Prathmesh Sunil Girme
#
##########################################################

def main():
    border = "-" * 50
   
    print(border)
    print("      DiskSanitizer - Automated File Cleanup Service")
    print(border)
    
    if len(sys.argv) == 2:
        arg = sys.argv[1].lower()
        
        if arg in ["--h", "-h"]:
            print("Help: This script scans a directory recursively, logs file sizes, and deletes zero-byte empty files.")
            print("Use option '--u' for usage instructions.")
        
        elif arg in ["--u", "-u"]:
            print("Usage Guide:")
            print("  python DiskSanitizer.py <Absolute_Directory_Path>")
            print("Example:")
            print("  python DiskSanitizer.py C:\\Users\\Public\\Downloads")
        
        else:
            target_directory = sys.argv[1]
            print(f"[+] Starting periodic cleanup job for: {target_directory}")
            print("[+] Job scheduled every 1 minute. Press Ctrl+C to stop.\n")

            # Run once immediately, then schedule
            directory_cleaner(target_directory)
            schedule.every(1).minute.do(directory_cleaner, target_directory)
            
            try:
                while True:
                    schedule.run_pending()
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n[!] Execution stopped by user.")
                
    else:
        print("Invalid arguments provided.")
        print("Run 'python DiskSanitizer.py --h' for Help or '--u' for Usage guidance.")

    print(border)
    print(" Thank you for using DiskSanitizer Automation Service ")
    print(border)


if __name__ == "__main__":
    main()