#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Функции для работы с Telegram ботом
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta

def send_telegram_message(bot_token, chat_id, text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    data = urllib.parse.urlencode(data).encode('utf-8')
    
    try:
        with urllib.request.urlopen(url, data) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('ok', False)
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")
        return False

def send_telegram_message_wrapper(bot_token, chat_id, text, is_test=False):
    """Обертка для отправки сообщения в Telegram с поддержкой тестового режима"""
    if is_test:
        text = "🧪 ТЕСТ: " + text
    return send_telegram_message(bot_token, chat_id, text)

def send_positive_balance_report(send_telegram_message_func, allowed_users):
    """Отправляет уведомление о том, что минусов нет (только в 9 утра)"""
    
    # Используем UTC+3 для Москвы (без перехода на летнее время)
    current_time_utc = datetime.utcnow()
    moscow_time = current_time_utc + timedelta(hours=3)
    
    message = f"🌅 <b>Утренняя проверка остатков</b>\n\n"
    message += f"⏰ Время: {moscow_time.strftime('%H:%M')} МСК\n\n"
    message += "✅ <b>Все счета в порядке!</b>\n\n"
    message += "🎉 <b>Отрицательных остатков не обнаружено</b>\n\n"
    message += "📊 Анализ выполнен успешно"
    
    # Отправляем отчет всем разрешенным пользователям
    for user_id in allowed_users:
        try:
            success = send_telegram_message_func(user_id, message)
            if success:
                print(f"Отправлено утреннее уведомление пользователю {user_id}")
            else:
                print(f"Ошибка отправки утреннего уведомления пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка отправки утреннего уведомления пользователю {user_id}: {e}")

def send_balance_analysis_report(analysis_result, send_telegram_func, allowed_users):
    """
    Отправляет единое уведомление с анализом всех счетов
    
    Args:
        analysis_result: результат analyze_all_accounts_balances()
        send_telegram_func: функция отправки сообщений
        allowed_users: список разрешенных пользователей
    """
    negative_balances = analysis_result['negative_balances']
    threatening_balances = analysis_result['threatening_balances']
    accounts_info = analysis_result['accounts_info']
    
    # Проверяем, есть ли проблемы
    if not negative_balances and not threatening_balances:
        # Проблем нет - отправляем уведомление только в 9 утра
        current_time_utc = datetime.utcnow()
        moscow_time = current_time_utc + timedelta(hours=3)
        
        if moscow_time.hour == 9 and moscow_time.minute < 10:
            send_positive_balance_report(send_telegram_func, allowed_users)
            print("Отправлено уведомление о том, что проблем нет (9 утра по Москве)")
        else:
            print(f"Проблем нет - уведомление не отправлено (время: {moscow_time.strftime('%H:%M')} МСК)")
        return
    
    # Формируем сообщение о проблемах
    message = "⚠️ <b>Анализ остатков счетов</b>\n\n"
    
    # Добавляем информацию об отрицательных остатках
    if negative_balances:
        message += "🔴 <b>ОТРИЦАТЕЛЬНЫЕ ОСТАТКИ:</b>\n\n"
        
        for account_id, negative_days in negative_balances.items():
            account_name = accounts_info[account_id]['name']
            current_balance = accounts_info[account_id]['current_balance']
            
            message += f"📊 <b>{account_name}</b>\n"
            message += f"📅 Отрицательные дни: {len(negative_days)}\n"
            
            # Показываем первые 5 дней для краткости
            for i, (date, balance) in enumerate(negative_days[:5]):
                message += f"   • {date}: {balance:>12,.0f} р.\n"
            
            if len(negative_days) > 5:
                message += f"   • ... и еще {len(negative_days) - 5} дней\n"
            
            message += "\n"
    
    # Добавляем информацию об угрожающих остатках
    if threatening_balances:
        message += "🟡 <b>УГРОЖАЮЩИЕ ОСТАТКИ:</b>\n\n"
        
        for account_id, threatening_days in threatening_balances.items():
            account_name = accounts_info[account_id]['name']
            current_balance = accounts_info[account_id]['current_balance']
            
            message += f"📊 <b>{account_name}</b>\n"
            message += f"📅 Угрожающие дни: {len(threatening_days)}\n"
            
            # Показываем первые 5 дней для краткости
            for i, (date, balance) in enumerate(threatening_days[:5]):
                message += f"   • {date}: {balance:>12,.0f} р.\n"
            
            if len(threatening_days) > 5:
                message += f"   • ... и еще {len(threatening_days) - 5} дней\n"
            
            message += "\n"
    
    message += "⚠️ <b>Требуется внимание!</b>"
    
    # Отправляем уведомление всем разрешенным пользователям
    for user_id in allowed_users:
        try:
            success = send_telegram_func(user_id, message)
            if success:
                print(f"Отправлено уведомление об анализе остатков пользователю {user_id}")
            else:
                print(f"Ошибка отправки уведомления об анализе остатков пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка отправки уведомления об анализе остатков пользователю {user_id}: {e}")
