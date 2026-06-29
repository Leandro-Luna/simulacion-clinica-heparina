"""Launcher para empaquetar la app Streamlit como ejecutable con PyInstaller.

Este script arranca Streamlit programáticamente. En modo desarrollo usa
subprocess del CLI; en modo empaquetado (frozen) usa bootstrap.run con
flag_options para forzar el puerto y abre el navegador manualmente.

Uso directo:

    uv run python -m simulacion_clinica.ui.launcher

Uso con PyInstaller (generar .exe en Windows):

    pyinstaller simulacion-clinica.spec --clean --noconfirm
"""

from __future__ import annotations

import subprocess
import sys
import threading
import webbrowser
from pathlib import Path

PORT = 8501


def _resolver_app_path() -> str:
    """Resuelve la ruta a app.py relativa a este launcher."""
    aqui = Path(__file__).parent
    app_path = aqui / "app.py"
    if app_path.exists():
        return str(app_path)

    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        app_path = base / "simulacion_clinica" / "ui" / "app.py"
        if app_path.exists():
            return str(app_path)

    raise FileNotFoundError("No se encontró app.py")


def _abrir_navegador() -> None:
    """Abre el navegador en el puerto correcto después de un delay."""
    import time

    time.sleep(3)
    webbrowser.open(f"http://localhost:{PORT}")


def _run_subprocess(app_path: str) -> None:
    """Modo desarrollo: usa subprocess con el CLI de Streamlit."""
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--server.port",
        str(PORT),
        "--server.headless",
        "false",
        "--browser.gatherUsageStats",
        "false",
        "--global.developmentMode",
        "false",
    ]
    try:
        subprocess.run(cmd, check=True)  # noqa: S603
    except KeyboardInterrupt:
        sys.exit(0)


def _run_frozen(app_path: str) -> None:
    """Modo empaquetado (PyInstaller): usa bootstrap.run con flag_options."""
    # Abrir navegador en el puerto correcto (Streamlit puede mostrar otro)
    threading.Thread(target=_abrir_navegador, daemon=True).start()

    from streamlit.web import bootstrap

    bootstrap.run(
        main_script_path=app_path,
        is_hello=False,
        args=[],
        flag_options={
            "server.port": PORT,
            "server.headless": False,
            "browser.gatherUsageStats": False,
            "global.developmentMode": False,
        },
    )


def main() -> None:
    app_path = _resolver_app_path()

    if getattr(sys, "frozen", False):
        _run_frozen(app_path)
    else:
        _run_subprocess(app_path)


if __name__ == "__main__":
    main()