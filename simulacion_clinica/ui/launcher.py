"""Launcher para empaquetar la app Streamlit como ejecutable con PyInstaller.

Este script arranca Streamlit programáticamente sin depender del CLI
`streamlit run`, lo que permite empaquetarlo con PyInstaller en un .exe.

Uso directo:

    uv run python -m simulacion_clinica.ui.launcher

Uso con PyInstaller (generar .exe en Windows):

    pyinstaller simulacion_clinica/ui/launcher.py \\
        --name simulacion-clinica \\
        --collect-all streamlit \\
        --collect-all plotly \\
        --add-data "simulacion_clinica/ui/app.py;simulacion_clinica/ui" \\
        --add-data "simulacion_clinica/ui/views;simulacion_clinica/ui/views" \\
        --add-data "simulacion_clinica/ui/components;simulacion_clinica/ui/components" \\
        --add-data "simulacion_clinica/ui/config_state.py;simulacion_clinica/ui" \\
        --add-data "simulacion_clinica/ui/utils.py;simulacion_clinica/ui" \\
        --add-data "simulacion_clinica;simulacion_clinica" \\
        --onefile
"""

from __future__ import annotations

import sys
import webbrowser
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

    # Abrir el navegador automáticamente después de un breve delay
    import threading

    def _abrir_navegador() -> None:
        import time

        time.sleep(2)
        webbrowser.open("http://localhost:8501")

    threading.Thread(target=_abrir_navegador, daemon=True).start()

    bootstrap.run(
        main_script_path=app_path,
        is_hello=False,
        args=[],
        flag_options={
            "server.port": 8501,
            "server.headless": False,
            "browser.gatherUsageStats": False,
        },
    )


if __name__ == "__main__":
    main()