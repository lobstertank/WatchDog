#!/bin/bash

# Переходим в директорию бота
cd ~/watchdog

# Проверяем, рабочий ли день (используем JSON систему)
if python3 holiday_checker_json.py; then
    echo "$(date): Рабочий день - запускаем бота" >> bot.log
    python3 telegram_bot.py >> bot.log 2>&1
else
    echo "$(date): Выходной/праздник - пропускаем запуск" >> bot.log
fi
