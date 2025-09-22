#!/bin/bash

# Переходим в директорию бота
cd ~/watchdog

# Создаем директорию логов, если отсутствует
mkdir -p logs

# Запускаем обновление календаря праздников
echo "$(date): Запуск обновления календаря праздников" >> logs/holiday_updater.log
python3 holiday_updater_minimal.py >> logs/holiday_updater.log 2>&1
echo "$(date): Обновление календаря завершено" >> logs/holiday_updater.log
