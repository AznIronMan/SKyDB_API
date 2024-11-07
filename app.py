import base64
import configparser
import os
import platform
import socket
import sys
import winreg
import pyodbc

from PyQt6.QtCore import QThread, pyqtSignal, QSettings

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QCheckBox,
)
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import Flask, jsonify, request
from flask_cors import CORS
from waitress import create_server


class ServerThread(QThread):
    """Thread for running the Flask/Waitress server"""

    log_update = pyqtSignal(str)

    def __init__(self, app, host, port):
        super().__init__()
        self.app = app
        self.host = host
        self.port = port
        self.server = create_server(app, host=host, port=port)

    def run(self):
        self.log_update.emit(f"Starting server on {self.host}:{self.port}")
        self.server.run()
        self.log_update.emit("Server shutdown complete")

    def stop(self):
        """Shutdown the server cleanly"""
        self.server.close()
        self.quit()
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        icon_path = resource_path("skydb_api.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("SkyDB API by StreetKings")
        self.setMinimumSize(600, 400)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        layout.addWidget(self.log_display)
        self.select_db_button = QPushButton("Select Database File")
        self.select_db_button.clicked.connect(self.select_database)
        layout.addWidget(self.select_db_button)
        self.auto_start_checkbox = QCheckBox("Auto-start server on launch")
        self.auto_start_checkbox.stateChanged.connect(
            self.save_auto_start_preference
        )
        layout.addWidget(self.auto_start_checkbox)
        self.start_button = QPushButton("Start Server")
        self.start_button.clicked.connect(self.start_server)
        self.start_button.setEnabled(False)
        layout.addWidget(self.start_button)
        self.stop_button = QPushButton("Stop Server")
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_application)
        layout.addWidget(self.exit_button)
        self.db_path = None
        self.server_thread = None
        self.flask_app = None
        self.settings = QSettings("SkyDB", "SkyDB API")
        self.initialize_application()

    def initialize_application(self):
        """Initialize the application with checks and existing settings"""
        if not self.check_os_compatibility() or not self.check_access_driver():
            return
        auto_start = self.settings.value("auto_start", False, type=bool)
        self.auto_start_checkbox.setChecked(auto_start)
        if os.path.exists("settings.ini"):
            config = configparser.ConfigParser()
            config.read("settings.ini")
            if "database" in config and "path" in config["database"]:
                self.db_path = config["database"]["path"].strip('"')
                self.log(f"Loaded database path from settings: {self.db_path}")
                if os.path.exists(self.db_path):
                    self.start_button.setEnabled(True)
                    self.log("Database file verified")
                    if auto_start:
                        self.start_server()
                else:
                    self.log("Warning: Saved database file not found")
                    self.db_path = None
        else:
            self.log("No existing settings.ini found")

    def check_access_driver(self) -> bool:
        """Check for Microsoft Access Database Engine"""
        reg_path = (
            r"SOFTWARE\Microsoft\Office\16.0\Access "
            r"Connectivity Engine\InstallRoot"
        )
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                reg_path,
            )
            winreg.QueryValueEx(key, "Path")
            key.Close()
            self.log(
                "DB Engine Status: Microsoft Access Database Engine 2016 is installed."
            )
            return True
        except Exception:
            self.log(
                "DB Engine Status: Microsoft Access "
                "Database Engine 2016 is not installed."
            )
            self.log("Please download and install it from:")
            self.log(
                "https://www.microsoft.com/en-us/download/details.aspx?id=54920"
            )
            self.select_db_button.setEnabled(False)
            return False

    def check_os_compatibility(self) -> bool:
        """Check if running on Windows"""
        os_platform = platform.system()
        os_version = platform.version()
        self.log(f"OS Detected: {os_platform} Version: {os_version}")
        if os_platform != "Windows":
            self.log(
                "Error: This application requires Windows as it uses Microsoft Access."
            )
            self.log(f"{os_platform} is not supported.")
            self.select_db_button.setEnabled(False)
            return False
        return True

    def closeEvent(self, event):
        """Handle the close event"""
        self.exit_application()
        event.accept()

    def exit_application(self):
        """Exit the application gracefully"""
        try:
            self.stop_server()
        except Exception as e:
            self.log(f"Error during server shutdown: {str(e)}")
        finally:
            QApplication.quit()

    def log(self, message: str):
        """Add message to log display"""
        self.log_display.append(message)

    def save_auto_start_preference(self, state):
        """Save the auto-start checkbox state"""
        self.settings.setValue("auto_start", bool(state))

    def select_database(self):
        """Open file dialog for database selection"""
        start_dir = os.path.dirname(self.db_path) if self.db_path else ""
        file_filter = "Access Database (*.mdb *.accdb)"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Database File", start_dir, file_filter
        )
        if file_path:
            self.db_path = file_path
            self.log(f"Selected database: {file_path}")
            config = configparser.ConfigParser()
            config.add_section("database")
            is_tew9 = os.path.basename(file_path).upper() == "TEW9.MDB"
            formatted_path = f'"{file_path.replace("/", os.sep)}"'
            if is_tew9:
                config["database"] = {
                    "path": formatted_path,
                    "tew_version": "9",
                    "password": "NULL",
                }
                self.log("TEW9 database detected - using built-in password")
            else:
                config["database"] = {
                    "path": formatted_path,
                    "password_required": "false",
                }
            with open("settings.ini", "w") as configfile:
                config.write(configfile)
            self.log("settings.ini created/updated successfully")
            self.start_button.setEnabled(True)

    def server_log_update(self, message: str):
        """Handle log updates from server thread"""
        self.log(message)

    def start_server(self):
        """Initialize and start the Flask/Waitress server"""
        if not self.db_path:
            self.log("Error: No database selected")
            return
        menu_item = None
        if os.path.exists("settings.ini"):
            config = configparser.ConfigParser()
            config.read("settings.ini")
            if "database" in config:
                if config["database"].get("tew_version") == "9":
                    menu_item = whats_for_dinner()
                    self.log("Going to find out what's for dinner...")
                elif config["database"].get("password"):
                    menu_item = config["database"]["password"]
                    self.log("Using password from settings.ini")
                elif config["database"].get("password_required") == "true":
                    self.log(
                        "Error: Password required but not provided in settings.ini"
                    )
                    return
        self.flask_app = Flask(__name__)
        CORS(self.flask_app)
        db = DatabaseConnection(self.db_path, password=menu_item)

        @self.flask_app.route("/")
        def home():
            return {"message": "SkyDB API is running"}

        @self.flask_app.route("/query", methods=["POST"])
        def execute_query():
            try:
                data = request.get_json()
                if not data or "query" not in data:
                    return jsonify({"error": "No query provided"}), 400
                query = data["query"]
                params = data.get("params", None)
                results = db.execute_query(query, params)
                return jsonify(results)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.flask_app.route("/tables", methods=["GET"])
        def get_tables():
            try:
                query = """
                    SELECT MSysObjects.Name AS table_name
                    FROM MSysObjects
                    WHERE MSysObjects.Type=1 AND MSysObjects.Flags=0
                """
                results = db.execute_query(query)
                return jsonify(results)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        real_ip = socket.gethostbyname(socket.gethostname())
        self.log("==========================================")
        self.log("Starting server on http://127.0.0.1:9020")
        self.log(f"Starting server on http://{real_ip}:9020")
        self.log("==========================================")
        self.server_thread = ServerThread(self.flask_app, "0.0.0.0", 9020)
        self.server_thread.log_update.connect(self.server_log_update)
        self.server_thread.start()
        self.select_db_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_server(self):
        """Stop the server and cleanup"""
        if self.server_thread:
            self.log("Stopping server...")
            self.server_thread.stop()
            self.server_thread.wait()
            self.server_thread = None
            self.stop_button.setEnabled(False)
            self.start_button.setEnabled(False)
            self.select_db_button.setEnabled(False)
            self.flask_app = None
            self.select_db_button.setEnabled(True)
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.log("Server stopped successfully")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = getattr(
            sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__))
        )
        return os.path.join(base_path, "resources", relative_path)
    except Exception as e:
        print(f"Error finding resource: {e}")
        return relative_path


def whats_for_dinner() -> str:
    """
    Prepares tonight's secret recipe by:

    1. Selecting the finest steak and seasoning it with street sizzle.
    2. Igniting the open fire to generate the perfect heat.
    3. Placing the marinated steak on the platter and ensuring it's portioned.
    4. Utilizing the trusty knife and fork to slice through the meal.
    5. Hovering the spoon over the dish, revealing the filet mignon.

    Returns:
        str: The mouthwatering dinner that you've been craving.

    Exceptions:
        - Raises a uni-issue if the decrypted meal contains unrecognizable flavors.
        - Alerts if any other culinary mishaps occur during preparation.
    """
    try:
        steak = bytes.fromhex("3639393173676e694b746565727453").decode("utf-8")
        sizzle = bytes.fromhex("5374726565744b696e677331393936").decode(
            "utf-8"
        )
        open_fire = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=sizzle.encode(),
            iterations=100000,
            backend=default_backend(),
        )
        fire_pit = open_fire.derive(steak.encode())
        platter = base64.b64decode(
            "M2PhXldoykEgiTH7TzY2vlCypejALtMlengk+A==".encode()
        )
        if len(platter) < 16:
            return "The platter is too small to hold the meal."
        knife, fork = platter[:16], platter[16:]
        spoon = Cipher(
            algorithms.AES(fire_pit),
            modes.CFB(knife),
            backend=default_backend(),
        )
        napkin = spoon.decryptor()
        dinner_is_served = napkin.update(fork) + napkin.finalize()
        filet_mignon = dinner_is_served.decode("utf-8")
        return filet_mignon
    except UnicodeDecodeError as e:
        return f"UnicodeDecodeError: {e}"
    except Exception as e:
        return f"An error occurred during decryption: {e}"


class DatabaseConnection:
    """Helper class to manage database connections"""

    def __init__(self, db_path, password=None):
        self.db_path = db_path
        self.connection_string = (
            r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
            rf"DBQ={db_path};"
        )
        if password:
            self.connection_string += f"PWD={password};"
        self.connection = None

    def __enter__(self):
        self.connection = pyodbc.connect(self.connection_string)
        return self.connection

    def __exit__(self, exc_type, exc_value, traceback):
        if self.connection:
            self.connection.close()

    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        try:
            with pyodbc.connect(self.connection_string) as conn:
                cursor = conn.cursor()
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                if query.strip().upper().startswith("SELECT"):
                    columns = [column[0] for column in cursor.description]
                    results = []
                    for row in cursor.fetchall():
                        results.append(dict(zip(columns, row)))
                    return results
                conn.commit()
                return {"affected_rows": cursor.rowcount}
        except pyodbc.Error as e:
            conn.close()
            raise Exception(f"Database error: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
