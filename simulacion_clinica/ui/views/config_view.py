"""Vista de configuración: sidebar con parámetros editables."""

from __future__ import annotations

import streamlit as st

from simulacion_clinica.ui.config_state import UIConfigState


def render_sidebar(state: UIConfigState) -> None:
    """Renderiza el sidebar con todos los parámetros agrupados."""
    st.sidebar.title("Configuración")

    if st.sidebar.button("Restaurar defaults", use_container_width=True):
        state.reset()
        st.rerun()

    with st.sidebar.expander("Tiempo / aleatoriedad", expanded=True):
        state.TF = st.number_input("TF (días)", value=state.TF, min_value=1, step=1)
        state.n_replicas = st.number_input(
            "N° réplicas", value=state.n_replicas, min_value=1, step=1
        )
        seed_val = st.number_input(
            "Seed (vacío = aleatorio)",
            value=state.seed if state.seed is not None else 0,
            min_value=0,
            step=1,
            help="Dejar en 0 para semilla aleatoria",
        )
        state.seed = seed_val if seed_val > 0 else None
        state.alpha = st.number_input(
            "Alpha (IC)", value=state.alpha, min_value=0.001, max_value=0.5, step=0.01
        )

    with st.sidebar.expander("Stock", expanded=True):
        state.ST_inicial = st.number_input(
            "Stock inicial", value=state.ST_inicial, min_value=0, step=100
        )
        state.PE = st.number_input(
            "Compra emergencia (PE)", value=state.PE, min_value=0, step=100
        )
        state.SS = st.number_input(
            "Stock seguridad (SS)", value=state.SS, min_value=0, step=100
        )
        state.TP = st.number_input(
            "Tamaño pedido (TP)", value=state.TP, min_value=0, step=100
        )

    with st.sidebar.expander("Costos", expanded=True):
        state.costo_unitario_pedido = st.number_input(
            "Costo unitario pedido", value=state.costo_unitario_pedido, min_value=0, step=50
        )
        state.costo_unitario_emergencia = st.number_input(
            "Costo unitario emergencia",
            value=state.costo_unitario_emergencia,
            min_value=0,
            step=50,
        )

    with st.sidebar.expander("Modelo base (ventana de pedido)"):
        state.dia_pedido_desde = st.number_input(
            "Día pedido desde", value=state.dia_pedido_desde, min_value=1, max_value=31, step=1
        )
        state.dia_pedido_hasta = st.number_input(
            "Día pedido hasta", value=state.dia_pedido_hasta, min_value=1, max_value=31, step=1
        )

    with st.sidebar.expander("Optimización (grilla PEP × TP)"):
        state.punto_emision_pedido = st.number_input(
            "PEP default", value=state.punto_emision_pedido, min_value=0, step=100
        )
        state.pep_min = st.number_input(
            "PEP mín", value=state.pep_min, min_value=0, step=100
        )
        state.pep_max = st.number_input(
            "PEP máx", value=state.pep_max, min_value=0, step=100
        )
        state.pep_paso = st.number_input(
            "PEP paso", value=state.pep_paso, min_value=1, step=100
        )
        state.tp_min = st.number_input(
            "TP mín", value=state.tp_min, min_value=0, step=100
        )
        state.tp_max = st.number_input(
            "TP máx", value=state.tp_max, min_value=0, step=100
        )
        state.tp_paso = st.number_input(
            "TP paso", value=state.tp_paso, min_value=1, step=100
        )