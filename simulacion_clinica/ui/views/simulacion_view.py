"""Vista de simulación base con Streamlit."""

from __future__ import annotations

import streamlit as st

from simulacion_clinica.simulacion import simular_replicas
from simulacion_clinica.ui.components.charts import (
    chart_costo_acumulado,
    chart_demanda_vs_dia,
    chart_replicas_ctf,
    chart_stock_vs_dia,
)
from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui.utils import exportar_simulacion_bytes


def render(state: UIConfigState) -> None:
    st.header("Simulación base")

    col_btn1, col_btn2 = st.columns([1, 1])
    ejecutar = col_btn1.button("Ejecutar simulación", type="primary")
    descargar = col_btn2.button("Exportar a Excel", disabled=True)

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
        ultima = df_corrida1.iloc[-1]
        col1, col2, col3 = st.columns(3)
        col1.metric("CTF final", f"${ultima['costo_total_acum']:,.0f}")
        col2.metric("Pedidos", f"{int(df_resumen['n_pedidos'].iloc[0])}")
        col3.metric("Emergencias", f"{int(df_resumen['n_emergencias'].iloc[0])}")

        st.subheader("Gráficos")
        tab1, tab2, tab3, tab4 = st.tabs(
            ["Stock", "Costo acumulado", "Demanda", "CTF por réplica"]
        )
        with tab1:
            st.plotly_chart(chart_stock_vs_dia(df_corrida1), use_container_width=True)
        with tab2:
            st.plotly_chart(chart_costo_acumulado(df_corrida1), use_container_width=True)
        with tab3:
            st.plotly_chart(chart_demanda_vs_dia(df_corrida1), use_container_width=True)
        with tab4:
            st.plotly_chart(chart_replicas_ctf(df_resumen), use_container_width=True)

        st.subheader("Tablas")
        with st.expander("Detalle por día (Corrida 1)", expanded=False):
            st.dataframe(df_corrida1, use_container_width=True, hide_index=True)
        with st.expander("Resumen de réplicas", expanded=False):
            st.dataframe(df_resumen, use_container_width=True, hide_index=True)

        if descargar:
            excel_bytes = exportar_simulacion_bytes(df_corrida1, df_resumen)
            st.download_button(
                label="Descargar Excel",
                data=excel_bytes,
                file_name="resultado_simulacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )