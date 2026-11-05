# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['pynput.keyboard', 'pynput.mouse', 'pystray', 'PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageDraw', 'requests', 'pywinstyles', 'win_magnification']
hiddenimports += collect_submodules('pynput')


a = Analysis(
    ['20.py'],
    pathex=[],
    binaries=[],
    datas=[('favicon.ico', '.')],
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
    name='20护眼小助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['favicon.ico'],
)
