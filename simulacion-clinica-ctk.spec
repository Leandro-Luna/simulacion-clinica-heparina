# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para empaquetar la app CustomTkinter como ejecutable.

Generar el .exe en Windows:

    pyinstaller simulacion-clinica-ctk.spec --clean --noconfirm

El ejecutable se genera en dist/Simulacion-Clinica-CTk.exe
"""

from PyInstaller.utils.hooks import collect_all, collect_data_files

block_cipher = None

# Collect-all para customtkinter (assets: fonts, themes, icons)
ctk_datas, ctk_binaries, ctk_hiddenimports = collect_all("customtkinter")

# Collect data files de matplotlib (fonts, colormaps, etc.)
mpl_datas = collect_data_files("matplotlib")

a = Analysis(
    ["simulacion_clinica/ui_ctk/launcher.py"],
    pathex=[],
    binaries=ctk_binaries,
    datas=[
        ("simulacion_clinica/ui_ctk", "simulacion_clinica/ui_ctk"),
        ("simulacion_clinica/config.py", "simulacion_clinica"),
        ("simulacion_clinica/generadores.py", "simulacion_clinica"),
        ("simulacion_clinica/simulacion.py", "simulacion_clinica"),
        ("simulacion_clinica/optimizacion.py", "simulacion_clinica"),
        ("simulacion_clinica/__init__.py", "simulacion_clinica"),
    ]
    + ctk_datas
    + mpl_datas,
    hiddenimports=[
        "customtkinter",
        "matplotlib",
        "matplotlib.backends.backend_tkagg",
        "pandas",
        "scipy",
        "openpyxl",
    ]
    + ctk_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["streamlit", "plotly"],
    cipher=block_cipher,
    noarchive=False,
)


def _dedup(toc):
    """Deduplicate TOC entries by destination name, keeping first occurrence."""
    seen = set()
    result = []
    for dest, src, typ in toc:
        if dest not in seen:
            seen.add(dest)
            result.append((dest, src, typ))
    return result


a.datas = _dedup(a.datas)
a.binaries = _dedup(a.binaries)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="Simulacion-Clinica-CTk",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    windowed=True,
    icon=None,
)
