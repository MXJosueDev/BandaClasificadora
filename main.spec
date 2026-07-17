# -*- mode: python ; coding: utf-8 -*-

import os

added_files = [
    (os.path.join('src'), 'src'),
    (os.path.join('model', 'model.tflite'), 'model'),
    (os.path.join('model', 'labels.txt'), 'model'),
]

hiddenimports = ['ai_edge_litert', 'ai_edge_litert.interpreter', 'serial', 'serial.tools', 'serial.tools.list_ports']

a = Analysis(
    [os.path.join('scripts', 'main.py')],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
