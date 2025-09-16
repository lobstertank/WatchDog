#!/usr/bin/env python3
"""
Проверка праздников на основе JSON файлов
Читает данные из holidays_YYYY.json
"""

import datetime
import json
import os

def load_holidays_json(year):
    """Загрузить данные о праздниках из JSON файла"""
    filename = f"holidays_{year}.json"
    
    if not os.path.exists(filename):
        print(f"⚠️ Файл {filename} не найден")
        return None
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"✅ Загружен календарь {year} из {filename}")
        return data
        
    except Exception as e:
        print(f"❌ Ошибка загрузки {filename}: {e}")
        return None

def is_working_day(date):
    """Проверка, является ли день рабочим"""
    year = date.year
    
    # Загружаем данные о праздниках
    holidays_data = load_holidays_json(year)
    
    if not holidays_data:
        # Fallback: базовая логика
        print(f"⚠️ Используем базовую логику для {year} года")
        return not (date.weekday() >= 5)  # Только выходные
    
    # Проверяем рабочие дни (переносы)
    working_days = holidays_data.get('working_days', [])
    date_str = date.strftime('%Y-%m-%d')
    
    if date_str in working_days:
        return True
    
    # Проверяем праздники
    holidays = holidays_data.get('holidays', [])
    for holiday in holidays:
        if holiday['date'] == date_str:
            return False
    
    # Проверяем обычные выходные
    if date.weekday() >= 5:
        return False
    
    return True

def get_holiday_info(date):
    """Получить информацию о празднике"""
    year = date.year
    holidays_data = load_holidays_json(year)
    
    if not holidays_data:
        return None
    
    date_str = date.strftime('%Y-%m-%d')
    
    # Проверяем праздники
    holidays = holidays_data.get('holidays', [])
    for holiday in holidays:
        if holiday['date'] == date_str:
            return holiday['name']
    
    # Проверяем рабочие дни (переносы)
    working_days = holidays_data.get('working_days', [])
    if date_str in working_days:
        transfers = holidays_data.get('transfers', [])
        for transfer in transfers:
            if transfer['to'] == date_str:
                return f"Рабочий день: {transfer['description']}"
    
    return None

def test_holiday_system():
    """Тестирование системы праздников"""
    print("🔍 Тестирование системы праздников на основе JSON")
    print("="*60)
    
    # Тестируем ключевые даты
    test_dates = [
        # 2025
        datetime.date(2025, 1, 1),   # Новый год
        datetime.date(2025, 1, 9),   # Первый рабочий день
        datetime.date(2025, 5, 2),   # Перенос (рабочий день)
        datetime.date(2025, 5, 9),   # День Победы
        datetime.date(2025, 12, 31), # Перенос (рабочий день)
        
        # 2026
        datetime.date(2026, 1, 1),   # Новый год
        datetime.date(2026, 1, 8),   # Рабочий день
        datetime.date(2026, 1, 9),   # Перенос (рабочий день)
    ]
    
    for date in test_dates:
        is_work = is_working_day(date)
        status = "РАБОЧИЙ" if is_work else "ВЫХОДНОЙ"
        weekday = date.strftime('%A')
        info = get_holiday_info(date)
        
        if info:
            print(f"{date.strftime('%d.%m.%Y')} ({weekday}) - {status} - {info}")
        else:
            print(f"{date.strftime('%d.%m.%Y')} ({weekday}) - {status}")

def main():
    """Основная функция для проверки"""
    today = datetime.date.today()
    
    if is_working_day(today):
        print("WORKING_DAY")
        return 0
    else:
        print("HOLIDAY")
        return 1

if __name__ == "__main__":
    if len(os.sys.argv) > 1 and os.sys.argv[1] == "test":
        test_holiday_system()
    else:
        main()

