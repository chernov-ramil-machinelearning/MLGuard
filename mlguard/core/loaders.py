"""
Загрузка данных для аудита.

Сейчас поддерживаются CSV и Parquet. Архитектура рассчитана на расширение:
чтобы добавить новый источник (SQL, S3, Excel...), достаточно объявить
новую функцию с декоратором @register_loader — менять cli.py не нужно.
"""
from pathlib import Path
from typing import Callable

import click
import pandas as pd

_LOADERS: dict[str, Callable[[Path], pd.DataFrame]] = {}


def register_loader(*extensions: str):
    def wrapper(fn: Callable[[Path], pd.DataFrame]):
        for ext in extensions:
            _LOADERS[ext] = fn
        return fn
    return wrapper


def load_data(source: str) -> pd.DataFrame:
    path = Path(source)
    loader = _LOADERS.get(path.suffix.lower())
    if loader is None:
        supported = ", ".join(sorted(_LOADERS)) or "(нет зарегистрированных загрузчиков)"
        raise click.ClickException(
            f"Неподдерживаемый формат файла: '{path.suffix or path.name}'. "
            f"Поддерживаются: {supported}"
        )
    return loader(path)


@register_loader(".csv")
def _load_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@register_loader(".parquet")
def _load_parquet(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)
