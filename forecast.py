from stable_functions import get_all_accounts, get_current_balances, get_all_transactions_for_year, filter_transactions_by_month
from datetime import datetime
from config import MONITORING_CONFIG

def forecast():
    """Анализ отрицательных остатков по месяцам"""
    
    # Получаем все счета
    accounts = get_all_accounts()
    if not accounts:
        return
    
    # Получаем текущие остатки
    current_balances = get_current_balances(accounts)
    
    # Текущая дата
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_year = now.year
    current_month = now.month
    
    # Месяцы для прогноза (текущий + следующие N месяцев из конфига)
    months_ahead = MONITORING_CONFIG['months_ahead']
    months = []
    for i in range(months_ahead):
        month = current_month + i
        year = current_year
        if month > 12:
            month -= 12
            year += 1
        months.append((year, month))
    
    print("АНАЛИЗ ОТРИЦАТЕЛЬНЫХ ОСТАТКОВ")
    print("=" * 50)
    
    accounts_with_negatives = []
    
    # Анализ для каждого счета
    for account in accounts:
        account_id = account.get('id')
        account_name = account.get('name', 'Без названия')
        
        # Текущий остаток
        current_balance = current_balances[account_id]['balance']
        
        # Получаем все плановые транзакции на год вперед от текущей даты одним запросом
        year_transactions = get_all_transactions_for_year(account_id, current_date)
        
        running_balance = current_balance
        negative_months = []
        
        for year, month in months:
            # Фильтруем транзакции за конкретный месяц
            planned_ops = filter_transactions_by_month(year_transactions, year, month)
            
            # Считаем сальдо плановых операций
            planned_balance = 0
            for tx in planned_ops:
                value = tx.get('value', 0)
                tx_type = tx.get('type', '')
                if tx_type == 'in':
                    planned_balance += value
                elif tx_type == 'out':
                    planned_balance += value
            
            # Обновляем баланс
            running_balance += planned_balance
            
            # Проверяем на отрицательный баланс
            if running_balance < 0:
                negative_months.append(f"{month:02d}-{year}")
        
        # Сохраняем только счета с минусами
        if negative_months:
            months_str = ", ".join(negative_months)
            accounts_with_negatives.append(f"{account_name}: минусы в месяцах: {months_str}")
    
    # Выводим результат
    if accounts_with_negatives:
        for account_info in accounts_with_negatives:
            print(account_info)
    else:
        print("Минусов нет")

if __name__ == "__main__":
    forecast()
