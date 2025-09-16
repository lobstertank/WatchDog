import urllib.request
import urllib.parse
import json
import io
import sys
import datetime
import os
from forecast import forecast
from config import TELEGRAM_CONFIG
from holiday_checker_json import is_working_day, get_holiday_info

# Настройки из config.py
BOT_TOKEN = TELEGRAM_CONFIG['bot_token']
ALLOWED_USERS = TELEGRAM_CONFIG['allowed_users']


def send_telegram_message(chat_id, text):
    """Отправляет сообщение в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
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

def send_negative_balance_report():
    """Отправляет отчет об отрицательных остатках в табличном формате"""
    
    # Перехватываем вывод функции в строку
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    try:
        # Запускаем анализ
        forecast()
        report = buffer.getvalue()
    finally:
        sys.stdout = old_stdout
    
    # Форматируем отчет в табличном виде
    if "Минусов нет" in report:
        message = "✅ <b>Анализ остатков</b>\n\n🎉 <b>Минусов нет!</b>\n\nВсе счета в порядке."
    else:
        # Парсим отчет и форматируем в таблицу
        lines = report.strip().split('\n')
        message = "⚠️ <b>Анализ остатков</b>\n\n"
        message += "🔴 <b>Обнаружены отрицательные остатки:</b>\n\n"
        
        for line in lines:
            if ":" in line and "минусы в месяцах" in line:
                # Форматируем строку: "Счет: минусы в месяцах: 09-2025, 10-2025"
                parts = line.split(": минусы в месяцах: ")
                if len(parts) == 2:
                    account_name = parts[0].strip()
                    months = parts[1].strip()
                    
                    # Создаем табличную строку
                    message += f"📊 <b>{account_name}</b>\n"
                    message += f"📅 Месяцы: <code>{months}</code>\n\n"
    
    # Отправляем отчет всем разрешенным пользователям
    for user_id in ALLOWED_USERS:
        try:
            success = send_telegram_message(user_id, message)
            if success:
                print(f"Отправлено пользователю {user_id}")
            else:
                print(f"Ошибка отправки пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка отправки пользователю {user_id}: {e}")

def send_positive_balance_report():
    """Отправляет уведомление о том, что минусов нет (только в 9 утра)"""
    
    # Используем UTC+3 для Москвы (без перехода на летнее время)
    current_time_utc = datetime.datetime.utcnow()
    moscow_time = current_time_utc + datetime.timedelta(hours=3)
    
    message = f"🌅 <b>Утренняя проверка остатков</b>\n\n"
    message += f"⏰ Время: {moscow_time.strftime('%H:%M')} МСК\n\n"
    message += "✅ <b>Все счета в порядке!</b>\n\n"
    message += "🎉 <b>Отрицательных остатков не обнаружено</b>\n\n"
    message += "📊 Анализ выполнен успешно"
    
    # Отправляем отчет всем разрешенным пользователям
    for user_id in ALLOWED_USERS:
        try:
            success = send_telegram_message(user_id, message)
            if success:
                print(f"Отправлено утреннее уведомление пользователю {user_id}")
            else:
                print(f"Ошибка отправки утреннего уведомления пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка отправки утреннего уведомления пользователю {user_id}: {e}")

def check_and_notify():
    """Проверяет остатки и отправляет уведомления только при наличии минусов и в рабочие дни"""
    
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
    
    # Перехватываем вывод функции в строку
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    try:
        # Запускаем анализ
        forecast()
        report = buffer.getvalue()
    finally:
        sys.stdout = old_stdout
    
    # Проверяем, есть ли минусы
    if "Минусов нет" not in report:
        # Есть минусы - отправляем уведомление
        send_negative_balance_report()
        print("Отправлено уведомление о минусах")
    else:
        # Минусов нет - проверяем время (только утром в 9:00 по Москве)
        # Используем UTC+3 для Москвы (без перехода на летнее время)
        current_time_utc = datetime.datetime.utcnow()
        moscow_time = current_time_utc + datetime.timedelta(hours=3)
        
        if moscow_time.hour == 9 and moscow_time.minute < 10:  # Только в 9 утра (с запасом на 10 минут)
            # Отправляем уведомление "все хорошо" в 9 утра
            send_positive_balance_report()
            print("Отправлено уведомление о том, что минусов нет (9 утра по Москве)")
        else:
            print(f"Минусов нет - уведомление не отправлено (время: {moscow_time.strftime('%H:%M')} МСК)")

def main():
    """Основная функция"""
    print("Запуск проверки остатков...")
    check_and_notify()

if __name__ == "__main__":
    main()
