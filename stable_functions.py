import urllib.request
import urllib.parse
import json
import time
from config import FINOLOG_CONFIG

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
        current_date_str = current_dt.strftime("%Y-%m-%d")
        
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



