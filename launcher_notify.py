#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher для основного бота мониторинга Финолога с принудительной отправкой уведомлений
"""

import datetime
from contacts import MAIN_BOT_CONFIG
from telegram_bot import main
from telegram_functions import send_telegram_message_wrapper

if __name__ == "__main__":
    # Отправляем уведомление о запуске
    for user_id in MAIN_BOT_CONFIG['allowed_users']:
        send_telegram_message_wrapper(
            MAIN_BOT_CONFIG['bot_token'],
            user_id,
            "🚀 Запущена принудительная проверка остатков. Результаты будут отправлены независимо от наличия проблем.",
            is_test=False
        )
    
    # Запускаем основной бот
    main(MAIN_BOT_CONFIG['bot_token'], MAIN_BOT_CONFIG['allowed_users'], is_test=False, force_check=True, always_notify=True)
