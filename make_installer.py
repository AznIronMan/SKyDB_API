import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


APP_NAME = "SKyDB_API"
SETUP_ICON = "skydb_api_installer.ico"
SEVEN_ZIP_PATH = Path("C:/Program Files/7-Zip")
SEVEN_ZIP_SFX = SEVEN_ZIP_PATH / "7z.sfx"
RESOURCE_HACKER_PATH = Path(
    "C:/Program Files (x86)/Resource Hacker/ResourceHacker.exe"
)
SETUP_EXE_NAME = f"{APP_NAME}_Setup.exe"
DEFAULT_INSTALL_PATH = f"%S\\{APP_NAME}"
TEMP_DIR = "./temp_installer"


def compile_resource_file() -> bool:
    """Compile the resource file for the icon"""
    try:
        print_log("INFO", f"Checking for installer icon: {SETUP_ICON}")
        if not os.path.exists(SETUP_ICON):
            print_log("WARNING", f"{SETUP_ICON} not found")
        print_log("INFO", "Creating resource file...")
        with open("installer.rc", "w", encoding="utf-8") as f:
            f.write(f'1 ICON "../{SETUP_ICON}"\n')
        print_log("INFO", "Checking for Resource Hacker...")
        if not RESOURCE_HACKER_PATH.exists():
            print_log(
                "WARNING", "Resource Hacker not found. Icon won't be applied."
            )
            return True
        print_log("INFO", "Applying icon to installer...")
        subprocess.run(
            [
                str(RESOURCE_HACKER_PATH),
                "-open",
                SETUP_EXE_NAME,
                "-save",
                SETUP_EXE_NAME,
                "-action",
                "addoverwrite",
                "-resource",
                SETUP_ICON,
                "-mask",
                "ICONGROUP,1,",
            ],
            check=True,
        )
        print()
        print()
        print_log("SUCCESS", "Icon applied successfully")
        return True
    except Exception as e:
        print_log("ERROR", f"Failed to compile resource file: {e}")
        raise e


def create_7z_archive(source_dir, output_file) -> bool:
    """Create a 7z archive from the source directory"""
    try:
        print_log("INFO", "Checking for 7-Zip installation...")
        try:
            subprocess.run(
                ["7z"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            print_log("SUCCESS", "7-Zip found in PATH")
        except FileNotFoundError:
            raise Exception(
                "7-Zip (7z) is not found in PATH. Please install 7-Zip first."
            )
        print_log("INFO", "Creating 7z archive from required files...")
        print()
        subprocess.run(
            ["7z", "a", output_file, f"{source_dir}/*"],
            check=True,
        )
        print()
        print()
        print_log("SUCCESS", f"Archive created successfully: {output_file}")
        return True
    except Exception as e:
        print_log("ERROR", f"Failed to create 7z archive: {e}")
        raise e


def create_installer(temp_dir: str = TEMP_DIR) -> bool:
    """Create the self-extracting installer"""
    try:
        print_log("INFO", f"Creating temporary directory: {temp_dir}")
        temp_dir_path = Path(temp_dir)
        temp_dir_path.mkdir(exist_ok=True, parents=True)
        print_log("INFO", "Checking distribution directory...")
        dist_dir = Path(f"./dist/{APP_NAME}")
        if not dist_dir.exists():
            print_log("ERROR", f"Distribution directory not found: {dist_dir}")
            raise Exception("Distribution directory not found")
        print_log("INFO", "Copying main executable...")
        shutil.copy2(
            str(dist_dir / f"{APP_NAME}.exe"),
            str(temp_dir_path / f"{APP_NAME}.exe"),
        )
        resources_dir = dist_dir / "resources"
        if resources_dir.exists():
            print_log("INFO", "Copying resource files...")
            shutil.copytree(
                str(resources_dir),
                str(temp_dir_path / "resources"),
                dirs_exist_ok=True,
            )
        print_log("INFO", "Changing to temporary directory...")
        os.chdir(str(temp_dir_path))
        create_7z_archive(".", "installer_files.7z")
        create_sfx_config()
        print_log("INFO", "Checking for 7-Zip SFX module...")
        if not SEVEN_ZIP_SFX.exists():
            print_log(
                "ERROR",
                (
                    f"7z.sfx not found at {SEVEN_ZIP_SFX}. "
                    "Please ensure 7-Zip is installed in the correct location"
                ),
            )
            raise Exception("7z.sfx not found")
        print_log("INFO", "Creating self-extracting installer...")
        with open(f"../{SETUP_EXE_NAME}", "wb") as outfile:
            with open(SEVEN_ZIP_SFX, "rb") as infile:
                outfile.write(infile.read())
            with open("config.txt", "rb") as infile:
                outfile.write(infile.read())
            with open("installer_files.7z", "rb") as infile:
                outfile.write(infile.read())
        os.chdir("..")
        compile_resource_file()
        print_log("INFO", "Cleaning up temporary files...")
        cleanup_files = ["config.txt", "installer_files.7z", "installer.rc"]
        for file in cleanup_files:
            try:
                os.remove(file)
            except OSError:  # type: ignore
                pass
        shutil.rmtree(temp_dir_path)
        final_destination = Path(f"./release/{SETUP_EXE_NAME}")
        final_destination.parent.mkdir(exist_ok=True, parents=True)
        print_log("INFO", f"Moving installer to {final_destination}")
        shutil.move(SETUP_EXE_NAME, final_destination)
        print_log("SUCCESS", "Installer creation completed")
        return True
    except Exception as e:
        print_log("ERROR", f"Failed to create installer: {e}")
        raise e


def create_sfx_config() -> bool:
    """Create the SFX configuration file"""
    try:
        print_log("INFO", "Generating SFX configuration file...")
        install_commands = (
            f"set /p install_dir=Enter installation directory "
            f"(default={DEFAULT_INSTALL_PATH}): && "
            'if "%%install_dir%"=="" '
            f"set install_dir={DEFAULT_INSTALL_PATH} && "
            'mkdir "%%install_dir%%" 2>nul && '
            'xcopy /E /I /Y * "%%install_dir%%" >nul 2>&1 && '
            "echo Installation complete. && "
            f'start "" "%%install_dir%%\\{APP_NAME}.exe" && '
            "exit"
        )
        config = f"""
    ;!@Install@!UTF-8!
    Title="{APP_NAME} Installer"
    BeginPrompt="Would you like to install {APP_NAME}?"
    MiscFlags="4"
    InstallPath="{DEFAULT_INSTALL_PATH}"
    RunProgram="cmd /c \\"{install_commands}\\""
    GUIFlags="2+8"
    GUIMode="1"
    ;!@InstallEnd@!
    """
        with open("config.txt", "w", encoding="utf-8") as f:
            f.write(config)
        print_log("SUCCESS", "SFX configuration file created successfully")
        return True
    except Exception as e:
        print_log("ERROR", f"Failed to create SFX config: {e}")
        raise e


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


if __name__ == "__main__":
    try:
        print(
            f"======= STARTING make_installer.py PROCESS @ {date_time_stamp()} ======="
        )
        print_log("INFO", f"Starting {APP_NAME} installer creation process...")
        create_installer()
        print_log(
            "SUCCESS", f"Installer created successfully: {SETUP_EXE_NAME}"
        )
        print(
            f"====== COMPLETED make_installer.py PROCESS @ {date_time_stamp()} ======="
        )
        print()
    except Exception as e:
        print_log("FAILURE", f"Error creating installer: {e}")
        print(
            f"====+=== FAILED make_installer.py PROCESS @ {date_time_stamp()} ========"
        )
        print()
        exit(1)
