# SKyDB_API

- **Version**: v1.0.0
- **Date**: 11.07.2024
- **Written by**: Geoff Clark of Clark & Burke, LLC

SKyDB_API is a powerful Python-based application designed to provide a robust API for managing SkyDB databases.
Leveraging Flask for backend operations, PyQt6 for the user interface, and Waitress as the production server,
SKyDB_API ensures seamless interaction with Microsoft Access databases. Additionally, it includes comprehensive
tools for building and packaging the application into user-friendly installers.

## Table of Contents

- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
- [Features](#features)
- [Usage](#usage)
- [Building the Installer](#building-the-installer)
- [Author Information](#author-information)
- [License](#license)

## Installation

### Prerequisites

Before installing SKyDB_API, ensure that your system meets the following requirements:

- **Operating System:** Windows (due to reliance on Microsoft Access)
- **Python:** Version 3.11.8 or higher
- **Microsoft Access Database Engine:** Version 2016
- **Dependencies:** Listed in `requirements.txt`
- **Additional Tools:**
  - **PyInstaller:** For building executables
  - **7-Zip:** For creating archives
  - **Resource Hacker:** For modifying executable resources

### Installation Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/AznIronMan/SKyDB_API.git
   cd SKyDB_API
   ```

2. **Set Up a Virtual Environment:**

   It's recommended to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install Required Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Microsoft Access Database Engine Installation:**

   Ensure that the Microsoft Access Database Engine 2016 is installed. If not, download and install it from [here](https://www.microsoft.com/en-us/download/details.aspx?id=54920).

## Features

- **RESTful API:** Built with Flask, providing endpoints to execute queries and retrieve database tables.
- **User Interface:** Developed with PyQt6, offering an intuitive GUI to manage server operations and settings.
- **Server Management:** Utilize Waitress for deploying the Flask application in a production environment.
- **Installer Creation:** Scripts to package the application into a standalone installer using PyInstaller and Resource Hacker.
- **Configuration Management:** Handles application settings and database configurations seamlessly.

## Usage

1. **Run the Application:**

   Launch the main application using the following command:

   ```bash
   python app.py
   ```

2. **Using the GUI:**

   - **Select Database File:** Click the "Select Database File" button to choose your Microsoft Access database (`*.mdb` or `*.accdb`).
   - **Auto-start Server:** Toggle the "Auto-start server on launch" checkbox to enable or disable automatic server startup.
   - **Start Server:** Click "Start Server" to initiate the API server.
   - **Stop Server:** Click "Stop Server" to shut down the API server.
   - **Exit:** Click "Exit" to close the application gracefully.

3. **API Endpoints:**

   - `GET /`: Verify if the SkyDB API is running.
   - `POST /query`: Execute custom SQL queries against the database.
   - `GET /tables`: Retrieve a list of tables present in the database.

## Building the Installer

Creating a standalone installer allows for easy distribution of SKyDB_API.

1. **Ensure All Dependencies Are Installed:**

   Make sure that all Python packages are installed within your virtual environment.

2. **Build the Executable:**

   Run the build script to generate the executable using PyInstaller.

   ```bash
   python build.py
   ```

   This script uses the `SkyDB_API.spec` file to configure the build process.

3. **Create the Installer:**

   Execute the installer creation script to package the executable into a user-friendly installer.

   ```bash
   python make_installer.py
   ```

   This process utilizes 7-Zip and Resource Hacker to bundle the application with necessary resources and a custom icon.

4. **Distribute the Installer:**

   The final installer (`SkyDB_API_Setup.exe`) will be located in the `./release/` directory.
   Share this installer to allow others to install SKyDB_API on their systems.

## Author Information

- **Author**: [Geoff Clark of Clark & Burke, LLC](https://www.cnb.llc)
- **Email**: [geoff@cnb.llc](mailto:geoff@cnb.llc)
- **Socials**:
  [GitHub @aznironman](https://github.com/aznironman)
  [IG: @cnbllc](https://instagram.com/cnbllc)
  [X: @clarkandburke](https://www.x.com/clarkandburke)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Attribution

If you use this software as a base for your own projects or fork it, we kindly request that
you give credit to Clark & Burke, LLC. While not required by the license, it is appreciated
and helps support the ongoing development of this project.

## Third-Party Notices

All rights reserved by their respective owners. Users must comply with the licenses and terms
of service of the software being installed.
