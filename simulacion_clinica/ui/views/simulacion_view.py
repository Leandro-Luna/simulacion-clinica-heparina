"""Vista de simulación base con Streamlit."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from simulacion_clinica.simulacion import simular_replicas
from simulacion_clinica.ui.components.charts import (
    chart_costo_acumulado,
    chart_demanda_vs_dia,
    chart_replicas_ctf,
    chart_stock_vs_dia,
)
from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui.utils import exportar_simulacion_bytes, safe_dataframe

_ETIQUETAS_STATS = {"Promedio", "Desvío", "Mín", "Máx", "IC Inf", "IC Sup"}


def _split_resumen(df_resumen: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, float]]:
    """Separa el resumen en filas de réplicas y dict de estadísticas."""
    mascara_stats = df_resumen["replica"].isin(_ETIQUETAS_STATS)
    df_stats = df_resumen[mascara_stats]
    df_replicas = df_resumen[~mascara_stats]

    stats: dict[str, float] = {}
    for _, fila in df_stats.iterrows():
        etiqueta = str(fila["replica"])
        stats[etiqueta] = float(fila["CTF"])
    return df_replicas, stats


def render(state: UIConfigState) -> None:
    st.header("Simulación base")

    col_btn1, col_btn2 = st.columns([1, 1])
    ejecutar = col_btn1.button("Ejecutar simulación", type="primary", key="sim_ejecutar")

    if ejecutar:
        st.session_state["sim_df_corrida1"] = None
        st.session_state["sim_df_resumen"] = None

    df_corrida1 = st.session_state.get("sim_df_corrida1")
    df_resumen = st.session_state.get("sim_df_resumen")

    if ejecutar or df_corrida1 is None:
        with st.spinner("Ejecutando simulación..."):
            cfg = state.to_config()
            df_corrida1, df_resumen = simular_replicas(cfg)
            st.session_state["sim_df_corrida1"] = df_corrida1
            st.session_state["sim_df_resumen"] = df_resumen

    if df_corrida1 is not None and df_resumen is not None:
        df_replicas, stats = _split_resumen(df_resumen)

        st.subheader("Estadísticas (IC 95%)")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("CTF promedio", f"${stats.get('Promedio', 0):,.0f}")
        col2.metric("Desvío", f"${stats.get('Desvío', 0):,.0f}")
        col3.metric("Mín", f"${stats.get('Mín', 0):,.0f}")
        col4.metric("IC Inf", f"${stats.get('IC Inf', 0):,.0f}")
        col5.metric("IC Sup", f"${stats.get('IC Sup', 0):,.0f}")

        st.subheader("Gráficos")
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Stock", "Costo acumulado", "Demanda", "CTF por réplica"]
        )
        with tab1:
            st.plotly_chart(chart_stock_vs_dia(df_corrida1), width="stretch")
        with tab2:
            st.plotly_chart(chart_costo_acumulado(df_corrida1), width="stretch")
        with tab3:
            st.plotly_chart(chart_demanda_vs_dia(df_corrida1), width="stretch")
        with tab4:
            st.plotly_chart(chart_replicas_ctf(df_resumen), width="stretch")

        st.subheader("Tablas")
        with st.expander("Detalle por día (Corrida 1)", expanded=False):
            st.dataframe(df_corrida1, width="stretch", hide_index=True)
        with st.expander("Resumen de réplicas", expanded=False):
            st.dataframe(safe_dataframe(df_replicas), width="stretch", hide_index=True)

        excel_bytes = exportar_simulacion_bytes(df_corrida1, df_resumen)
        st.download_button(
            label="Exportar a Excel",
            data=excel_bytes,
            file_name="resultado_simulacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="sim_download",
        )