# WatchDog - Краткая справка по командам

## 🚀 Быстрые команды

### Подключение к серверу
```bash
ssh n8n-server
```

### Проверка статуса системы
```bash
# Статус cron
ssh n8n-server "sudo systemctl status cron"

# Текущие cron задачи
ssh n8n-server "crontab -l"

# Процессы WatchDog
ssh n8n-server "ps aux | grep -i watchdog"
```

### Просмотр логов
```bash
# Логи основного бота
ssh n8n-server "tail -f ~/watchdog/logs/cron.log"

# Логи обновления праздников
ssh n8n-server "tail -f ~/watchdog/logs/holiday_updater.log"

# Логи за сегодня
ssh n8n-server "grep \"\$(date +%Y-%m-%d)\" ~/watchdog/logs/cron.log"
```

### Ручной запуск
```bash
# Основной бот
ssh n8n-server "cd ~/watchdog && ./run_bot.sh"

# Тестовый бот
ssh n8n-server "cd ~/watchdog && python3 launcher_test.py"

# Обновление праздников
ssh n8n-server "cd ~/watchdog && ./run_holiday_updater.sh"
```

## 🔧 Управление cron

### Просмотр задач
```bash
ssh n8n-server "crontab -l"
```

### Редактирование задач
```bash
ssh n8n-server "crontab -e"
```

### Перезапуск cron
```bash
ssh n8n-server "sudo systemctl restart cron"
```

## 📁 Управление файлами

### Просмотр файлов
```bash
ssh n8n-server "cd ~/watchdog && ls -la"
```

### Проверка прав доступа
```bash
ssh n8n-server "cd ~/watchdog && ls -la *.sh"
```

### Создание резервной копии
```bash
ssh n8n-server "cd ~/watchdog && tar -czf WG_backup_\$(date +%d%m%H%M).tgz *.py *.json *.sh *.txt *.md"
```

## 🧪 Тестирование

### Проверка импортов
```bash
ssh n8n-server "cd ~/watchdog && python3 -c 'import launcher; print(\"OK\")'"
```

### Тест API Финолога
```bash
ssh n8n-server "cd ~/watchdog && python3 -c 'from stable_functions import get_all_accounts; print(len(get_all_accounts()))'"
```

### Тест праздников
```bash
ssh n8n-server "cd ~/watchdog && python3 holiday_checker_json.py"
```

## 📊 Мониторинг

### Статус сервисов
```bash
# Cron
ssh n8n-server "sudo systemctl status cron"

# Время системы
ssh n8n-server "timedatectl"

# Использование диска
ssh n8n-server "df -h ~/watchdog"
```

### Сетевые проверки
```bash
# API Финолога
ssh n8n-server "curl -I https://api.finolog.ru/v1/"

# Telegram API
ssh n8n-server "curl -I https://api.telegram.org/"
```

## 🚨 Экстренные команды

### Остановка системы
```bash
ssh n8n-server "sudo systemctl stop cron"
```

### Восстановление из резервной копии
```bash
ssh n8n-server "cd ~/watchdog && tar -xzf WG_backup_*.tgz"
```

### Очистка логов
```bash
ssh n8n-server "cd ~/watchdog/logs && > cron.log && > holiday_updater.log"
```

## 📋 Текущая конфигурация

### Cron расписание
```bash
# Основной бот: 9:00-18:00 каждый час
0 9-18 * * * cd /home/sheinin/watchdog && ./run_bot.sh >> /home/sheinin/watchdog/logs/cron.log 2>&1

# Обновление праздников: первый понедельник месяца в 14:00
0 14 1-7 * 1 cd /home/sheinin/watchdog && ./run_holiday_updater.sh >> /home/sheinin/watchdog/logs/holiday_updater.log 2>&1
```

### Основные файлы
```
~/watchdog/
├── launcher.py              # Точка входа основного бота
├── launcher_test.py         # Точка входа тестового бота
├── telegram_bot.py          # Telegram бот
├── stable_functions.py      # API функции
├── config.py                # Конфигурация
├── contacts.py              # Настройки ботов
├── run_bot.sh               # Скрипт запуска
├── holidays_2025.json       # Календарь 2025
├── holidays_2026.json       # Календарь 2026
└── logs/                    # Папка логов
    ├── cron.log             # Логи основного бота
    └── holiday_updater.log  # Логи обновления праздников
```

### Токены ботов
```
Основной бот: 8363091905:AAE8n7P1PwuQrmQRIGYPSLmgi9ceNgIY9lE
Тестовый бот: 8351421023:AAEmidqjJjbkVOT3CRwLQ7LFlvaWWTUGfO0
```

## 🎯 Следующие запуски

### Основной бот
- **Следующий запуск:** 19:00 (через ~30 минут)
- **Расписание:** Каждый час с 9:00 до 18:00

### Обновление праздников
- **Следующий запуск:** 6 октября 2025 в 14:00
- **Расписание:** Первый понедельник каждого месяца

---

**Последнее обновление:** 18.09.2025 18:32 MSK
