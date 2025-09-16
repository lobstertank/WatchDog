#!/bin/bash

# Переходим в директорию бота
cd ~/watchdog

# Запускаем обновление календаря праздников
echo "$(date): Запуск обновления календаря праздников" >> holiday_updater.log
python3 holiday_updater_minimal.py >> holiday_updater.log 2>&1
echo "$(date): Обновление календаря завершено" >> holiday_updater.log
