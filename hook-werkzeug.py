from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
)

hiddenimports = collect_submodules("werkzeug")
datas = collect_data_files("werkzeug")
binaries = []
hiddenimports += [
    "werkzeug._internal",
    "werkzeug.serving",
    "werkzeug.debug",
    "werkzeug.middleware",
    "werkzeug.local",
    "werkzeug.routing",
    "werkzeug.http",
    "werkzeug.urls",
    "werkzeug.utils",
    "werkzeug.wsgi",
]
