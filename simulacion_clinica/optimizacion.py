"""Modelo de optimización: reorden por punto de emisión + tamaño de pedido.

A diferencia del modelo base (reorden por ventana de días 15-20), este modelo
emite el pedido cuando el stock baja a un Punto de Emisión de Pedido (PEP).
Permite probar una grilla de combinaciones (PEP × tamaño de pedido) para
encontrar la que minimiza el costo total final (CTF) promedio.
"""

import math
import random
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta

import pandas as pd
from scipy.stats import t as t_student

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


@dataclass
class ConfigOptimizacion:
    """Parámetros del modelo de optimización por punto de emisión.

    A diferencia de Config, elimina la ventana de días (dia_pedido_desde/hasta)
    y agrega punto_emision_pedido (PEP). Renombra PE a cantidad_emergencia.
    """

    # --- Tiempo ---
    fecha_inicio: date = date(2026, 1, 1)
    TF: int = 365
    delta_t: int = 1
    n_replicas: int = 100

    # --- Stock (en cc) ---
    ST_inicial: int = 1000
    cantidad_emergencia: int = 500  # tamaño compra de emergencia (cc)
    SS: int = 300  # stock de seguridad (umbral de emergencia)
    TP: int = 1500  # tamaño del pedido programado (cc)
    punto_emision_pedido: int = 2000  # PEP: nivel de stock que dispara el pedido

    # --- Costos ---
    costo_unitario_pedido: int = 1150
    costo_unitario_emergencia: int = 2300

    # --- Aleatoriedad ---
    seed: int | None = None

    # --- Intervalo de confianza ---
    alpha: float = 0.05


def _demanda_diaria(dia_sem: int, rng: random.Random) -> int:
    """Calcula la demanda diaria de Heparina (cc) según el día de la semana."""
    if dia_sem in (1, 3, 5):
        return math.ceil(demanda_LMV(rng.random()))
    if dia_sem in (2, 4, 6):
        return math.ceil(demanda_MJS(rng.random()))
    return 0


def simular_optimizacion(cfg: ConfigOptimizacion) -> tuple[pd.DataFrame, dict]:
    """Ejecuta una corrida de simulación con reorden por PEP.

    Retorna (DataFrame por día, resultados finales).
    """
    rng = random.Random(cfg.seed)

    # --- Estado ---
    ST = cfg.ST_inicial
    IP = 0  # indicador de pedido en tránsito (0 = libre, 1 = hay pedido)
    FLL = INF
    COMPRA_MES = 0  # indicador de compra programada realizada en el mes

    CTEM = 0.0
    CTEP = 0.0
    CTF = 0.0

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
            IP = 0
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
            costo_emerg_dia = cfg.costo_unitario_emergencia * cfg.cantidad_emergencia
            CTEM += costo_emerg_dia
            ST += cfg.cantidad_emergencia
            compra_emergencia = True
            n_emergencias += 1

        # --- Reorden por punto de emisión (PEP) ---
        hace_pedido = False
        costo_pedido_dia = 0.0
        if cfg.punto_emision_pedido >= ST and IP == 0 and COMPRA_MES == 0:
            DE = math.ceil(demora_proveedor(rng.random()))
            IP = 1
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
    }
    return df, resultados


def optimizar(
    cfg_base: ConfigOptimizacion,
    puntos_emision: list[int],
    tamanios_pedido: list[int],
    on_combo_done: Callable[[int, int], None] | None = None,
) -> pd.DataFrame:
    """Grid search sobre el producto cartesiano PEP × tamaño de pedido.

    Por cada combinación corre n_replicas réplicas y calcula estadísticas.
    Retorna un DataFrame ordenado por CTF promedio ascendente.

    on_combo_done: callback opcional ``(completados, total)`` llamado tras
    cada combinación para reportar progreso.
    """
    filas: list[dict] = []
    total_combos = len(puntos_emision) * len(tamanios_pedido)
    completados = 0

    for pep in puntos_emision:
        for tp in tamanios_pedido:
            ctfs: list[float] = []
            ctems: list[float] = []
            cteps: list[float] = []
            n_peds: list[int] = []
            n_emergs: list[int] = []
            n_receps: list[int] = []

            for _ in range(cfg_base.n_replicas):
                cfg = ConfigOptimizacion(
                    fecha_inicio=cfg_base.fecha_inicio,
                    TF=cfg_base.TF,
                    delta_t=cfg_base.delta_t,
                    n_replicas=cfg_base.n_replicas,
                    ST_inicial=cfg_base.ST_inicial,
                    cantidad_emergencia=cfg_base.cantidad_emergencia,
                    SS=cfg_base.SS,
                    TP=tp,
                    punto_emision_pedido=pep,
                    costo_unitario_pedido=cfg_base.costo_unitario_pedido,
                    costo_unitario_emergencia=cfg_base.costo_unitario_emergencia,
                    seed=None,
                    alpha=cfg_base.alpha,
                )
                _, res = simular_optimizacion(cfg)
                ctfs.append(res["CTF"])
                ctems.append(res["CTEM"])
                cteps.append(res["CTEP"])
                n_peds.append(res["n_pedidos"])
                n_emergs.append(res["n_emergencias"])
                n_receps.append(res["n_recepciones"])

            # Estadísticas
            n = cfg_base.n_replicas
            promedio_ctf = sum(ctfs) / n
            desvio_ctf = (sum((x - promedio_ctf) ** 2 for x in ctfs) / (n - 1)) ** 0.5
            t_critico = t_student.ppf(1 - cfg_base.alpha / 2, n - 1)
            error_std = desvio_ctf / math.sqrt(n)
            ic_inf = promedio_ctf - error_std * t_critico
            ic_sup = promedio_ctf + error_std * t_critico

            filas.append(
                {
                    "punto_emision_pedido": pep,
                    "tamaño_pedido": tp,
                    "CTF_promedio": promedio_ctf,
                    "IC_inf": ic_inf,
                    "IC_sup": ic_sup,
                    "CTEM_prom": sum(ctems) / n,
                    "CTEP_prom": sum(cteps) / n,
                    "n_pedidos_prom": sum(n_peds) / n,
                    "n_emergencias_prom": sum(n_emergs) / n,
                    "n_recepciones_prom": sum(n_receps) / n,
                }
            )

            completados += 1
            if on_combo_done is not None:
                on_combo_done(completados, total_combos)

    df_resultados = pd.DataFrame(filas)
    df_resultados = df_resultados.sort_values("CTF_promedio", ascending=True).reset_index(drop=True)
    return df_resultados
