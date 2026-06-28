"""Tests para el modelo de optimización por punto de emisión."""

import pandas as pd

from simulacion_clinica.optimizacion import (
    ConfigOptimizacion,
    optimizar,
    simular_optimizacion,
)


def _cfg_base(**overrides) -> ConfigOptimizacion:
    """Config base con semilla fija para tests deterministas."""
    cfg = ConfigOptimizacion(seed=42, TF=60, n_replicas=3)
    for clave, valor in overrides.items():
        setattr(cfg, clave, valor)
    return cfg


class TestSimularOptimizacion:
    def test_retorna_dataframe_y_resultados(self):
        df, res = simular_optimizacion(_cfg_base())
        assert isinstance(df, pd.DataFrame)
        assert isinstance(res, dict)

    def test_cantidad_de_filas_igual_a_TF(self):
        df, _ = simular_optimizacion(_cfg_base(TF=30))
        assert len(df) == 30

    def test_columnas_esperadas(self):
        df, _ = simular_optimizacion(_cfg_base())
        columnas = {
            "dia",
            "fecha",
            "dia_nombre",
            "demanda_cc",
            "stock_final",
            "recibe_pedido",
            "hace_pedido",
            "compra_emergencia",
            "costo_emerg_dia",
            "costo_pedido_dia",
            "costo_total_acum",
        }
        assert columnas.issubset(set(df.columns))

    def test_reorder_se_dispara_por_pep_no_por_ventana(self):
        # Con PEP alto y stock inicial bajo, se debe disparar el pedido el día 1
        df, _ = simular_optimizacion(_cfg_base(ST_inicial=500, punto_emision_pedido=2000, TF=5))
        assert bool(df["hace_pedido"].iloc[0])

    def test_no_hay_pedido_si_stock_sobre_pep(self):
        # Con PEP muy bajo y stock inicial alto, no hay pedido
        df, _ = simular_optimizacion(_cfg_base(ST_inicial=5000, punto_emision_pedido=100, TF=5))
        assert not bool(df["hace_pedido"].any())

    def test_un_solo_pedido_en_transito(self):
        # Con PEP alto, el pedido se hace el día 1; no debe haber otro hasta que llegue
        df, _ = simular_optimizacion(
            _cfg_base(ST_inicial=500, punto_emision_pedido=2000, TF=15, seed=99)
        )
        pedidos = df[df["hace_pedido"]]
        # Los pedidos deben estar separados por al menos la demora mínima (10 días)
        dias_pedidos = pedidos["dia"].tolist()
        for i in range(1, len(dias_pedidos)):
            assert dias_pedidos[i] - dias_pedidos[i - 1] >= 10

    def test_emergencia_cuando_stock_baja_ss(self):
        df, _ = simular_optimizacion(_cfg_base(ST_inicial=200, SS=250, TF=5))
        assert bool(df["compra_emergencia"].any())

    def test_costo_total_igual_suma_componentes(self):
        df, res = simular_optimizacion(_cfg_base(TF=30))
        total = df["costo_emerg_dia"].sum() + df["costo_pedido_dia"].sum()
        assert abs(res["CTF"] - total) < 1e-6

    def test_pedido_solo_una_vez_por_mes(self):
        df, _ = simular_optimizacion(_cfg_base(TF=360, seed=42))
        df = df.copy()
        df["mes"] = pd.to_datetime(df["fecha"]).dt.month
        pedidos_por_mes: pd.Series = df.groupby("mes")["hace_pedido"].sum()  # type: ignore[assignment]
        assert bool((pedidos_por_mes <= 1).all())


class TestOptimizar:
    def test_retorna_dataframe(self):
        df = optimizar(
            ConfigOptimizacion(TF=30, n_replicas=3),
            puntos_emision=[1000, 2000],
            tamanios_pedido=[2000, 3000],
        )
        assert isinstance(df, pd.DataFrame)

    def test_cantidad_de_filas_igual_producto_cartesiano(self):
        df = optimizar(
            ConfigOptimizacion(TF=30, n_replicas=3),
            puntos_emision=[1000, 2000, 3000],
            tamanios_pedido=[2000, 3000],
        )
        assert len(df) == 6

    def test_columnas_esperadas(self):
        df = optimizar(
            ConfigOptimizacion(TF=30, n_replicas=3),
            puntos_emision=[1000],
            tamanios_pedido=[2000],
        )
        columnas = {
            "punto_emision_pedido",
            "tamaño_pedido",
            "CTF_promedio",
            "IC_inf",
            "IC_sup",
            "CTEM_prom",
            "CTEP_prom",
            "n_pedidos_prom",
            "n_emergencias_prom",
            "n_recepciones_prom",
        }
        assert columnas.issubset(set(df.columns))

    def test_ordenado_por_ctf_promedio_ascendente(self):
        df = optimizar(
            ConfigOptimizacion(TF=30, n_replicas=3),
            puntos_emision=[500, 1000, 2000, 3000],
            tamanios_pedido=[2000, 3000],
        )
        assert bool(df["CTF_promedio"].is_monotonic_increasing)

    def test_ic_inf_menor_o_igual_promedio_menor_o_igual_ic_sup(self):
        df = optimizar(
            ConfigOptimizacion(TF=30, n_replicas=5),
            puntos_emision=[1000, 2000],
            tamanios_pedido=[2000, 3000],
        )
        for _, fila in df.iterrows():
            assert fila["IC_inf"] <= fila["CTF_promedio"] <= fila["IC_sup"]

    def test_mejor_combinacion_tiene_ctf_minimo(self):
        df = optimizar(
            ConfigOptimizacion(TF=30, n_replicas=3),
            puntos_emision=[500, 1000, 2000],
            tamanios_pedido=[2000, 3000],
        )
        assert df["CTF_promedio"].iloc[0] == df["CTF_promedio"].min()
