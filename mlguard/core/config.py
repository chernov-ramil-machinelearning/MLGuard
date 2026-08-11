"""
Загрузка конфигурации mlguard.

Приоритет значений: CLI-флаги > mlguard.toml > дефолты в коде.
Если файл конфига не указан явно, ищем mlguard.toml в текущей директории.
"""
from pathlib import Path

import click

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]


DEFAULTS: dict = {
    "target_col": None,
    "time_col": None,
    "checks": None,        # None = все проверки
    "fail_on": "CRITICAL",  # минимальная severity для ненулевого exit code
    "format": "table",
}


def load_config(config_path: str | None) -> dict:
    """Читает mlguard.toml (если есть) и накладывает поверх дефолтов."""
    if config_path is None:
        implicit = Path("mlguard.toml")
        config_path = str(implicit) if implicit.exists() else None

    if config_path is None:
        return dict(DEFAULTS)

    path = Path(config_path)
    if not path.exists():
        raise click.ClickException(f"Конфиг не найден: {path}")

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    user_config = raw.get("mlguard", raw)  # поддержим и плоский toml без [mlguard]
    return {**DEFAULTS, **user_config}


def merge_cli_overrides(config: dict, **cli_values) -> dict:
    """Явно переданные CLI-флаги (не None) перетирают конфиг."""
    for key, value in cli_values.items():
        if value is not None:
            config[key] = value
    return config
