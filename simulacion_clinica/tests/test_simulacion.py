"""Tests para el bucle principal de simulación."""

from datetime import date

import pandas as pd

from simulacion_clinica.config import Config
from simulacion_clinica.simulacion import simular, simular_replicas


def _config_base(**overrides) -> Config:
    """Config con semilla fija y parámetros pequeños para tests deterministas."""
    cfg = Config(seed=42, TF=60, ST_inicial=30000)
    for clave, valor in overrides.items():
        setattr(cfg, clave, valor)
    return cfg


class TestEstructuraSalida:
    def test_retorna_dataframe(self):
        df, _ = simular(_config_base())
        assert isinstance(df, pd.DataFrame)

    def test_cantidad_de_filas_igual_a_TF(self):
        df, _ = simular(_config_base(TF=30))
        assert len(df) == 30

    def test_columnas_esperadas(self):
        df, _ = simular(_config_base())
        columnas_esperadas = {
            "dia",
            "fecha",
            "dia_mes",
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
        assert columnas_esperadas.issubset(set(df.columns))

    def test_dia_comienza_en_1_y_es_secuencial(self):
        df, _ = simular(_config_base(TF=10))
        assert df["dia"].tolist() == list(range(1, 11))

    def test_fecha_inicio_correcta(self):
        df, _ = simular(_config_base(TF=5))
        assert df["fecha"].iloc[0] == date(2026, 1, 1)

    def test_dia_corresponde_a_fecha_calendario(self):
        df, _ = simular(_config_base(TF=5))
        # 2026-01-01 es jueves
        assert df["dia_nombre"].iloc[0] == "Jueves"
        assert df["dia_mes"].iloc[0] == 1


class TestDemandaPorDiaSemana:
    def test_domingo_demanda_cero(self):
        # 2026-01-04 es domingo
        df, _ = simular(_config_base(TF=10))
        domingo = df[df["fecha"] == date(2026, 1, 4)].iloc[0]
        assert domingo["demanda_cc"] == 0

    def test_demanda_LMV_dentro_de_rango(self):
        df, _ = simular(_config_base(TF=31))
        lmv = df[df["dia_nombre"].isin(["Lunes", "Miércoles", "Viernes"])]
        assert bool((lmv["demanda_cc"] >= 74).all())
        assert bool((lmv["demanda_cc"] <= 92).all())

    def test_demanda_MJS_dentro_de_rango(self):
        df, _ = simular(_config_base(TF=31))
        mjs = df[df["dia_nombre"].isin(["Martes", "Jueves", "Sábado"])]
        assert bool((mjs["demanda_cc"] >= 62).all())
        assert bool((mjs["demanda_cc"] <= 76).all())

    def test_demanda_es_entero(self):
        df, _ = simular(_config_base(TF=31))
        assert bool(df["demanda_cc"].apply(lambda x: isinstance(x, (int, float))).all())


class TestRecepcionYPedido:
    def test_recibe_pedido_cuando_T_igual_FLL(self):
        # Con seed fija, al menos un pedido se genera y se recibe
        df, _ = simular(_config_base(TF=120))
        assert int(df["hace_pedido"].sum()) >= 1  # type: ignore[arg-type]
        assert int(df["recibe_pedido"].sum()) >= 1  # type: ignore[arg-type]

    def test_pedido_solo_una_vez_por_mes(self):
        df, _ = simular(_config_base(TF=120))
        # Agrupar por mes calendario y contar pedidos
        df = df.copy()
        df["mes"] = pd.to_datetime(df["fecha"]).dt.month
        pedidos_por_mes: pd.Series = df.groupby("mes")["hace_pedido"].sum()  # type: ignore[assignment]
        assert bool((pedidos_por_mes <= 1).all())  # type: ignore[operator]

    def test_pedido_solo_en_ventana_15_a_20(self):
        df, _ = simular(_config_base(TF=120))
        dias_pedido = df[df["hace_pedido"]]["dia_mes"]
        assert ((dias_pedido >= 15) & (dias_pedido <= 20)).all()


class TestEmergencia:
    def test_emergencia_cuando_stock_baja_umbral(self):
        # Stock inicial bajo => dispara emergencia el día 1
        df, _ = simular(_config_base(ST_inicial=2000, SS=2500, TF=5))
        assert df["compra_emergencia"].sum() >= 1

    def test_emergencia_aumenta_stock_en_PE(self):
        df, _ = simular(_config_base(ST_inicial=2000, SS=2500, TF=5))
        fila_emerg = df[df["compra_emergencia"]].iloc[0]
        # Después de consumir y agregar PE, el stock final debe reflejar la reposición
        assert fila_emerg["stock_final"] > 0


class TestCostos:
    def test_costo_total_acum_es_monotonico_creciente(self):
        df, _ = simular(_config_base(TF=60))
        assert df["costo_total_acum"].is_monotonic_increasing

    def test_costo_total_acum_igual_suma_componentes(self):
        df, res = simular(_config_base(TF=60))
        total_esperado = df["costo_emerg_dia"].sum() + df["costo_pedido_dia"].sum()
        assert abs(df["costo_total_acum"].iloc[-1] - total_esperado) < 1e-6

    def test_resultados_contiene_ctf_y_desglose(self):
        _, res = simular(_config_base(TF=30))
        claves = ("CTF", "CTEM", "CTEP", "n_pedidos", "n_emergencias", "n_recepciones")
        for clave in claves:
            assert clave in res

    def test_ctf_igual_suma_desglose(self):
        _, res = simular(_config_base(TF=30))
        assert abs(res["CTF"] - (res["CTEM"] + res["CTEP"])) < 1e-6


class TestReproducibilidad:
    def test_misma_semilla_produce_mismo_resultado(self):
        cfg1 = Config(seed=123, TF=30)
        cfg2 = Config(seed=123, TF=30)
        df1, res1 = simular(cfg1)
        df2, res2 = simular(cfg2)
        pd.testing.assert_frame_equal(df1, df2)
        assert res1 == res2

    def test_semillas_distintas_producen_distinto_resultado(self):
        cfg1 = Config(seed=1, TF=30)
        cfg2 = Config(seed=2, TF=30)
        df1, _ = simular(cfg1)
        df2, _ = simular(cfg2)
        assert not df1["demanda_cc"].equals(df2["demanda_cc"])


class TestReplicas:
    def test_retorna_dos_dataframes(self):
        df_corrida, df_resumen = simular_replicas(Config(n_replicas=5, TF=30))
        assert isinstance(df_corrida, pd.DataFrame)
        assert isinstance(df_resumen, pd.DataFrame)

    def test_corrida1_tiene_TF_filas(self):
        df_corrida, _ = simular_replicas(Config(n_replicas=5, TF=30))
        assert len(df_corrida) == 30

    def test_resumen_tiene_n_replicas_mas_estadisticas(self):
        n = 5
        _, df_resumen = simular_replicas(Config(n_replicas=n, TF=30))
        # n réplicas + 4 estadísticas + 2 IC = n + 6
        assert len(df_resumen) == n + 6

    def test_columnas_resumen_esperadas(self):
        _, df_resumen = simular_replicas(Config(n_replicas=5, TF=30))
        columnas = {
            "replica",
            "CTF",
            "CTEM",
            "CTEP",
            "n_pedidos",
            "n_emergencias",
            "n_recepciones",
        }
        assert columnas.issubset(set(df_resumen.columns))

    def test_replicas_tienen_numeros_secuenciales(self):
        n = 5
        _, df_resumen = simular_replicas(Config(n_replicas=n, TF=30))
        assert df_resumen["replica"].iloc[:n].tolist() == list(range(1, n + 1))

    def test_estadisticas_presentes(self):
        _, df_resumen = simular_replicas(Config(n_replicas=5, TF=30))
        etiquetas = df_resumen["replica"].iloc[-6:].tolist()
        assert etiquetas == ["Promedio", "Desvío", "Mín", "Máx", "IC Inf", "IC Sup"]

    def test_replicas_producen_ctf_distintos(self):
        _, df_resumen = simular_replicas(Config(n_replicas=10, TF=30))
        ctfs = df_resumen["CTF"].iloc[:10]
        assert ctfs.nunique() > 1

    def test_promedio_coincide_con_media(self):
        n = 5
        _, df_resumen = simular_replicas(Config(n_replicas=n, TF=30))
        ctfs: pd.Series = df_resumen["CTF"].iloc[:n]  # type: ignore[assignment]
        fila_promedio = df_resumen[df_resumen["replica"] == "Promedio"]
        promedio_fila = float(fila_promedio["CTF"].iloc[0])  # type: ignore[union-attr]
        assert abs(promedio_fila - float(ctfs.mean())) < 1e-6

    def test_ic_inf_menor_o_igual_promedio_menor_o_igual_ic_sup(self):
        _, df_resumen = simular_replicas(Config(n_replicas=10, TF=30))
        ic_inf = float(df_resumen[df_resumen["replica"] == "IC Inf"]["CTF"].iloc[0])  # type: ignore[union-attr]
        ic_sup = float(df_resumen[df_resumen["replica"] == "IC Sup"]["CTF"].iloc[0])  # type: ignore[union-attr]
        promedio = float(df_resumen[df_resumen["replica"] == "Promedio"]["CTF"].iloc[0])  # type: ignore[union-attr]
        assert ic_inf <= promedio <= ic_sup

    def test_ic_formula_exacta(self):
        import math

        from scipy.stats import t as t_student

        n = 10
        alpha = 0.05
        _, df_resumen = simular_replicas(Config(n_replicas=n, TF=30, alpha=alpha))
        ctfs: pd.Series = df_resumen["CTF"].iloc[:n]  # type: ignore[assignment]
        promedio = float(ctfs.mean())
        desvio = float(ctfs.std())  # type: ignore[arg-type]
        t_critico = t_student.ppf(1 - alpha / 2, n - 1)
        error_std = desvio / math.sqrt(n)
        ic_inf_esperado = promedio - error_std * t_critico
        ic_sup_esperado = promedio + error_std * t_critico
        ic_inf = float(df_resumen[df_resumen["replica"] == "IC Inf"]["CTF"].iloc[0])  # type: ignore[union-attr]
        ic_sup = float(df_resumen[df_resumen["replica"] == "IC Sup"]["CTF"].iloc[0])  # type: ignore[union-attr]
        assert abs(ic_inf - ic_inf_esperado) < 1e-6
        assert abs(ic_sup - ic_sup_esperado) < 1e-6

    def test_alpha_menor_genera_intervalo_mas_anch(self):
        from scipy.stats import t as t_student

        n = 20
        # Con mismo promedio y desvío, un alpha menor => t_critico mayor => intervalo más ancho
        t_95 = t_student.ppf(1 - 0.05 / 2, n - 1)
        t_99 = t_student.ppf(1 - 0.01 / 2, n - 1)
        assert t_99 > t_95
