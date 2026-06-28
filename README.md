# Simulación de Gestión de Stock de Heparina - Centro de Diálisis

Trabajo Práctico N°1 de la materia **Simulación** - UTN Facultad Regional Resistencia.

Grupo **"Los Estocásticos"**: Almirón Sabugo Alejo, Velazquez Victoria, Luna Leandro, Barboza Facundo.

## Descripción

Simulación de Monte Carlo del sistema de gestión de insumos críticos (Heparina) en un centro de diálisis de Corrientes Capital. El objetivo es determinar un **Punto de Emisión de Pedido (PE)** adecuado que minimice los costos totales evitando quiebres de stock.

El modelo considera dos variables aleatorias generadas vía **Método de la Transformada Inversa**:

| Variable | Distribución | Generador |
|---|---|---|
| Demanda diaria Lun/Mié/Vie | Uniforme (74, 92) | `x = 74 + 18·r` |
| Demanda diaria Mar/Jue/Sáb | Uniforme (62, 76) | `x = 62 + 14·r` |
| Demora del proveedor | Exponencial desplazada (10, 2.58) | `x = 10 - 2.58·ln(r)` |

Los domingos no hay demanda (no se realizan diálisis).

## Requisitos

- Python >= 3.12
- [uv](https://docs.astral.sh/uv/) (gestor de dependencias)

## Instalación

```bash
uv sync
```

## Uso

```bash
uv run python -m simulacion_clinica.main
```

### Interfaz web (Streamlit)

También podés ejecutar la aplicación web para configurar parámetros, correr la simulación/optimización y ver gráficos interactivos y tablas en el navegador:

```bash
uv run streamlit run simulacion_clinica/ui/app.py
```

La simulación:
1. Muestra en consola el DataFrame con el detalle por día (sin límites de columnas/filas).
2. Imprime un resumen con el costo total final (CTF) y su desglose.
3. Exporta los resultados a `resultado_simulacion.xlsx`.

### Salida por día (columnas del DataFrame)

| Columna | Descripción |
|---|---|
| `dia` | Día de la simulación (1 a 365) |
| `fecha` | Fecha calendario real |
| `dia_mes` | Día del mes (1-31) |
| `dia_nombre` | Día de la semana (Lunes, Martes, ...) |
| `demanda_cc` | Demanda diaria de Heparina en cc |
| `stock_final` | Stock al cierre del día en cc |
| `recibe_pedido` | True si llegó un pedido programado |
| `hace_pedido` | True si se generó un pedido al proveedor |
| `compra_emergencia` | True si se realizó compra de emergencia |
| `costo_emerg_dia` | Costo de compra de emergencia del día |
| `costo_pedido_dia` | Costo de pedido programado del día |
| `costo_total_acum` | Costo total acumulado hasta el día |

## Parámetros configurables

Todos los parámetros se configuran en `simulacion_clinica/config.py` (dataclass `Config`):

| Parámetro | Default | Descripción |
|---|---|---|
| `fecha_inicio` | 2026-01-01 | Fecha de inicio de la simulación |
| `TF` | 365 | Cantidad de días a simular |
| `ST_inicial` | 3000 | Stock inicial (cc) |
| `PE` | 500 | Tamaño de compra de emergencia (cc) |
| `SS` | 250 | Stock de seguridad / umbral de emergencia (cc) |
| `TP` | 1500 | Tamaño del pedido programado (cc) |
| `costo_unitario_pedido` | 1150 | Costo por cc de pedido programado |
| `costo_unitario_emergencia` | 2300 | Costo por cc de compra de emergencia |
| `dia_pedido_desde` | 15 | Inicio ventana de pedido |
| `dia_pedido_hasta` | 20 | Fin ventana de pedido |
| `seed` | None | Semilla aleatoria (None = aleatoria por corrida) |

## Lógica de la simulación

Por cada día `T` (de 1 a `TF`):

1. **Avance de tiempo**: `fecha = fecha_inicio + (T-1) días`
2. **Reset mensual**: si es día 1 del mes, se reinicia el indicador de compra mensual
3. **Recepción de pedido**: si `T == FLL` (fecha de llegada), se suma `TP` al stock
4. **Demanda diaria**: según día de la semana (LMV, MJS o Domingo=0)
5. **Consumo**: `ST -= demanda`
6. **Compra de emergencia**: si `ST ≤ SS`, se compra `PE` cc a costo unitario `costo_unitario_emergencia` (llega en el día)
7. **Reorden programado**: si `15 ≤ dia_mes ≤ 20` y no se hizo pedido este mes, se genera la demora y se programa la llegada
8. **Costo total acumulado**: `CTF = CTEM + CTEP`

## Estructura del proyecto

```
simulacion_clinica/
├── config.py        # Parámetros configurables (dataclass Config)
├── generadores.py   # Transformada inversa: demanda_LMV, demanda_MJS, demora_proveedor
├── simulacion.py    # Bucle principal del flowchart → DataFrame por día
├── main.py          # Entry point: corre sim, muestra y exporta resultados
└── tests/
    ├── test_generadores.py   # Tests de los generadores (12 tests)
    └── test_simulacion.py    # Tests del bucle de simulación (22 tests)
```

## Testing

```bash
uv run pytest          # tests
uv run ruff check .    # lint + formato
uv run pyright         # type check
```

## Generadores (Transformada Inversa)

Las fórmulas están hardcodeadas según el enunciado del TP:

```python
def demanda_LMV(r):       return 74 + 18 * r        # Uniforme(74, 92)
def demanda_MJS(r):       return 62 + 14 * r        # Uniforme(62, 76)
def demora_proveedor(r):  return 10 - 2.58 * ln(r)  # Exp. desplazada (min=10, media=2.58)
```

Donde `r` es un número pseudoaleatorio en `(0, 1]`.