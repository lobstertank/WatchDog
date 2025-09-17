from stable_functions import get_all_accounts, get_current_balances, get_all_transactions_for_year, calculate_daily_balances
from datetime import datetime
from config import MONITORING_CONFIG

def forecast(transactions_by_account=None):
    """Анализ отрицательных остатков по дням"""
    
    # Получаем все счета
    accounts = get_all_accounts()
    if not accounts:
        return
    
    # Получаем текущие остатки
    current_balances = get_current_balances(accounts)
    
    # Текущая дата
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    
    # Количество дней для прогноза (месяцы * 30 дней)
    months_ahead = MONITORING_CONFIG['months_ahead']
    days_ahead = months_ahead * 30
    
    print("АНАЛИЗ ОТРИЦАТЕЛЬНЫХ ОСТАТКОВ")
    print("=" * 50)
    
    accounts_with_negatives = []
    
    # Анализ для каждого счета
    for account in accounts:
        account_id = account.get('id')
        account_name = account.get('name', 'Без названия')
        
        # Текущий остаток
        current_balance = current_balances[account_id]['balance']
        
        # Получаем транзакции (либо переданные, либо загружаем)
        # Приводим account_id к int для соответствия ключам в transactions_by_account
        account_id_int = int(account_id)
        if transactions_by_account and account_id_int in transactions_by_account:
            year_transactions = transactions_by_account[account_id_int]
        else:
            # По этому счету не было движений за год - используем пустой список
            year_transactions = []
        
        # Рассчитываем ежедневные остатки
        daily_balances = calculate_daily_balances(
            current_balance=current_balance,
            planned_transactions=year_transactions,
            start_date=current_date,
            days_ahead=days_ahead
        )
        
        # Ищем отрицательные дни
        negative_days = []
        for date_str, balance in daily_balances.items():
            if balance < 0:
                # Форматируем дату для вывода
                date_obj = datetime.strptime(date_str, "%Y-%m-%d 00:00:00")
                formatted_date = date_obj.strftime("%d-%m-%Y")
                negative_days.append(f"{formatted_date}")
        
        # Сохраняем только счета с минусами
        if negative_days:
            # Группируем по месяцам для компактности
            months_with_negatives = set()
            for date_str in negative_days:
                date_obj = datetime.strptime(date_str, "%d-%m-%Y")
                month_year = date_obj.strftime("%m-%Y")
                months_with_negatives.add(month_year)
            
            months_str = ", ".join(sorted(months_with_negatives))
            accounts_with_negatives.append(f"{account_name}: минусы в месяцах: {months_str}")
    
    # Выводим результат
    if accounts_with_negatives:
        for account_info in accounts_with_negatives:
            print(account_info)
    else:
        print("Минусов нет")

if __name__ == "__main__":
    forecast()
