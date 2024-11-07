from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
)

hiddenimports = collect_submodules("flask")
datas = collect_data_files("flask")
binaries = []
hiddenimports += [
    "flask.json",
    "flask.json.tag",
    "flask.helpers",
    "flask.sessions",
    "flask.templating",
    "flask.wrappers",
    "flask.views",
    "flask.signals",
    "flask_cors",
]
