#!/bin/bash
# Скрипт для тестирования развертывания WatchDog

echo "🧪 Тестирование WatchDog перед развертыванием"
echo "=============================================="

# Проверка импортов
echo "📦 Проверка импортов..."
python3 -c "
try:
    from api_functions import get_all_accounts, get_current_balances
    from telegram_functions import send_telegram_message, send_telegram_message_wrapper
    from telegram_bot import main
    from config import FINOLOG_CONFIG, THREATENING_CONFIG
    from contacts import MAIN_BOT_CONFIG, TEST_BOT_CONFIG
    print('✅ Все импорты успешны')
except ImportError as e:
    print(f'❌ Ошибка импорта: {e}')
    exit(1)
"

# Проверка конфигурации
echo "⚙️  Проверка конфигурации..."
python3 -c "
from config import FINOLOG_CONFIG, THREATENING_CONFIG
from contacts import MAIN_BOT_CONFIG, TEST_BOT_CONFIG

# Проверка обязательных ключей
required_finolog = ['api_key', 'biz_id', 'base_url']
required_threatening = ['account_ids', 'threshold', 'days_ahead']
required_bot = ['bot_token', 'allowed_users']

for key in required_finolog:
    assert key in FINOLOG_CONFIG, f'Отсутствует FINOLOG_CONFIG.{key}'
    
for key in required_threatening:
    assert key in THREATENING_CONFIG, f'Отсутствует THREATENING_CONFIG.{key}'
    
for key in required_bot:
    assert key in MAIN_BOT_CONFIG, f'Отсутствует MAIN_BOT_CONFIG.{key}'
    assert key in TEST_BOT_CONFIG, f'Отсутствует TEST_BOT_CONFIG.{key}'
    
print('✅ Конфигурация валидна')
"

# Проверка структуры файлов
echo "📁 Проверка структуры файлов..."
required_files=(
    "launcher.py"
    "launcher_test.py" 
    "telegram_bot.py"
    "api_functions.py"
    "telegram_functions.py"
    "config.py"
    "contacts.py"
    "holiday_checker_json.py"
    "holiday_updater_minimal.py"
    "holidays_2025.json"
    "holidays_2026.json"
    "requirements.txt"
    "run_bot.sh"
    "run_holiday_updater.sh"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ Отсутствует: $file"
        exit 1
    fi
done

# Проверка скриптов
echo "🔧 Проверка скриптов..."
scripts=("run_bot.sh" "run_holiday_updater.sh" "run_bot_with_holidays.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "✅ $script"
    else
        echo "⚠️  $script не найден (опциональный)"
    fi
done

# Проверка документации
echo "📚 Проверка документации..."
docs=("PRODUCT_DOCUMENTATION.md" "DEPLOYMENT_PROCESS.md" "QUICK_REFERENCE.md" "GITHUB_ACTIONS_SETUP.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "✅ $doc"
    else
        echo "⚠️  $doc не найден"
    fi
done

echo ""
echo "🎉 Все тесты пройдены успешно!"
echo "🚀 Готово к развертыванию!"
echo ""
echo "Следующие шаги:"
echo "1. git add . && git commit -m 'feat: add GitHub Actions workflows'"
echo "2. git push origin master"
echo "3. Настроить Secrets в GitHub"
echo "4. Запустить деплой через GitHub Actions"
