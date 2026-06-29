# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para empaquetar la app Streamlit como ejecutable.

Generar el .exe en Windows:

    pyinstaller simulacion-clinica.spec --clean --noconfirm

El ejecutable se genera en dist/simulacion-clinica.exe
"""

import os

block_cipher = None

a = Analysis(
    ["simulacion_clinica/ui/launcher.py"],
    pathex=[],
    binaries=[],
    datas=[
        # Código fuente de la app (necesario porque Streamlit lo lee en runtime)
        ("simulacion_clinica/ui/app.py", "simulacion_clinica/ui"),
        ("simulacion_clinica/ui/config_state.py", "simulacion_clinica/ui"),
        ("simulacion_clinica/ui/utils.py", "simulacion_clinica/ui"),
        ("simulacion_clinica/ui/views", "simulacion_clinica/ui/views"),
        ("simulacion_clinica/ui/components", "simulacion_clinica/ui/components"),
        # Backend de simulación
        ("simulacion_clinica/config.py", "simulacion_clinica"),
        ("simulacion_clinica/generadores.py", "simulacion_clinica"),
        ("simulacion_clinica/simulacion.py", "simulacion_clinica"),
        ("simulacion_clinica/optimizacion.py", "simulacion_clinica"),
        ("simulacion_clinica/__init__.py", "simulacion_clinica"),
    ],
    hiddenimports=[
        "streamlit",
        "plotly",
        "pandas",
        "scipy",
        "openpyxl",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

# Collect-all para streamlit y plotly (assets estáticos)
from PyInstaller.utils.hooks import collect_all

streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all("streamlit")
plotly_datas, plotly_binaries, plotly_hiddenimports = collect_all("plotly")

a.datas += streamlit_datas + plotly_datas
a.binaries += streamlit_binaries + plotly_binaries
a.hiddenimports += streamlit_hiddenimports + plotly_hiddenimports

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="simulacion-clinica",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    icon=None,
)