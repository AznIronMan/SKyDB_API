# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect all necessary packages
flask_bins, flask_datas, flask_hiddenimports = collect_all('flask')
werkzeug_bins, werkzeug_datas, werkzeug_hiddenimports = collect_all('werkzeug')
waitress_bins, waitress_datas, waitress_hiddenimports = collect_all('waitress')
flask_cors_bins, flask_cors_datas, flask_cors_hiddenimports = collect_all('flask_cors')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=flask_bins + werkzeug_bins + waitress_bins + flask_cors_bins,
    datas=[
        ('skydb_api.ico', 'resources')
    ] + flask_datas + werkzeug_datas + waitress_datas + flask_cors_datas,
    hiddenimports=['werkzeug._internal', 'werkzeug.serving'] +
                   flask_hiddenimports +
                   werkzeug_hiddenimports +
                   waitress_hiddenimports +
                   flask_cors_hiddenimports,
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SkyDB_API',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='skydb_api.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SkyDB_API',
)
