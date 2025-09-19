# Процесс выката WatchDog на продакшн

## 📋 Обзор процесса

Данный документ описывает пошаговый процесс развертывания системы WatchDog на продакшн сервер `n8n.bpmdoc.com`.

## 🎯 Цели процесса

- ✅ Безопасное развертывание обновлений
- ✅ Минимизация времени простоя
- ✅ Сохранение резервных копий
- ✅ Проверка работоспособности
- ✅ Настройка автоматического запуска

## 🏗️ Архитектура развертывания

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Локальная      │    │   Сервер         │    │   Продакшн      │
│  разработка     │───►│  n8n.bpmdoc.com  │───►│   система       │
│  (Windows)      │    │  (Linux)         │    │   (cron)        │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Структура файлов для развертывания

### Основные модули (обязательные)
```
launcher.py              # Точка входа основного бота
launcher_test.py         # Точка входа тестового бота
telegram_bot.py          # Telegram бот и уведомления
stable_functions.py      # API функции для Финолога
forecast.py              # Анализ остатков и прогноз
holiday_checker_json.py  # Работа с календарем праздников
holiday_updater_minimal.py # Обновление календаря
config.py                # Централизованные настройки
contacts.py              # Настройки ботов и пользователей
```

### Данные и конфигурация
```
holidays_2025.json       # Календарь праздников 2025
holidays_2026.json       # Календарь праздников 2026
requirements.txt         # Зависимости Python
```

### Скрипты запуска
```
run_bot.sh               # Запуск основного бота
run_bot_with_holidays.sh # Запуск с проверкой праздников
run_holiday_updater.sh   # Обновление календаря праздников
```

## 🚀 Пошаговый процесс развертывания

### Этап 1: Подготовка

#### 1.1 Проверка локальных файлов
```bash
# Проверка наличия всех необходимых файлов
ls -la *.py *.json *.sh *.txt

# Проверка синтаксиса Python файлов
python3 -m py_compile *.py
```

#### 1.2 Создание архива для развертывания
```bash
# Создание архива с обновленными файлами
tar -czf WG_deploy_$(date +%d%m%H%M).tgz *.py *.json *.sh *.txt *.md

# Проверка архива
tar -tzf WG_deploy_*.tgz
```

### Этап 2: Резервное копирование

#### 2.1 Создание резервной копии на сервере
```bash
# Подключение к серверу
ssh n8n-server

# Создание резервной копии
cd ~/watchdog
tar -czf WG_backup_$(date +%d%m%H%M).tgz *.py *.json *.sh *.txt *.md

# Проверка резервной копии
ls -la WG_backup_*.tgz
```

#### 2.2 Скачивание резервной копии на локальную машину
```bash
# Скачивание резервной копии
scp n8n-server:~/watchdog/WG_backup_*.tgz ./

# Проверка скачанного файла
ls -la WG_backup_*.tgz
```

### Этап 3: Загрузка обновлений

#### 3.1 Загрузка основных модулей
```bash
# Загрузка ключевых файлов
scp launcher.py telegram_bot.py stable_functions.py config.py contacts.py n8n-server:~/watchdog/
scp forecast.py holiday_checker_json.py n8n-server:~/watchdog/

# Проверка загрузки
ssh n8n-server "cd ~/watchdog && ls -la *.py | head -10"
```

#### 3.2 Загрузка скриптов запуска
```bash
# Загрузка скриптов
scp run_bot.sh n8n-server:~/watchdog/

# Установка прав доступа
ssh n8n-server "cd ~/watchdog && chmod +x run_bot.sh"
```

### Этап 4: Проверка развертывания

#### 4.1 Проверка импортов
```bash
# Проверка основных модулей
ssh n8n-server "cd ~/watchdog && python3 -c 'import launcher; print(\"Launcher OK\")'"
ssh n8n-server "cd ~/watchdog && python3 -c 'import telegram_bot, stable_functions, contacts; print(\"All modules OK\")'"
```

#### 4.2 Тестовый запуск
```bash
# Тестовый запуск с таймаутом
ssh n8n-server "cd ~/watchdog && timeout 10s ./run_bot.sh"
```

#### 4.3 Проверка логов
```bash
# Проверка создания логов
ssh n8n-server "cd ~/watchdog && ls -la logs/ && tail -5 logs/cron.log 2>/dev/null || echo 'Logs will be created on first run'"
```

### Этап 5: Настройка автоматизации

#### 5.1 Создание правильного расписания cron
```bash
# Создание файла с расписанием
cat > /tmp/watchdog_cron << 'EOF'
0 9-18 * * * cd /home/sheinin/watchdog && ./run_bot.sh >> /home/sheinin/watchdog/logs/cron.log 2>&1
0 14 1-7 * 1 cd /home/sheinin/watchdog && ./run_holiday_updater.sh >> /home/sheinin/watchdog/logs/holiday_updater.log 2>&1
EOF

# Установка расписания
ssh n8n-server "crontab /tmp/watchdog_cron"
```

#### 5.2 Проверка cron задач
```bash
# Проверка установленных задач
ssh n8n-server "crontab -l"

# Перезапуск cron сервиса
ssh n8n-server "sudo systemctl restart cron"
```

#### 5.3 Проверка статуса cron
```bash
# Проверка статуса сервиса
ssh n8n-server "sudo systemctl status cron | head -5"
```

### Этап 6: Финальная проверка

#### 6.1 Проверка всех компонентов
```bash
# Проверка файлов
ssh n8n-server "cd ~/watchdog && ls -la *.py *.sh *.json"

# Проверка прав доступа
ssh n8n-server "cd ~/watchdog && ls -la run_bot.sh"

# Проверка cron задач
ssh n8n-server "crontab -l"
```

#### 6.2 Тестовый запуск системы
```bash
# Полный тестовый запуск
ssh n8n-server "cd ~/watchdog && timeout 15s ./run_bot.sh && echo 'System test completed'"
```

## 🔧 Команды для быстрого развертывания

### Полный процесс одной командой
```bash
#!/bin/bash
# Скрипт быстрого развертывания

echo "🚀 Начинаем развертывание WatchDog..."

# 1. Создание резервной копии
echo "📦 Создание резервной копии..."
ssh n8n-server "cd ~/watchdog && tar -czf WG_backup_\$(date +%d%m%H%M).tgz *.py *.json *.sh *.txt *.md"
scp n8n-server:~/watchdog/WG_backup_*.tgz ./

# 2. Загрузка обновлений
echo "📤 Загрузка обновлений..."
scp launcher.py telegram_bot.py stable_functions.py config.py contacts.py forecast.py holiday_checker_json.py n8n-server:~/watchdog/
scp run_bot.sh n8n-server:~/watchdog/

# 3. Настройка прав
echo "🔧 Настройка прав доступа..."
ssh n8n-server "cd ~/watchdog && chmod +x run_bot.sh && mkdir -p logs"

# 4. Проверка
echo "✅ Проверка развертывания..."
ssh n8n-server "cd ~/watchdog && python3 -c 'import launcher; print(\"OK\")'"

# 5. Тестовый запуск
echo "🧪 Тестовый запуск..."
ssh n8n-server "cd ~/watchdog && timeout 10s ./run_bot.sh"

echo "🎉 Развертывание завершено!"
```

## 📊 Мониторинг развертывания

### Ключевые метрики
- ✅ **Время развертывания:** ~5-10 минут
- ✅ **Время простоя:** 0 (горячее развертывание)
- ✅ **Размер резервной копии:** ~80KB
- ✅ **Количество файлов:** 14 основных файлов

### Проверочный список
- [ ] Резервная копия создана
- [ ] Файлы загружены на сервер
- [ ] Права доступа настроены
- [ ] Импорты работают
- [ ] Тестовый запуск успешен
- [ ] Cron задачи настроены
- [ ] Логирование работает

## 🚨 Откат изменений

### Процедура отката
```bash
# 1. Остановка cron (опционально)
ssh n8n-server "sudo systemctl stop cron"

# 2. Восстановление из резервной копии
ssh n8n-server "cd ~/watchdog && tar -xzf WG_backup_*.tgz"

# 3. Перезапуск cron
ssh n8n-server "sudo systemctl start cron"

# 4. Проверка восстановления
ssh n8n-server "cd ~/watchdog && ./run_bot.sh"
```

## 🔍 Диагностика проблем

### Частые проблемы при развертывании

1. **Ошибки импорта**
   ```bash
   # Проверка синтаксиса
   python3 -m py_compile *.py
   
   # Проверка зависимостей
   python3 -c "import requests, datetime, json"
   ```

2. **Проблемы с правами доступа**
   ```bash
   chmod +x *.sh
   chmod 644 *.py *.json
   ```

3. **Ошибки cron**
   ```bash
   # Проверка синтаксиса crontab
   crontab -l
   
   # Проверка логов cron
   sudo journalctl -u cron -n 20
   ```

4. **Проблемы с сетью**
   ```bash
   # Проверка подключения к серверу
   ssh n8n-server "echo 'Connection OK'"
   
   # Проверка API
   curl -I https://api.finolog.ru/v1/
   ```

## 📈 Статистика развертывания

### Последнее развертывание (18.09.2025)
- **Время начала:** 18:13 MSK
- **Время завершения:** 18:32 MSK
- **Общее время:** 19 минут
- **Размер обновления:** 70KB
- **Статус:** ✅ Успешно

### История развертываний
| Дата | Время | Статус | Размер | Комментарий |
|------|-------|--------|--------|-------------|
| 18.09.2025 | 18:32 | ✅ | 70KB | Обновление архитектуры |
| 16.09.2025 | 13:59 | ✅ | 65KB | Первоначальное развертывание |

## 📞 Поддержка развертывания

### Контакты
- **Разработчик:** WatchDog Development Team
- **Сервер:** n8n.bpmdoc.com
- **Пользователь:** sheinin

### Документация
- **Продукт:** `PRODUCT_DOCUMENTATION.md`
- **Развертывание:** `DEPLOYMENT_PROCESS.md`
- **README:** `README.md`

---

**Версия документации:** 1.0  
**Дата обновления:** 18.09.2025  
**Последнее развертывание:** 18.09.2025 18:32 MSK
