# Agent Notes - simulacion-clinica

Small academic Python project (Monte Carlo simulation of Heparina stock management for a dialysis center). Managed with `uv`.

## Run commands

```bash
# Install/sync deps
uv sync

# Run simulation (writes resultado_simulacion.xlsx in repo root)
uv run python -m simulacion_clinica.main

# Run optimization grid search (writes resultado_optimizacion.xlsx in repo root)
uv run python -m simulacion_clinica.main_optimizacion

# Run UI (Flet web mode by default; opens browser)
uv run python -m simulacion_clinica.ui.app

# Force native desktop window
FLET_VIEW=desktop uv run python -m simulacion_clinica.ui.app

# Validation
uv run pytest
uv run ruff check .
uv run pyright
```

## Project structure

- `simulacion_clinica/config.py` — base `Config` dataclass (defaults for `main.py`).
- `simulacion_clinica/generadores.py` — inverse-transform random variates (`demanda_LMV`, `demanda_MJS`, `demora_proveedor`).
- `simulacion_clinica/simulacion.py` — base model: calendar-day loop, scheduled reorder window (days 15–20), emergency purchases.
- `simulacion_clinica/optimizacion.py` — alternate model with `ConfigOptimizacion` and reorder by PEP (punto de emisión de pedido); includes `optimizar()` grid search.
- `simulacion_clinica/main.py` and `main_optimizacion.py` — CLI entry points.
- `simulacion_clinica/ui/` — Flet desktop UI.
  - `app.py` — entry point of the UI.
  - `config_state.py` — shared editable state.
  - `views/config_view.py`, `views/simulacion_view.py`, `views/optimizacion_view.py` — tabs.
  - `components/data_table.py`, `components/charts.py` — reusable table and matplotlib charts.
- `simulacion_clinica/tests/` — pytest suite.

## Known gotchas

- **README defaults do not match code**: e.g. `SS` in `config.py` is `300`, `ST_inicial` is `1000`; README lists different values. Trust `config.py` / `optimizacion.py`.
- `pyright` is configured with `venvPath = ".venv"` in `pyproject.toml`; it runs against the project package only (`include = ["simulacion_clinica"]`).

## Conventions

- Python 3.12+ syntax (`X | None`, etc.).
- `ruff` line length is 100; selected rules: `E`, `F`, `I`, `UP`, `B`, `SIM`.
- No CI, no task runner, no pre-commit hooks.
