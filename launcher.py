#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Launcher для основного бота мониторинга Финолога
"""

from contacts import MAIN_BOT_CONFIG
from telegram_bot import main

if __name__ == "__main__":
    main(MAIN_BOT_CONFIG['bot_token'], MAIN_BOT_CONFIG['allowed_users'], is_test=False)
