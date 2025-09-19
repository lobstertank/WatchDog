#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Универсальный бот мониторинга Финолога
"""

import datetime
import os
from holiday_checker_json import is_working_day, get_holiday_info
from api_functions import (
    get_all_accounts,
    get_all_transactions_for_all_accounts, 
    calculate_daily_balances,
    get_current_balances,
    analyze_all_accounts_balances
)
from telegram_functions import (
    send_telegram_message,
    send_telegram_message_wrapper,
    send_positive_balance_report,
    send_balance_analysis_report
)


def check_and_notify(bot_token, allowed_users, is_test=False):
    """Проверяет остатки и отправляет уведомления только при наличии проблем и в рабочие дни"""
    
    # Проверяем, рабочий ли сегодня день
    today = datetime.date.today()
    if not is_working_day(today):
        holiday_info = get_holiday_info(today)
        if holiday_info:
            print(f"📅 Сегодня {holiday_info} - выходной, уведомления не отправляем")
        else:
            print(f"📅 Сегодня выходной день - уведомления не отправляем")
        return
    
    print(f"📅 Сегодня рабочий день - проверяем остатки")
    
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

def main(bot_token, allowed_users, is_test=False):
    """Основная функция"""
    bot_type = "ТЕСТОВОГО" if is_test else "ОСНОВНОГО"
    print(f"🚀 Запуск {bot_type} бота мониторинга остатков...")
    check_and_notify(bot_token, allowed_users, is_test)