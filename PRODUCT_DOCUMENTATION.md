# WatchDog - Система мониторинга остатков Финолога

## 📋 Обзор продукта

**WatchDog** - автоматизированная система мониторинга остатков на счетах через API Финолога с уведомлениями в Telegram. Система учитывает рабочие дни и праздники, автоматически обновляет календарь праздников и предотвращает кассовые разрывы.

### 🎯 Основные возможности

- 🤖 **Telegram бот** с уведомлениями в реальном времени
- 🔍 **Автоматическая проверка** всех счетов в Финологе
- 📊 **Прогноз балансов** на 12 месяцев вперед
- ⚠️ **Обнаружение кассовых разрывов** и угрожающих остатков
- 📅 **Учет российских праздников** и рабочих дней
- 🔄 **Автоматическое обновление** календаря праздников
- ⚙️ **Гибкая конфигурация** и настройки

### 🏗️ Архитектура системы

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │◄───┤  WatchDog Core   │◄───┤  Finolog API    │
│   (Уведомления) │    │  (Анализ данных) │    │  (Источник)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Cron Scheduler│    │  Holiday System  │    │  Data Storage   │
│   (Автозапуск)  │    │  (Календарь)     │    │  (JSON файлы)   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Структура проекта

### Основные модули
- **`launcher.py`** (11 строк) - точка входа для основного бота
- **`launcher_test.py`** (11 строк) - точка входа для тестового бота
- **`telegram_bot.py`** (70 строк) - Telegram бот и уведомления
- **`api_functions.py`** (285 строк) - API функции для Финолога и расчеты
- **`telegram_functions.py`** (95 строк) - функции отправки сообщений в Telegram
- **`holiday_checker_json.py`** (134 строки) - работа с календарем праздников
- **`holiday_updater_minimal.py`** (167 строк) - обновление календаря

### Конфигурация и данные
- **`config.py`** (35 строк) - централизованные настройки
- **`contacts.py`** (25 строк) - настройки ботов и пользователей
- **`holidays_2025.json`** - календарь праздников 2025
- **`holidays_2026.json`** - календарь праздников 2026
- **`requirements.txt`** - зависимости Python

### Скрипты запуска
- **`run_bot.sh`** - запуск основного бота
- **`run_bot_with_holidays.sh`** - запуск с проверкой праздников
- **`run_holiday_updater.sh`** - обновление календаря праздников

## 🔧 Конфигурация

### API настройки Финолога
```python
FINOLOG_CONFIG = {
    'api_key': 'GXqFgOgsHOoTXbKDd9ff3dafa24ae865c48291100fe7cf82J14wlR8WCucDv4Gu',
    'biz_id': '53850',
    'base_url': 'https://api.finolog.ru/v1'
}
```

### Настройки мониторинга
```python
MONITORING_CONFIG = {
    'months_ahead': 12,        # Количество месяцев для прогноза
}

THREATENING_CONFIG = {
    'account_ids': [190104],   # ID счетов для проверки угрожающих балансов
    'threshold': 100000,       # Порог угрожающего баланса в рублях
    'days_ahead': 356,         # Количество дней для анализа
}
```

### Настройки ботов
```python
# Основной продуктивный бот
MAIN_BOT_CONFIG = {
    'bot_token': '8363091905:AAE8n7P1PwuQrmQRIGYPSLmgi9ceNgIY9lE',
    'allowed_users': [13553737, 2095138167]  # Ваш ID и Лена
}

# Тестовый бот
TEST_BOT_CONFIG = {
    'bot_token': '8351421023:AAEmidqjJjbkVOT3CRwLQ7LFlvaWWTUGfO0',
    'allowed_users': [13553737]  # Только Ваш ID
}
```

## ⏰ Расписание работы

### Cron задачи
```bash
# Основной скрипт: каждый день с 9:00 до 18:00 каждый час
0 9-18 * * * cd /home/sheinin/watchdog && ./run_bot.sh >> /home/sheinin/watchdog/logs/cron.log 2>&1

# Обновление праздников: 14:00 в первый понедельник каждого месяца
0 14 1-7 * 1 cd /home/sheinin/watchdog && ./run_holiday_updater.sh >> /home/sheinin/watchdog/logs/holiday_updater.log 2>&1
```

### Логика работы
1. **Проверка рабочих дней** - система работает только в рабочие дни
2. **Анализ остатков** - проверка всех счетов на отрицательные и угрожающие балансы
3. **Уведомления** - отправка только при наличии проблем
4. **Обновление календаря** - автоматическое обновление праздников ежемесячно

## ⚡ Оптимизация производительности

### API запросы
Система оптимизирована для минимального количества API запросов к Финологу:

- **Было:** 18+ запросов (1 для счетов + 17 для балансов + N для транзакций)
- **Стало:** 2-3 запроса (1 для счетов с балансами + 1-2 для транзакций)
- **Ускорение:** в 6-9 раз! 🚀

### Архитектурные улучшения
- **Разделение модулей:** `api_functions.py` (API) + `telegram_functions.py` (уведомления)
- **Использование summary:** балансы извлекаются из ответа `/account` endpoint
- **Таймауты:** предотвращение зависания на API запросах
- **Удаление дублирования:** убрана неиспользуемая `get_current_balance()`

## 🚀 Процесс развертывания

### 1. Подготовка сервера
```bash
# Создание директории
mkdir -p ~/watchdog
cd ~/watchdog

# Установка часового пояса
sudo timedatectl set-timezone Europe/Moscow
```

### 2. Загрузка файлов
```bash
# Основные модули
scp launcher.py telegram_bot.py api_functions.py telegram_functions.py config.py contacts.py n8n-server:~/watchdog/
scp holiday_checker_json.py holiday_updater_minimal.py n8n-server:~/watchdog/

# Данные и скрипты
scp holidays_2025.json holidays_2026.json requirements.txt n8n-server:~/watchdog/
scp run_bot.sh run_bot_with_holidays.sh run_holiday_updater.sh n8n-server:~/watchdog/
```

### 3. Настройка прав доступа
```bash
cd ~/watchdog
chmod +x *.sh
```

### 4. Настройка cron
```bash
# Создание расписания
cat > /tmp/watchdog_cron << 'EOF'
0 9-18 * * * cd /home/sheinin/watchdog && ./run_bot.sh >> /home/sheinin/watchdog/logs/cron.log 2>&1
0 14 1-7 * 1 cd /home/sheinin/watchdog && ./run_holiday_updater.sh >> /home/sheinin/watchdog/logs/holiday_updater.log 2>&1
EOF

# Установка расписания
crontab /tmp/watchdog_cron

# Перезапуск cron
sudo systemctl restart cron
```

### 5. Создание папки для логов
```bash
mkdir -p ~/watchdog/logs
```

## 📊 Мониторинг и логирование

### Логи системы
- **`~/watchdog/logs/cron.log`** - логи основного бота
- **`~/watchdog/logs/holiday_updater.log`** - логи обновления праздников
- **`~/watchdog/bot.log`** - старые логи (если есть)

### Команды мониторинга
```bash
# Просмотр логов в реальном времени
tail -f ~/watchdog/logs/cron.log

# Логи за сегодня
grep "$(date +%Y-%m-%d)" ~/watchdog/logs/cron.log

# Статус cron
systemctl status cron

# Проверка задач cron
crontab -l
```

## 🧪 Тестирование

### Ручное тестирование
```bash
cd ~/watchdog

# Тест проверки праздников
python3 holiday_checker_json.py

# Тест обновления календаря
python3 holiday_updater_minimal.py

# Ручной запуск основного бота
./run_bot.sh

# Ручной запуск тестового бота
python3 launcher_test.py
```

### Проверка конфигурации
```bash
# Тест импорта модулей
python3 -c "import telegram_bot; import api_functions; import telegram_functions; print('OK')"

# Тест API Финолога
python3 -c "from api_functions import get_all_accounts; print(len(get_all_accounts()))"

# Тест Telegram бота
python3 -c "from telegram_bot import send_telegram_message; print('Bot OK')"
```

## 🔄 Процесс обновления

### 1. Создание резервной копии
```bash
# На сервере
cd ~/watchdog
tar -czf WG_backup_$(date +%d%m%H%M).tgz *.py *.json *.sh *.txt *.md

# Скачивание на локальную машину
scp n8n-server:~/watchdog/WG_backup_*.tgz ./
```

### 2. Загрузка обновлений
```bash
# Загрузка основных файлов
scp launcher.py telegram_bot.py api_functions.py telegram_functions.py config.py contacts.py n8n-server:~/watchdog/
scp holiday_checker_json.py n8n-server:~/watchdog/

# Обновление скриптов запуска
scp run_bot.sh n8n-server:~/watchdog/
```

### 3. Проверка развертывания
```bash
# Проверка импортов
ssh n8n-server "cd ~/watchdog && python3 -c 'import launcher; print(\"OK\")'"

# Тестовый запуск
ssh n8n-server "cd ~/watchdog && timeout 10s ./run_bot.sh"
```

## 🛠️ Устранение неполадок

### Частые проблемы

1. **Cron не работает**
   ```bash
   sudo systemctl status cron
   sudo systemctl restart cron
   ```

2. **Неправильный часовой пояс**
   ```bash
   timedatectl
   sudo timedatectl set-timezone Europe/Moscow
   ```

3. **Нет прав на файлы**
   ```bash
   chmod +x ~/watchdog/*.sh
   ```

4. **Ошибки API**
   ```bash
   # Проверка API ключа в config.py
   # Проверка доступности API
   curl -I https://api.finolog.ru/v1/
   ```

5. **Проблемы с Telegram**
   ```bash
   # Проверка токена бота
   # Проверка доступности API
   curl -I https://api.telegram.org/
   ```

### Диагностика
```bash
# Проверка процессов
ps aux | grep python

# Проверка логов cron
sudo journalctl -u cron -n 20

# Проверка сетевого подключения
ping api.finolog.ru
ping api.telegram.org
```

## 📈 Статистика проекта

- **Общий объем кода:** 600+ строк в 7 Python файлах (оптимизировано)
- **Автоматизация:** 100%
- **Покрытие:** рабочие дни + праздники
- **Мониторинг:** 10 запусков в день (9:00-18:00)
- **Обновления:** автоматические ежемесячно
- **API интеграции:** Finolog + Telegram
- **Поддерживаемые годы:** 2025-2026
- **Оптимизация:** Удалено 5 неиспользуемых функций (33% кода)

## 🔒 Безопасность

- API ключи хранятся в конфигурационных файлах
- Пользователи должны быть добавлены в `allowed_users`
- Логи содержат только служебную информацию
- Резервные копии создаются перед обновлениями

## 📚 Описание модулей

### api_functions.py
**Назначение:** API функции для работы с Финологом и расчеты
**Основные функции:**
- `make_request(url, timeout=30)` - базовый API запрос с таймаутом
- `get_all_accounts()` - получение всех счетов с балансами
- `get_current_balances(accounts)` - извлечение балансов из данных счетов
- `get_all_transactions_for_all_accounts(account_ids, start_date)` - получение транзакций для всех счетов
- `calculate_daily_balances()` - расчет ежедневных остатков
- `analyze_all_accounts_balances()` - анализ всех счетов на проблемы

### telegram_functions.py
**Назначение:** Функции для отправки сообщений в Telegram
**Основные функции:**
- `send_telegram_message(bot_token, chat_id, text)` - отправка сообщения
- `send_positive_balance_report()` - уведомление о положительных остатках
- `send_balance_analysis_report()` - единый отчет об анализе остатков

### telegram_bot.py
**Назначение:** Основная логика бота и координация работы
**Основные функции:**
- `check_and_notify()` - проверка остатков и отправка уведомлений
- `main()` - точка входа для запуска бота
- `send_telegram_message_wrapper()` - обертка с поддержкой тестового режима

## 📞 Поддержка

При возникновении проблем проверьте:
1. Правильность API ключей в `config.py`
2. Доступность интернета
3. Логи в `~/watchdog/logs/`
4. Статус cron сервиса
5. Права доступа к файлам

---

**Версия документации:** 1.0  
**Дата обновления:** 18.09.2025  
**Автор:** WatchDog Development Team
