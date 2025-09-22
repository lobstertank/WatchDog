# Развертывание WatchDog Telegram бота на Linux сервере

## Описание проекта
WatchDog - автоматизированная система мониторинга остатков на счетах через API Финолога с уведомлениями в Telegram. Система учитывает рабочие дни и праздники, автоматически обновляет календарь праздников.

## Архитектура проекта
- **701 строка кода** в 6 Python файлах
- **Модульная архитектура** без дублирования кода
- **Централизованные настройки** в `config.py`
- **Автоматическое обновление** календаря праздников

## Требования
- Python 3.6+
- Linux сервер с доступом к интернету
- Cron для автоматического запуска
- API ключ Финолога
- Telegram Bot Token

## Структура файлов

### Основные модули
- `config.py` (23 строки) - централизованные настройки
- `telegram_bot.py` (116 строк) - Telegram бот и уведомления
- `forecast.py` (84 строки) - анализ остатков и прогноз
- `stable_functions.py` (185 строк) - API функции для Финолога
- `holiday_checker_json.py` (126 строк) - работа с календарем праздников
- `holiday_updater_minimal.py` (167 строк) - обновление календаря

### Данные и скрипты
- `holidays_2025.json`, `holidays_2026.json` - календари праздников
- `run_bot.sh` - простой запуск бота
- `run_bot_with_holidays.sh` - запуск с проверкой праздников
- `run_holiday_updater.sh` - обновление календаря
- `requirements.txt` - зависимости Python

## Установка

### 1. Подготовка сервера
```bash
# Создайте директорию
mkdir -p ~/watchdog
cd ~/watchdog

# Установите московский часовой пояс
sudo timedatectl set-timezone Europe/Moscow
```

### 2. Загрузка файлов
Загрузите все файлы проекта в `~/watchdog/`:
```bash
# Основные модули
scp config.py telegram_bot.py forecast.py stable_functions.py user@server:~/watchdog/
scp holiday_checker_json.py holiday_updater_minimal.py user@server:~/watchdog/

# Данные и скрипты
scp holidays_2025.json holidays_2026.json user@server:~/watchdog/
scp run_bot.sh run_bot_with_holidays.sh run_holiday_updater.sh user@server:~/watchdog/
scp requirements.txt README.md DEPLOYMENT.md user@server:~/watchdog/
```

### 3. Настройка прав доступа
```bash
cd ~/watchdog
chmod +x *.sh
ls -la
```

### 4. Настройка конфигурации
Отредактируйте `config.py`:
```python
# API настройки Финолога
FINOLOG_CONFIG = {
    'api_key': 'YOUR_API_KEY',  # Ваш API ключ
    'biz_id': 'YOUR_BIZ_ID',    # Ваш Biz ID
    'base_url': 'https://api.finolog.ru/v1'
}

# Настройки Telegram бота
TELEGRAM_CONFIG = {
    'bot_token': 'YOUR_BOT_TOKEN',
    'allowed_users': [
        12345678,  # Ваш Telegram ID
    ]
}
```

### 5. Настройка cron
```bash
# Создайте файл с расписанием (ВАЖНО: без символов \r)
cat > /tmp/watchdog_cron << 'EOF'
# WatchDog - мониторинг остатков
# Обновление календаря праздников - первый понедельник месяца в 14:00 (MSK)
0 14 1-7 * 1 /home/sheinin/watchdog/run_holiday_updater.sh
# Проверка остатков - каждый час с 9:00 до 18:00 (MSK)
0 9-18 * * * /home/sheinin/watchdog/run_bot_with_holidays.sh
EOF

# Установите расписание
crontab /tmp/watchdog_cron

# Проверьте установку (должно быть без символов \r)
crontab -l

# Перезапустите cron для применения изменений
sudo systemctl restart cron
```

## Мониторинг

### Просмотр логов
```bash
# Основной лог бота
tail -f ~/watchdog/logs/bot.log

# Лог обновления календаря
tail -f ~/watchdog/logs/holiday_updater.log

# Логи за сегодня
grep "$(date +%Y-%m-%d)" ~/watchdog/logs/bot.log
```

### Тестирование
```bash
cd ~/watchdog

# Тест проверки праздников
python3 holiday_checker_json.py

# Тест обновления календаря
python3 holiday_updater_minimal.py

# Ручной запуск бота
./run_bot_with_holidays.sh

# Прямой запуск Python
python3 telegram_bot.py
```

## Функциональность

### Автоматические задачи
1. **Обновление календаря праздников**
   - Расписание: 1 число каждого месяца в 14:00 MSK
   - Источник: КонсультантПлюс
   - Результат: обновление `holidays_YYYY.json`

2. **Мониторинг остатков**
   - Расписание: каждый час с 9:00 до 18:00 MSK
   - Проверка: только в рабочие дни
   - Уведомления: при отрицательных остатках

### Логика работы
- Система автоматически определяет рабочие дни
- Учитывает праздники и переносы рабочих дней
- Отправляет уведомления только при наличии минусов
- Логирует все операции

## Устранение неполадок

### Проверка системы
```bash
# Статус cron
systemctl status cron

# Текущее время
timedatectl

# Права доступа
ls -la ~/watchdog/

# Версия Python
python3 --version

# Проверка задач cron
crontab -l

# Логи cron (рекомендуется)
sudo journalctl -u cron -n 20

# Мониторинг cron в реальном времени
sudo journalctl -u cron -f
```

### Проверка конфигурации
```bash
# Тест импорта модулей
python3 -c "import telegram_bot; import forecast; import stable_functions; print('OK')"

# Тест API Финолога
python3 -c "from stable_functions import get_all_accounts; print(len(get_all_accounts()))"

# Тест Telegram бота
python3 -c "from telegram_bot import send_telegram_message; print('Bot OK')"
```

### Проверка сети
```bash
# API Финолога
curl -I https://api.finolog.ru/v1/

# Telegram API
curl -I https://api.telegram.org/

# КонсультантПлюс
curl -I https://www.consultant.ru/
```

### Частые проблемы
1. **Неправильный часовой пояс** - проверьте `timedatectl`
2. **Нет прав на файлы** - выполните `chmod +x *.sh`
3. **Неправильные API ключи** - проверьте `config.py`
4. **Cron не работает** - проверьте `systemctl status cron`
5. **Символы `\r` в crontab** - пересоздайте crontab без Windows-символов
6. **Задачи cron не выполняются** - проверьте логи: `sudo journalctl -u cron`

## Безопасность
- Все настройки в `config.py` (можно исключить из git)
- API ключи не должны быть в публичном доступе
- Пользователи должны сначала написать боту
- Логи содержат только служебную информацию

## Обновление
```bash
# Остановите cron (опционально)
sudo systemctl stop cron

# Обновите файлы
scp new_files.py user@server:~/watchdog/

# Перезапустите cron
sudo systemctl start cron

# Проверьте работу
./run_bot_with_holidays.sh
```

## Статистика проекта
- **701 строка кода** в 6 файлах
- **Автоматизация**: 100%
- **Покрытие**: рабочие дни + праздники
- **Мониторинг**: каждый час 9:00-18:00 MSK
- **Обновления**: автоматические ежемесячно