# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for Resume & Cover Letter Generator."""

import os
import importlib

block_cipher = None

# Locate customtkinter assets
ctk_path = os.path.dirname(importlib.import_module("customtkinter").__file__)

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (ctk_path, "customtkinter"),
        ("experience_data.json", "."),
    ],
    hiddenimports=[
        "lxml.etree",
        "lxml._elementpath",
        "httpx",
        "httpcore",
        "anyio",
        "anyio._backends",
        "anyio._backends._asyncio",
        "h11",
        "certifi",
        "docx.oxml.ns",
        "PIL",
    ],
    hookspath=[],
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
    name="ResumeGenerator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/icon.ico" if os.path.isfile("assets/icon.ico") else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ResumeGenerator",
)
