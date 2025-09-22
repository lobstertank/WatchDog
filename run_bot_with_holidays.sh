#!/bin/bash

# Переходим в директорию бота
cd ~/watchdog

# Создаем директорию логов, если отсутствует
mkdir -p logs

# Проверяем, рабочий ли день (используем JSON систему)
if python3 holiday_checker_json.py; then
    echo "$(date): Рабочий день - запускаем бота" >> logs/bot.log
    python3 launcher.py >> logs/bot.log 2>&1
else
    echo "$(date): Выходной/праздник - пропускаем запуск" >> logs/bot.log
fi
