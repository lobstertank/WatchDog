#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конфигурационный файл для мониторинга Финолога
Замените значения на ваши реальные данные
"""

# API настройки Финолога
FINOLOG_CONFIG = {
    'api_key': 'GXqFgOgsHOoTXbKDd9ff3dafa24ae865c48291100fe7cf82J14wlR8WCucDv4Gu',  # Ваш API ключ от Финолога
    'biz_id': '53850',    # Ваш Biz ID
    'base_url': 'https://api.finolog.ru/v1'
}

# Настройки мониторинга
MONITORING_CONFIG = {
    'months_ahead': 12,        # Количество месяцев для прогноза
}

# Настройки проверки угрожающих балансов
THREATENING_CONFIG = {
    'account_ids': [190104],   # ID счетов для проверки угрожающих балансов (Модуль RUB)
    'threshold': 100000,       # Порог угрожающего баланса в рублях
    'days_ahead': 356,         # Количество дней для анализа
}

