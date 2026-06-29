# -*- mode: python ; coding: utf-8 -*-
"""Spec de PyInstaller para empaquetar la app Streamlit como ejecutable.

Generar el .exe en Windows:

    pyinstaller simulacion-clinica.spec --clean --noconfirm

El ejecutable se genera en dist/simulacion-clinica.exe
"""

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Collect-all para streamlit y plotly (assets estáticos)
streamlit_datas, streamlit_binaries, streamlit_hiddenimports = collect_all("streamlit")
plotly_datas, plotly_binaries, plotly_hiddenimports = collect_all("plotly")

a = Analysis(
    ["simulacion_clinica/ui/launcher.py"],
    pathex=[],
    binaries=streamlit_binaries + plotly_binaries,
    datas=[
        ("simulacion_clinica/ui/app.py", "simulacion_clinica/ui"),
        ("simulacion_clinica/ui/config_state.py", "simulacion_clinica/ui"),
        ("simulacion_clinica/ui/utils.py", "simulacion_clinica/ui"),
        ("simulacion_clinica/ui/views", "simulacion_clinica/ui/views"),
        ("simulacion_clinica/ui/components", "simulacion_clinica/ui/components"),
        ("simulacion_clinica/config.py", "simulacion_clinica"),
        ("simulacion_clinica/generadores.py", "simulacion_clinica"),
        ("simulacion_clinica/simulacion.py", "simulacion_clinica"),
        ("simulacion_clinica/optimizacion.py", "simulacion_clinica"),
        ("simulacion_clinica/__init__.py", "simulacion_clinica"),
    ]
    + streamlit_datas
    + plotly_datas,
    hiddenimports=[
        "streamlit",
        "plotly",
        "pandas",
        "scipy",
        "openpyxl",
    ]
    + streamlit_hiddenimports
    + plotly_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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