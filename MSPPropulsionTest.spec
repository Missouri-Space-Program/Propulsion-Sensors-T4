# -*- mode: python ; coding: utf-8 -*-
import os

from PyInstaller.utils.hooks import collect_submodules


hiddenimports = [
    "labjack.ljm",
    "labjack.ljm.constants",
    "labjack.ljm.errorcodes",
    "dearpygui.dearpygui",
]
hiddenimports += collect_submodules("dearpygui")

ljm_dll = os.environ.get("LABJACK_LJM_DLL")
binaries = [(ljm_dll, ".")] if ljm_dll and os.path.isfile(ljm_dll) else []


a = Analysis(
    ["MSPPropulsionTest.py"],
    pathex=[],
    binaries=binaries,
    datas=[("assets", "assets")],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MSPPropulsionTest",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)