#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher для тестового бота мониторинга Финолога с принудительной отправкой
"""

from contacts import TEST_BOT_CONFIG
from telegram_bot import main

if __name__ == "__main__":
    main(TEST_BOT_CONFIG['bot_token'], TEST_BOT_CONFIG['allowed_users'], is_test=True, force_check=True)
