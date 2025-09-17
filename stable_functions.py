import urllib.request
import urllib.parse
import json
import time
from datetime import datetime, timedelta
from config import FINOLOG_CONFIG, THREATENING_CONFIG

def make_request(url):
    """Выполнить API запрос к Finolog с паузой 3 секунды"""
    # Пауза 3 секунды перед каждым запросом
    #time.sleep(1)
    
    try:
        req = urllib.request.Request(url)
        req.add_header('Api-Token', FINOLOG_CONFIG['api_key'])
        
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Ошибка API запроса: {e}")
        return None

def get_current_balance(account_id):
    """
    Получить текущий баланс счета.
    ЭТА ФУНКЦИЯ НЕ ДОЛЖНА ИЗМЕНЯТЬСЯ - она работает правильно!
    """
    url = f"{FINOLOG_CONFIG['base_url']}/biz/{FINOLOG_CONFIG['biz_id']}/account/{account_id}"
    account_details = make_request(url)
    if account_details and 'summary' in account_details and account_details['summary']:
        if isinstance(account_details['summary'], list):
            return account_details['summary'][0].get('balance', 0)
        else:
            return account_details['summary'].get('balance', 0)
    return 0

def get_planned_transactions_for_month(account_id, year, month):
    """
    Получить все плановые транзакции за указанный месяц.
    Учитывает только неразбитые операции и суммирующие операции (родительские).
    Исключает части разбитых операций.
    
    Args:
        account_id: ID счета
        year: год (например, 2025)
        month: месяц (1-12)
    
    Returns:
        list: список плановых транзакций за месяц
    """
    # Определяем диапазон дат для месяца
    start_date = f"{year}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1}-01-01"
    else:
        end_date = f"{year}-{month+1:02d}-01"
    
    # Добавляем параметры для получения плановых операций и суммирующих операций
    url = f"{FINOLOG_CONFIG['base_url']}/biz/{FINOLOG_CONFIG['biz_id']}/transaction?account_ids={account_id}&date={start_date}%2C{end_date}&status=planned&with_splitted=false&without_closed_accounts=false"
    
    all_transactions = make_request(url)
    
    # Фильтруем транзакции по типу операции на клиентской стороне
    # (статус 'planned' уже отфильтрован на сервере)
    if not all_transactions:
        return []
    
    filtered_transactions = []
    for tx in all_transactions:
        is_splitted = tx.get('is_splitted', False)
        split_id = tx.get('split_id')
        
        # Включаем только:
        # 1. Неразбитые операции (split_id = null, is_splitted = false)
        # 2. Суммирующие операции (is_splitted = true)
        # Исключаем части разбитых операций (split_id ≠ null, is_splitted = false)
        if (split_id is None and not is_splitted) or is_splitted:
            filtered_transactions.append(tx)
    
    return filtered_transactions

def get_all_transactions_for_year(account_id, start_date):
    """Получить все транзакции на год вперед от заданной даты (передается как параметр) с пагинацией"""
    # Диапазон дат на год вперед от указанной даты
    # start_date может быть в формате "2025-09-14" или "2025"
    if len(str(start_date)) == 4:  # Если передан только год
        start_date = f"{start_date}-01-01"
        end_date = f"{int(start_date[:4])+1}-01-01"
    else:  # Если передана точная дата
        from datetime import datetime, timedelta
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        start_dt_in_past= start_dt - timedelta(days=365)
        start_date_in_past = start_dt_in_past.strftime("%Y-%m-%d")
        end_dt = start_dt + timedelta(days=365)
        end_date = end_dt.strftime("%Y-%m-%d")
    
    all_transactions = []
    page = 1
    pagesize = 200  # Максимальный размер страницы
    
    while True:
        # Запрос транзакций с пагинацией (используем правильный формат как в get_planned_transactions_for_month)
        url = f"{FINOLOG_CONFIG['base_url']}/biz/{FINOLOG_CONFIG['biz_id']}/transaction?account_ids={account_id}&date={start_date_in_past}%2C{end_date}&status=planned&with_splitted=false&without_closed_accounts=false&page={page}&pagesize={pagesize}"
        
        page_transactions = make_request(url)
        
        if not page_transactions:
            break
            
        all_transactions.extend(page_transactions)
        
        # Если получили меньше транзакций чем pagesize, значит это последняя страница
        if len(page_transactions) < pagesize:
            break
            
        page += 1
    
    if not all_transactions:
        return []
    
    # Фильтруем транзакции по типу операции (статус 'planned' уже отфильтрован на сервере)
    filtered_transactions = []
    for tx in all_transactions:
        is_splitted = tx.get('is_splitted', False)
        split_id = tx.get('split_id')
        
        # Включаем только:
        # 1. Неразбитые операции (split_id = null, is_splitted = false)
        # 2. Суммирующие операции (is_splitted = true)
        # Исключаем части разбитых операций (split_id ≠ null, is_splitted = false)
        if (split_id is None and not is_splitted) or is_splitted:
            filtered_transactions.append(tx)
    
    return filtered_transactions

def get_all_transactions_for_all_accounts(account_ids, start_date):
    """Получить все транзакции для нескольких счетов одним запросом"""
    # Диапазон дат на год вперед от указанной даты
    if len(str(start_date)) == 4:  # Если передан только год
        start_date = f"{start_date}-01-01"
        end_date = f"{int(start_date[:4])+1}-01-01"
    else:  # Если передана точная дата
        from datetime import datetime, timedelta
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        start_dt_in_past = start_dt - timedelta(days=365)
        start_date_in_past = start_dt_in_past.strftime("%Y-%m-%d")
        end_dt = start_dt + timedelta(days=365)
        end_date = end_dt.strftime("%Y-%m-%d")
    
    # Объединяем ID счетов через запятую
    account_ids_str = ','.join(map(str, account_ids))
    
    all_transactions = []
    page = 1
    pagesize = 200  # Максимальный размер страницы
    
    while True:
        # Запрос транзакций для всех счетов одним запросом
        url = f"{FINOLOG_CONFIG['base_url']}/biz/{FINOLOG_CONFIG['biz_id']}/transaction?account_ids={account_ids_str}&date={start_date_in_past}%2C{end_date}&status=planned&with_splitted=false&without_closed_accounts=false&page={page}&pagesize={pagesize}"
        
        page_transactions = make_request(url)
        
        if not page_transactions:
            break
            
        all_transactions.extend(page_transactions)
        
        # Если получили меньше транзакций чем pagesize, значит это последняя страница
        if len(page_transactions) < pagesize:
            break
            
        page += 1
    
    if not all_transactions:
        return {}
    
    # Фильтруем транзакции по типу операции
    filtered_transactions = []
    for tx in all_transactions:
        is_splitted = tx.get('is_splitted', False)
        split_id = tx.get('split_id')
        
        # Включаем только:
        # 1. Неразбитые операции (split_id = null, is_splitted = false)
        # 2. Суммирующие операции (is_splitted = true)
        # Исключаем части разбитых операций (split_id ≠ null, is_splitted = false)
        if (split_id is None and not is_splitted) or is_splitted:
            filtered_transactions.append(tx)
    
    # Группируем транзакции по счетам
    transactions_by_account = {}
    for tx in filtered_transactions:
        account_id = tx.get('account_id')
        if account_id not in transactions_by_account:
            transactions_by_account[account_id] = []
        transactions_by_account[account_id].append(tx)
    
    return transactions_by_account

def filter_transactions_by_month(transactions, year, month):
    """Выделить транзакции за конкретный месяц из списка транзакций за год"""
    from datetime import datetime
    
    filtered_transactions = []
    
    # Вычисляем текущую дату на ходу
    current_date = datetime.now().strftime("%Y-%m-%d")
    target_month = f"{year}-{month:02d}"
    current_month = current_date[:7]  # YYYY-MM
    
    for tx in transactions:
        tx_date = tx.get('date', '')
        is_splitted = tx.get('is_splitted', False)
        split_id = tx.get('split_id')
        
        # Логика фильтрации:
        # 1. Если целевой месяц в прошлом или текущем - включаем все плановые операции до этого месяца
        # 2. Если целевой месяц в будущем - включаем только операции за этот месяц
        if target_month <= current_month:
            # Для прошлых/текущих месяцев - включаем все операции до этого месяца включительно
            if tx_date[:7] <= target_month:
                pass  # Включаем
            else:
                continue  # Пропускаем
        else:
            # Для будущих месяцев - только операции за конкретный месяц
            if not tx_date.startswith(f"{year}-{month:02d}-"):
                continue
            
        # Включаем только:
        # 1. Неразбитые операции (split_id = null, is_splitted = false)
        # 2. Суммирующие операции (is_splitted = true)
        # Исключаем части разбитых операций (split_id ≠ null, is_splitted = false)
        if (split_id is None and not is_splitted) or is_splitted:
            filtered_transactions.append(tx)
    
    return filtered_transactions

def get_all_accounts():
    """Получить список всех счетов"""
    url = f"{FINOLOG_CONFIG['base_url']}/biz/{FINOLOG_CONFIG['biz_id']}/account"
    return make_request(url)

def get_current_balances(accounts):
    """Получить текущие остатки по списку счетов"""
    balances = {}
    
    for account in accounts:
        account_id = account.get('id')
        account_name = account.get('name', 'Без названия')
        balance = get_current_balance(account_id)
        balances[account_id] = {
            'name': account_name,
            'balance': balance
        }
    
    return balances

def send_negative_balance_report(transactions_by_account, send_telegram_message, allowed_users, forecast_func):
    """Отправляет отчет об отрицательных остатках в табличном формате"""
    import io
    import sys
    
    # Перехватываем вывод функции в строку
    old_stdout = sys.stdout
    sys.stdout = buffer = io.StringIO()
    
    try:
        # Запускаем анализ (передаем транзакции)
        forecast_func(transactions_by_account)
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
    for user_id in allowed_users:
        try:
            success = send_telegram_message(user_id, message)
            if success:
                print(f"Отправлено пользователю {user_id}")
            else:
                print(f"Ошибка отправки пользователю {user_id}")
        except Exception as e:
            print(f"Ошибка отправки пользователю {user_id}: {e}")

def calculate_daily_balances(current_balance, planned_transactions, start_date, days_ahead=365):
    """
    Рассчитать ежедневные остатки на указанное количество дней вперед.
    Использует уже загруженные данные без дополнительных API вызовов.
    
    Args:
        current_balance: текущий остаток счета
        planned_transactions: список плановых транзакций (уже полученных другой функцией)
        start_date: начальная дата в формате "YYYY-MM-DD"
        days_ahead: количество дней для расчета (по умолчанию 365)
    
    Returns:
        dict: словарь с датами и остатками {date: balance}
    """
    from datetime import datetime, timedelta
    
    # Создаем словарь для группировки транзакций по датам
    transactions_by_date = {}
    for tx in planned_transactions:
        tx_date = tx.get('date', '')
        if tx_date:
            if tx_date not in transactions_by_date:
                transactions_by_date[tx_date] = []
            transactions_by_date[tx_date].append(tx)
    
    # Рассчитываем остатки по дням
    daily_balances = {}
    running_balance = current_balance
    
    # Начальная дата
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    
    for day_offset in range(days_ahead + 1):
        current_dt = start_dt + timedelta(days=day_offset)
        current_date_str = current_dt.strftime("%Y-%m-%d 00:00:00")
        
        # Добавляем транзакции за этот день
        if current_date_str in transactions_by_date:
            for tx in transactions_by_date[current_date_str]:
                value = tx.get('value', 0)
                tx_type = tx.get('type', '')
                if tx_type == 'in':
                    running_balance += value
                elif tx_type == 'out':
                    running_balance += value  # value уже отрицательный для исходящих
        
        daily_balances[current_date_str] = running_balance
    
    return daily_balances

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

def check_daily_balances_for_threats(account_id, planned_transactions):
    """Проверяет ежедневные остатки указанного счета на угрожающие балансы"""
    
    print(f"🔍 Проверяем ежедневные остатки счета ID: {account_id}...")
    
    try:
        # Получаем информацию о счете
        accounts = get_all_accounts()
        if not accounts:
            print("Ошибка: не удалось получить список счетов")
            return None, None, None
        
        account_name = None
        for account in accounts:
            if account.get('id') == account_id:
                account_name = account.get('name', 'Без названия')
                break
        
        if not account_name:
            print(f"Ошибка: счет с ID {account_id} не найден")
            return None, None, None
        
        # Получаем текущий остаток
        current_balance = get_current_balance(account_id)
        start_date = datetime.now().strftime("%Y-%m-%d")
        
        # Рассчитываем ежедневные остатки на 356 дней вперед
        daily_balances = calculate_daily_balances(
            current_balance=current_balance,
            planned_transactions=planned_transactions,
            start_date=start_date,
            days_ahead=356
        )
        
        # Проверяем на угрожающие балансы (меньше 100,000 руб.)
        threatening_dates = [(date, balance) for date, balance in daily_balances.items() if balance < 100000]
        
        if threatening_dates:
            print(f"⚠️ Обнаружены угрожающие балансы в {account_name}: {len(threatening_dates)} дней")
            return threatening_dates, account_name, current_balance
        else:
            print(f"✅ Угрожающих балансов в {account_name} не обнаружено (проверено {len(daily_balances)} дней)")
            return None, account_name, current_balance
            
    except Exception as e:
        print(f"Ошибка при проверке ежедневных остатков: {e}")
        return None, None, None

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

def analyze_all_accounts_balances(transactions_by_account, accounts, current_balances):
    """
    Анализирует все счета на отрицательные и угрожающие остатки
    
    Args:
        transactions_by_account: словарь транзакций по счетам
        accounts: список счетов
        current_balances: словарь текущих остатков по счетам
    
    Returns:
        dict: {
            'negative_balances': {account_id: [(date, balance), ...]},
            'threatening_balances': {account_id: [(date, balance), ...]},
            'accounts_info': {account_id: {'name': str, 'current_balance': float}}
        }
    """
    print("🔍 Анализируем все счета на отрицательные и угрожающие остатки...")
    
    if not accounts:
        print("Ошибка: список счетов пуст")
        return {'negative_balances': {}, 'threatening_balances': {}, 'accounts_info': {}}
    
    # Текущая дата
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Настройки из конфига
    threatening_account_ids = THREATENING_CONFIG['account_ids']
    threatening_threshold = THREATENING_CONFIG['threshold']
    days_ahead = THREATENING_CONFIG['days_ahead']
    
    # Результаты анализа
    negative_balances = {}
    threatening_balances = {}
    accounts_info = {}
    
    # Анализ для каждого счета
    for account in accounts:
        account_id = account.get('id')
        account_name = account.get('name', 'Без названия')
        
        # Текущий остаток
        current_balance = current_balances[account_id]['balance']
        accounts_info[account_id] = {
            'name': account_name,
            'current_balance': current_balance
        }
        
        # Получаем транзакции 
        account_id_int = int(account_id)
        if transactions_by_account and account_id_int in transactions_by_account:
            year_transactions = transactions_by_account[account_id_int]
        else:
            # По этому счету не было движений - используем пустой список
            year_transactions = []
        
        # Рассчитываем ежедневные остатки
        daily_balances = calculate_daily_balances(
            current_balance=current_balance,
            planned_transactions=year_transactions,
            start_date=current_date,
            days_ahead=days_ahead
        )
        
        # Ищем отрицательные дни (balance < 0)
        negative_days = []
        for date_str, balance in daily_balances.items():
            if balance < 0:
                # Форматируем дату для вывода
                date_obj = datetime.strptime(date_str, "%Y-%m-%d 00:00:00")
                formatted_date = date_obj.strftime("%Y-%m-%d")
                negative_days.append((formatted_date, balance))
        
        if negative_days:
            negative_balances[account_id] = negative_days
            print(f"⚠️ Найдены отрицательные остатки в {account_name}: {len(negative_days)} дней")
        
        # Ищем угрожающие дни (0 < balance < threshold) для определенных счетов
        if account_id in threatening_account_ids:
            threatening_days = []
            for date_str, balance in daily_balances.items():
                if 0 < balance < threatening_threshold:
                    # Форматируем дату для вывода
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d 00:00:00")
                    formatted_date = date_obj.strftime("%Y-%m-%d")
                    threatening_days.append((formatted_date, balance))
            
            if threatening_days:
                threatening_balances[account_id] = threatening_days
                print(f"⚠️ Найдены угрожающие остатки в {account_name}: {len(threatening_days)} дней")
    
    print(f"✅ Анализ завершен: {len(negative_balances)} счетов с отрицательными остатками, {len(threatening_balances)} счетов с угрожающими остатками")
    
    return {
        'negative_balances': negative_balances,
        'threatening_balances': threatening_balances,
        'accounts_info': accounts_info
    }

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
                message += f"   • {date}: {balance:>12,.2f} руб.\n"
            
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
                message += f"   • {date}: {balance:>12,.2f} руб.\n"
            
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



