#!/usr/bin/env python3
"""
Минимальный обновлятор календаря праздников
Только: обращение к КонсультантПлюс, парсинг, сохранение в JSON
"""

import datetime
import urllib.request
import json
import re

def get_consultant_html(year):
    """Получить HTML страницу календаря с КонсультантПлюс"""
    try:
        url = f"https://www.consultant.ru/law/ref/calendar/proizvodstvennye/{year}/"
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'WatchDog Holiday Updater')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            if response.getcode() == 200:
                html_content = response.read().decode('utf-8')
                print(f"✅ КонсультантПлюс {year}: HTML получен ({len(html_content)} символов)")
                return html_content
            else:
                print(f"❌ КонсультантПлюс {year}: HTTP {response.getcode()}")
                return None
    except Exception as e:
        print(f"❌ Ошибка получения HTML {year}: {e}")
        return None

def parse_consultant_html(html_content, year):
    """Парсинг HTML страницы КонсультантПлюс для извлечения праздников"""
    holidays = []
    working_days = []
    
    # Ищем переносы выходных дней
    transfer_pattern = r'с\s+(\w+)\s+(\d+)\s+(\w+)\s+на\s+(\w+)\s+(\d+)\s+(\w+)'
    transfers = re.findall(transfer_pattern, html_content)
    
    # Обрабатываем переносы
    for transfer in transfers:
        try:
            from_day = int(transfer[1])
            from_month = get_month_number(transfer[2])
            to_day = int(transfer[4])
            to_month = get_month_number(transfer[5])
            
            # Добавляем рабочий день (куда перенесли)
            to_date = datetime.date(year, to_month, to_day)
            working_days.append(to_date.strftime('%Y-%m-%d'))
            
            print(f"📅 Перенос: {from_day}.{from_month} → {to_day}.{to_month}")
        except:
            continue
    
    # Ищем праздники в тексте
    holiday_patterns = [
        (r'(\d+)\s+января.*?Новый год', 1, "Новый год"),
        (r'(\d+)\s+января.*?Рождество', 1, "Рождество Христово"),
        (r'(\d+)\s+февраля.*?защитника Отечества', 2, "День защитника Отечества"),
        (r'(\d+)\s+марта.*?женский день', 3, "Международный женский день"),
        (r'(\d+)\s+мая.*?Весны и Труда', 5, "Праздник Весны и Труда"),
        (r'(\d+)\s+мая.*?Победы', 5, "День Победы"),
        (r'(\d+)\s+июня.*?России', 6, "День России"),
        (r'(\d+)\s+ноября.*?народного единства', 11, "День народного единства"),
    ]
    
    # Извлекаем праздники
    for pattern, month, name in holiday_patterns:
        matches = re.findall(pattern, html_content, re.IGNORECASE)
        for match in matches:
            try:
                day = int(match)
                date_obj = datetime.date(year, month, day)
                holidays.append({
                    'date': date_obj.strftime('%Y-%m-%d'),
                    'name': name
                })
                print(f"🎉 Найден праздник: {day}.{month} - {name}")
            except ValueError:
                continue
    
    # Добавляем новогодние каникулы (обычно 1-8 января)
    for day in range(1, 9):
        try:
            date_obj = datetime.date(year, 1, day)
            if day == 1:
                name = "Новый год"
            elif day == 7:
                name = "Рождество Христово"
            else:
                name = "Новогодние каникулы"
            
            holidays.append({
                'date': date_obj.strftime('%Y-%m-%d'),
                'name': name
            })
        except ValueError:
            continue
    
    return {
        "year": year,
        "source": "КонсультантПлюс (парсинг HTML)",
        "last_updated": datetime.datetime.now().isoformat(),
        "holidays": holidays,
        "working_days": working_days
    }

def get_month_number(month_name):
    """Получить номер месяца по названию"""
    months = {
        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
    }
    return months.get(month_name.lower(), 1)

def save_holidays_json(year, holidays_data):
    """Сохранить данные о праздниках в JSON файл"""
    filename = f"holidays_{year}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(holidays_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Сохранен: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Ошибка сохранения {filename}: {e}")
        return None

def update_holidays_for_year(year):
    """Обновить календарь праздников для года"""
    print(f"🔄 Обновление {year}...")
    
    # Получаем HTML с КонсультантПлюс
    html_content = get_consultant_html(year)
    if not html_content:
        print(f"❌ Не удалось получить данные для {year}")
        return None
    
    # Парсим HTML
    holidays_data = parse_consultant_html(html_content, year)
    if not holidays_data or not holidays_data.get('holidays'):
        print(f"❌ Не удалось распарсить данные для {year}")
        return None
    
    print(f"📊 Найдено {len(holidays_data['holidays'])} праздников, {len(holidays_data['working_days'])} переносов")
    
    # Сохраняем в JSON
    filename = save_holidays_json(year, holidays_data)
    return filename

def main():
    """Основная функция обновления"""
    print("🔄 Обновление календаря праздников")
    print("="*50)
    
    # Обновляем календари
    years_to_update = [2025, 2026]
    updated_years = []
    
    for year in years_to_update:
        try:
            filename = update_holidays_for_year(year)
            if filename:
                updated_years.append(year)
        except Exception as e:
            print(f"❌ Ошибка {year}: {e}")
    
    print(f"✅ Завершено: {updated_years}")

if __name__ == "__main__":
    main()
