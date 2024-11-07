import os
import shutil
import subprocess
from datetime import datetime


APP_NAME = "SKyDB_API"


def check_for_pyinstaller() -> None:
    """Check if PyInstaller is installed"""
    if not shutil.which("pyinstaller"):
        print_log(
            "FAILURE", "PyInstaller not found. Please install PyInstaller."
        )
        exit(1)


def date_time_stamp() -> str:
    """Return the current date and time as a string"""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def print_log(type: str, message: str) -> None:
    """Print a log message with colored output"""
    color = {
        "ERROR": "\033[91m",
        "WARNING": "\033[93m",
        "INFO": "\033[96m",
        "SUCCESS": "\033[92m",
    }
    background = {
        "FAILURE": "\033[40;91m",
    }
    spacer = {
        "ERROR": "  ",
        "WARNING": "",
        "INFO": "   ",
        "SUCCESS": "",
        "FAILURE": "",
    }
    timestamp = date_time_stamp()
    if type in background:
        print(
            f"{spacer[type]}[{background[type]}{type}\033[0m]:{timestamp}: {message}"
        )
    else:
        print(
            f"{spacer[type]}[{color[type]}{type}\033[0m]:{timestamp}: {message}"
        )


def modify_exe_binary(exe_path: str) -> None:
    """Modify the exe to look for DLLs in 'resources' instead of '_internal'"""
    try:
        if not os.path.exists(exe_path):
            print_log("ERROR", f"File not found: {exe_path}")
            raise FileNotFoundError(f"File not found: {exe_path}")
        print_log("INFO", "Reading executable file...")
        with open(exe_path, "rb") as f:
            content = f.read()
        print_log("INFO", "Modifying binary content...")
        modified = content.replace(b"_internal", b"resources")
        print_log("INFO", "Writing modified content back to file...")
        with open(exe_path, "wb") as f:
            f.write(modified)
        print_log("SUCCESS", "Binary modification completed successfully")
    except Exception as e:
        print_log("ERROR", f"Failed to modify executable: {e}")
        raise


if __name__ == "__main__":
    try:
        print(
            f"========= STARTING build.py PROCESS @ {date_time_stamp()} ========="
        )
        print_log("INFO", "Checking for PyInstaller...")
        check_for_pyinstaller()
        print_log("SUCCESS", "PyInstaller found")
        print_log("INFO", "Starting PyInstaller build process...")
        subprocess.run(["pyinstaller", f"{APP_NAME}.spec"], check=True)
        print_log("SUCCESS", "PyInstaller build completed")
        dist_dir = os.path.join("dist", APP_NAME)
        exe_path = os.path.join(dist_dir, f"{APP_NAME}.exe")
        internal_path = os.path.join(dist_dir, "_internal")
        resources_path = os.path.join(dist_dir, "resources")
        print_log("INFO", "Modifying executable binary...")
        modify_exe_binary(exe_path)
        if os.path.exists(internal_path):
            if os.path.exists(resources_path):
                print_log("INFO", "Removing existing resources directory...")
                shutil.rmtree(resources_path)
            print_log("INFO", "Renaming _internal directory to resources...")
            os.rename(internal_path, resources_path)
            print_log("SUCCESS", "Successfully renamed _internal to resources")
        print_log("SUCCESS", "Build process completed successfully")
        print(
            f"======== COMPLETED build.py PROCESS @ {date_time_stamp()} ========="
        )
        print()
    except Exception as e:
        print_log("FAILURE", f"Build process failed: {e}")
        print(
            f"========== FAILED build.py PROCESS @ {date_time_stamp()} =========="
        )
        print()
        exit(1)
