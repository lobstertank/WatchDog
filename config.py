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

# Настройки Telegram бота
TELEGRAM_CONFIG = {
    'bot_token': '8363091905:AAE8n7P1PwuQrmQRIGYPSLmgi9ceNgIY9lE',
    'allowed_users': [
        13553737,  # Ваш ID
	2095138167, #Лена
    ]
}
