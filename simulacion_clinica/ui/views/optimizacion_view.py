"""Vista de optimización por punto de emisión con Streamlit."""

from __future__ import annotations

import streamlit as st

from simulacion_clinica.optimizacion import optimizar, simular_optimizacion
from simulacion_clinica.ui.components.charts import (
    chart_costo_acumulado,
    chart_optimizacion_ctf,
    chart_optimizacion_mejor_detalle,
)
from simulacion_clinica.ui.config_state import UIConfigState
from simulacion_clinica.ui.utils import exportar_optimizacion_bytes


def render(state: UIConfigState) -> None:
    st.header("Optimización")

    col_btn1, col_btn2 = st.columns([1, 1])
    ejecutar = col_btn1.button("Ejecutar optimización", type="primary")
    descargar = col_btn2.button("Exportar a Excel", disabled=True)

    if ejecutar:
        st.session_state["opt_df_resultados"] = None
        st.session_state["opt_df_mejor"] = None

    df_resultados = st.session_state.get("opt_df_resultados")
    df_mejor = st.session_state.get("opt_df_mejor")

    if ejecutar or df_resultados is None:
        with st.spinner("Ejecutando optimización..."):
            cfg = state.to_config_optimizacion()
            puntos_emision = list(range(state.pep_min, state.pep_max + 1, state.pep_paso))
            tamanios_pedido = list(range(state.tp_min, state.tp_max + 1, state.tp_paso))

            df_resultados = optimizar(cfg, puntos_emision, tamanios_pedido)
            mejor = df_resultados.iloc[0]
            cfg_mejor = state.to_config_optimizacion()
            cfg_mejor.TP = int(mejor["tamaño_pedido"])
            cfg_mejor.punto_emision_pedido = int(mejor["punto_emision_pedido"])
            cfg_mejor.seed = None
            df_mejor, _ = simular_optimizacion(cfg_mejor)

            st.session_state["opt_df_resultados"] = df_resultados
            st.session_state["opt_df_mejor"] = df_mejor

    if df_resultados is not None and df_mejor is not None:
        mejor = df_resultados.iloc[0]
        col1, col2, col3 = st.columns(3)
        col1.metric("Mejor PEP", f"{int(mejor['punto_emision_pedido'])}")
        col2.metric("Mejor TP", f"{int(mejor['tamaño_pedido'])}")
        col3.metric("CTF promedio", f"${mejor['CTF_promedio']:,.0f}")

        st.subheader("Gráficos")
        tab1, tab2, tab3 = st.tabs(
            ["Ranking combinaciones", "Stock mejor combinación", "Costo mejor combinación"]
        )
        with tab1:
            st.plotly_chart(
                chart_optimizacion_ctf(df_resultados, top_n=10), use_container_width=True
            )
        with tab2:
            st.plotly_chart(
                chart_optimizacion_mejor_detalle(df_mejor), use_container_width=True
            )
        with tab3:
            st.plotly_chart(chart_costo_acumulado(df_mejor), use_container_width=True)

        st.subheader("Tablas")
        with st.expander("Combinaciones evaluadas", expanded=False):
            st.dataframe(df_resultados, use_container_width=True, hide_index=True)
        with st.expander("Detalle mejor combinación", expanded=False):
            st.dataframe(df_mejor, use_container_width=True, hide_index=True)

        if descargar:
            excel_bytes = exportar_optimizacion_bytes(df_resultados, df_mejor)
            st.download_button(
                label="Descargar Excel",
                data=excel_bytes,
                file_name="resultado_optimizacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )