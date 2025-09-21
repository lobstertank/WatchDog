#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Временный скрипт для запуска тестового бота с принудительной проверкой
"""

import sys
import os
import datetime
from holiday_checker_json import is_working_day, get_holiday_info

# Импортируем необходимые функции
from api_functions import (
    get_all_accounts,
    get_all_transactions_for_all_accounts,
    get_current_balances,
    analyze_all_accounts_balances
)
from telegram_functions import (
    send_telegram_message_wrapper,
    send_balance_analysis_report
)
from contacts import TEST_BOT_CONFIG

def force_check_and_notify():
    """Принудительно проверяет остатки и отправляет уведомления независимо от дня недели"""
    
    bot_token = TEST_BOT_CONFIG['bot_token']
    allowed_users = TEST_BOT_CONFIG['allowed_users']
    is_test = True
    
    print(f"🚀 Запуск ТЕСТОВОГО бота мониторинга остатков (ПРИНУДИТЕЛЬНЫЙ РЕЖИМ)...")
    print(f"📅 Принудительная проверка остатков (игнорируем выходной день)")
    
    # Получаем транзакции для всех счетов одним запросом
    accounts = get_all_accounts()
    account_ids = [account.get('id') for account in accounts]
    
    print(f"📊 Загружаем плановые транзакции для всех счетов одним запросом... {account_ids}")

    start_date = datetime.datetime.now().strftime("%Y-%m-%d")
    transactions_by_account = get_all_transactions_for_all_accounts(account_ids, start_date)
    
    # Получаем текущие остатки
    current_balances = get_current_balances(accounts)
    
    # Единый анализ всех счетов
    analysis_result = analyze_all_accounts_balances(transactions_by_account, accounts, current_balances)
    
    # Отправка единого уведомления
    send_balance_analysis_report(analysis_result, 
                               lambda chat_id, text: send_telegram_message_wrapper(bot_token, chat_id, text, is_test), 
                               allowed_users)
    
    print(f"✅ Проверка завершена")

if __name__ == "__main__":
    force_check_and_notify()
