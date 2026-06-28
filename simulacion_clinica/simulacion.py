"""Bucle principal de la simulación de gestión de stock de Heparina.

Implementa el flowchart del TP: avance de tiempo, recepción de pedidos,
demanda diaria por grupo de días, compra de emergencia y reorden programado.
"""

import math
import random
from dataclasses import asdict
from datetime import timedelta

import pandas as pd
from scipy.stats import t as t_student

from simulacion_clinica.config import Config
from simulacion_clinica.generadores import demanda_LMV, demanda_MJS, demora_proveedor

INF = float("inf")

_NOMBRES_DIAS = {
    1: "Lunes",
    2: "Martes",
    3: "Miércoles",
    4: "Jueves",
    5: "Viernes",
    6: "Sábado",
    7: "Domingo",
}


def _demanda_diaria(dia_sem: int, rng: random.Random) -> int:
    """Calcula la demanda diaria de Heparina (cc) según el día de la semana.

    Lun/Mié/Vie (1,3,5) -> 74 + 18*r  (Uniforme 74-92)
    Mar/Jue/Sáb (2,4,6) -> 62 + 14*r  (Uniforme 62-76)
    Domingo (7)         -> 0
    """
    if dia_sem in (1, 3, 5):
        return math.ceil(demanda_LMV(rng.random()))
    if dia_sem in (2, 4, 6):
        return math.ceil(demanda_MJS(rng.random()))
    return 0


def simular(cfg: Config) -> tuple[pd.DataFrame, dict]:
    """Ejecuta la simulación y retorna (DataFrame por día, resultados finales).

    El DataFrame contiene una fila por día simulado con el detalle de stock,
    demandas, pedidos, emergencias y costos.
    """
    rng = random.Random(cfg.seed)

    # --- Estado de la simulación ---
    ST = cfg.ST_inicial
    FLL = INF  # fecha (en T) de llegada del pedido
    COMPRA_MES = 0  # indicador de compra realizada en el mes

    # Acumuladores de costos
    CTEM = 0.0
    CTEP = 0.0
    CTF = 0.0

    # Contadores
    n_pedidos = 0
    n_emergencias = 0
    n_recepciones = 0

    registros: list[dict] = []

    for T in range(1, cfg.TF + 1):
        fecha = cfg.fecha_inicio + timedelta(days=T - 1)
        dia_mes = fecha.day
        dia_sem = fecha.isoweekday()

        # Reset de COMPRA_MES al inicio de cada mes calendario
        if dia_mes == 1:
            COMPRA_MES = 0

        # --- Recepción de pedido ---
        recibe_pedido = False
        if T == FLL:
            ST += cfg.TP
            FLL = INF
            recibe_pedido = True
            n_recepciones += 1

        # --- Demanda diaria ---
        CD = _demanda_diaria(dia_sem, rng)
        ST -= CD

        # --- Compra de emergencia ---
        compra_emergencia = False
        costo_emerg_dia = 0.0
        if ST <= cfg.SS:
            costo_emerg_dia = cfg.costo_unitario_emergencia * cfg.PE
            CTEM += costo_emerg_dia
            ST += cfg.PE
            compra_emergencia = True
            n_emergencias += 1

        # --- Reorden programado ---
        hace_pedido = False
        costo_pedido_dia = 0.0
        if cfg.dia_pedido_desde <= dia_mes <= cfg.dia_pedido_hasta and COMPRA_MES == 0:
            DE = math.ceil(demora_proveedor(rng.random()))
            COMPRA_MES = 1
            FLL = T + DE
            costo_pedido_dia = cfg.costo_unitario_pedido * cfg.TP
            CTEP += costo_pedido_dia
            hace_pedido = True
            n_pedidos += 1

        # --- Costo total acumulado ---
        CTF = CTEM + CTEP

        registros.append(
            {
                "dia": T,
                "fecha": fecha,
                "dia_mes": dia_mes,
                "dia_nombre": _NOMBRES_DIAS[dia_sem],
                "demanda_cc": CD,
                "stock_final": ST,
                "recibe_pedido": recibe_pedido,
                "hace_pedido": hace_pedido,
                "compra_emergencia": compra_emergencia,
                "costo_emerg_dia": costo_emerg_dia,
                "costo_pedido_dia": costo_pedido_dia,
                "costo_total_acum": CTF,
            }
        )

    df = pd.DataFrame(registros)
    resultados = {
        "CTF": CTF,
        "CTEM": CTEM,
        "CTEP": CTEP,
        "n_pedidos": n_pedidos,
        "n_emergencias": n_emergencias,
        "n_recepciones": n_recepciones,
        "config": asdict(cfg),
    }
    return df, resultados


def simular_replicas(cfg: Config) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ejecuta la simulación N veces (una por réplica) con semillas aleatorias.

    Retorna:
      - df_corrida1: DataFrame detallado por día de la primera réplica.
      - df_resumen: DataFrame con una fila por réplica + filas de estadísticas
        (Promedio, Desvío, Mín, Máx, IC Inf, IC Sup) al final.
    """
    filas_resumen: list[dict] = []
    df_corrida1: pd.DataFrame | None = None

    for i in range(1, cfg.n_replicas + 1):
        cfg_replica = Config(
            fecha_inicio=cfg.fecha_inicio,
            TF=cfg.TF,
            delta_t=cfg.delta_t,
            n_replicas=cfg.n_replicas,
            ST_inicial=cfg.ST_inicial,
            PE=cfg.PE,
            SS=cfg.SS,
            TP=cfg.TP,
            costo_unitario_pedido=cfg.costo_unitario_pedido,
            costo_unitario_emergencia=cfg.costo_unitario_emergencia,
            dia_pedido_desde=cfg.dia_pedido_desde,
            dia_pedido_hasta=cfg.dia_pedido_hasta,
            seed=None,  # aleatoria por corrida
            alpha=cfg.alpha,
        )
        df, res = simular(cfg_replica)

        if df_corrida1 is None:
            df_corrida1 = df

        filas_resumen.append(
            {
                "replica": i,
                "CTF": res["CTF"],
                "CTEM": res["CTEM"],
                "CTEP": res["CTEP"],
                "n_pedidos": res["n_pedidos"],
                "n_emergencias": res["n_emergencias"],
                "n_recepciones": res["n_recepciones"],
            }
        )

    df_resumen = pd.DataFrame(filas_resumen)

    # Filas de estadísticas
    columnas_numericas = [
        "CTF",
        "CTEM",
        "CTEP",
        "n_pedidos",
        "n_emergencias",
        "n_recepciones",
    ]
    estadisticas = pd.DataFrame(
        [
            {"replica": "Promedio", **{c: df_resumen[c].mean() for c in columnas_numericas}},
            {"replica": "Desvío", **{c: df_resumen[c].std() for c in columnas_numericas}},
            {"replica": "Mín", **{c: df_resumen[c].min() for c in columnas_numericas}},
            {"replica": "Máx", **{c: df_resumen[c].max() for c in columnas_numericas}},
        ]
    )
    df_resumen = pd.concat([df_resumen, estadisticas], ignore_index=True)

    # Intervalo de confianza para CTF (t-Student, solo CTF)
    n = cfg.n_replicas
    t_critico = t_student.ppf(1 - cfg.alpha / 2, n - 1)
    promedio_ctf = df_resumen["CTF"].iloc[:n].mean()
    desvio_ctf = df_resumen["CTF"].iloc[:n].std()
    error_std = desvio_ctf / math.sqrt(n)
    ic_inf = promedio_ctf - error_std * t_critico
    ic_sup = promedio_ctf + error_std * t_critico

    ic_filas = pd.DataFrame(
        [
            {"replica": "IC Inf", "CTF": ic_inf},
            {"replica": "IC Sup", "CTF": ic_sup},
        ]
    )
    df_resumen = pd.concat([df_resumen, ic_filas], ignore_index=True)

    assert df_corrida1 is not None
    return df_corrida1, df_resumen
