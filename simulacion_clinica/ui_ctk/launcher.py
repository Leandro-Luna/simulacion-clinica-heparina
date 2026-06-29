"""Launcher para empaquetar la app CustomTkinter como ejecutable con PyInstaller.

Uso directo:

    uv run python -m simulacion_clinica.ui_ctk.launcher

Uso con PyInstaller (generar .exe en Windows):

    pyinstaller simulacion-clinica-ctk.spec --clean --noconfirm
"""

from __future__ import annotations

import sys

if __name__ == "__main__":
    from simulacion_clinica.ui_ctk.app import main

    main()
