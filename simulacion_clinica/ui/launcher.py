"""Launcher para empaquetar la app Streamlit como ejecutable con PyInstaller.

Este script arranca Streamlit programáticamente sin depender del CLI
`streamlit run`, lo que permite empaquetarlo con PyInstaller en un .exe.

Uso directo:

    uv run python -m simulacion_clinica.ui.launcher

Uso con PyInstaller (generar .exe en Windows):

    pyinstaller simulacion-clinica.spec --clean --noconfirm
"""

from __future__ import annotations

import sys
from pathlib import Path


def _resolver_app_path() -> str:
    """Resuelve la ruta a app.py relativa a este launcher."""
    aqui = Path(__file__).parent
    app_path = aqui / "app.py"
    if app_path.exists():
        return str(app_path)

    # Fallback: buscar en el mismo directorio del ejecutable (PyInstaller)
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        app_path = base / "simulacion_clinica" / "ui" / "app.py"
        if app_path.exists():
            return str(app_path)

    raise FileNotFoundError("No se encontró app.py")


def main() -> None:
    from streamlit.web import bootstrap

    app_path = _resolver_app_path()

    # Dejar que Streamlit maneje el puerto y la apertura del navegador.
    # No hardcodear el puerto porque puede haber config del usuario que
    # override el default (8501).
    bootstrap.run(
        main_script_path=app_path,
        is_hello=False,
        args=[],
        flag_options={
            "browser.gatherUsageStats": False,
        },
    )


if __name__ == "__main__":
    main()