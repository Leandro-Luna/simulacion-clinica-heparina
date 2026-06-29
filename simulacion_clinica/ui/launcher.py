"""Launcher para empaquetar la app Streamlit como ejecutable con PyInstaller.

Este script arranca Streamlit como un subprocess del CLI `streamlit run`,
lo que es más confiable que la API interna `bootstrap.run` para empaquetado.

Uso directo:

    uv run python -m simulacion_clinica.ui.launcher

Uso con PyInstaller (generar .exe en Windows):

    pyinstaller simulacion-clinica.spec --clean --noconfirm
"""

from __future__ import annotations

import os
import subprocess
import sys
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


def main() -> None:
    app_path = _resolver_app_path()

    # Construir el comando streamlit run con flags explícitos
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

    # En modo empaquetado (PyInstaller), el PYTHONPATH puede no incluir
    # el directorio del ejecutable. Lo agregamos explícitamente.
    env = os.environ.copy()
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        env["PYTHONPATH"] = str(base) + os.pathsep + env.get("PYTHONPATH", "")

    try:
        subprocess.run(cmd, env=env, check=True)  # noqa: S603
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()