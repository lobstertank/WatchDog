#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурационный файл для мониторинга Финолога.
Секреты считываются из переменных окружения или .env файла.
"""

import os
from pathlib import Path


def _load_dotenv(path: Path) -> None:
    """Load key=value pairs from a local .env file without extra deps."""
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())
    except Exception as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Не удалось прочитать файл окружения {path}") from exc


_base_dir = Path(__file__).resolve().parent
_env_file = _base_dir / ".env"
if _env_file.exists():
    _load_dotenv(_env_file)


def _get_env(name: str, *, default=None, required: bool = False) -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        if required and default is None:
            raise RuntimeError(f"Не задана обязательная переменная окружения {name}")
        return default
    return value.strip()


def _get_int(name: str, *, default=None, required: bool = False) -> int:
    raw_value = _get_env(name, default=None, required=required)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Переменная окружения {name} должна быть целым числом") from exc


def _get_int_list(name: str, *, default=None) -> list[int]:
    raw_value = _get_env(name, default=None, required=False)
    if raw_value is None:
        return default if default is not None else []
    result = []
    for item in raw_value.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            result.append(int(item))
        except ValueError as exc:
            raise RuntimeError(
                f"Переменная окружения {name} должна содержать список целых через запятую"
            ) from exc
    return result


FINOLOG_CONFIG = {
    "api_key": _get_env("FINOLOG_API_KEY", required=True),
    "biz_id": _get_env("FINOLOG_BIZ_ID", required=True),
    "base_url": _get_env("FINOLOG_BASE_URL", default="https://api.finolog.ru/v1"),
}

THREATENING_CONFIG = {
    "account_ids": _get_int_list("THREATENING_ACCOUNT_IDS"),
    "threshold": _get_int("THREATENING_THRESHOLD", default=100_000),
    "days_ahead": _get_int("THREATENING_DAYS_AHEAD", default=356),
}
