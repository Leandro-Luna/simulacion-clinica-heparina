"""Punto de entrada de la aplicación con Streamlit.

Ejecutar con:

    uv run streamlit run simulacion_clinica/ui/app.py
"""

from __future__ import annotations

import streamlit as st

from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui.views.config_view import render_sidebar
from simulacion_clinica.ui.views.optimizacion_view import render as render_optimizacion
from simulacion_clinica.ui.views.simulacion_view import render as render_simulacion


def init_state() -> UIConfigState:
    if "ui_state" not in st.session_state:
        st.session_state["ui_state"] = UIConfigState.from_defaults()
    return st.session_state["ui_state"]


def main() -> None:
    st.set_page_config(
        page_title="Simulación de Stock de Heparina",
        page_icon="🏥",
        layout="wide",
    )

    state = init_state()
    render_sidebar(state)

    st.title("Simulación de Stock de Heparina")
    st.caption("Centro de Diálisis — Monte Carlo")

    tab_sim, tab_opt = st.tabs(["Simulación", "Optimización"])
    with tab_sim:
        render_simulacion(state)
    with tab_opt:
        render_optimizacion(state)


if __name__ == "__main__":
    main()