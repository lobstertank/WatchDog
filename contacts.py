#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Настройки контактов для ботов Finolog. Секреты берутся из окружения.
"""

import os
from pathlib import Path
from typing import Optional


def _load_dotenv(path: Path) -> None:
    """Load key=value pairs from .env without внешних зависимостей."""
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


def _get_env(name: str, *, required: bool = False) -> Optional[str]:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        if required:
            raise RuntimeError(f"Не задана обязательная переменная окружения {name}")
        return None
    return value.strip()


def _get_int_list(name: str, *, required: bool = False) -> list[int]:
    raw_value = _get_env(name, required=required)
    if raw_value is None:
        return []
    result: list[int] = []
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
    if required and not result:
        raise RuntimeError(f"Переменная окружения {name} не может быть пустой")
    return result


MAIN_BOT_CONFIG = {
    "bot_token": _get_env("MAIN_BOT_TOKEN", required=True),
    "allowed_users": _get_int_list("MAIN_BOT_ALLOWED_USERS", required=True),
}

TEST_BOT_CONFIG = {
    "bot_token": _get_env("TEST_BOT_TOKEN", required=True),
    "allowed_users": _get_int_list("TEST_BOT_ALLOWED_USERS", required=True),
}
