# WatchDog - Finolog Monitoring Bot

## Overview
WatchDog is a monitoring system that tracks financial accounts in Finolog and sends alerts via Telegram when certain conditions are met. It provides real-time monitoring of account balances and can forecast potential issues.

## Features
- Monitor account balances in Finolog
- Send notifications about threatening balances
- Provide balance reports on demand
- Support for both production and test environments
- Automated deployment via GitHub Actions
- Holiday-aware scheduling (skips non-working days)
- Force-run capability for manual checks regardless of holidays

## Architecture
The application is structured in a modular way with the following components:

### Core Modules
- `launcher.py` - Main entry point for the production bot
- `launcher_test.py` - Entry point for the test bot
- `launcher_force.py` - Entry point for forcing the bot to run regardless of holidays
- `launcher_notify.py` - Entry point for sending custom notifications
- `api_functions.py` - Functions for interacting with the Finolog API
- `telegram_functions.py` - Functions for sending Telegram messages
- `config.py` - Configuration settings
- `contacts.py` - Bot-specific configurations
- `holiday_checker_json.py` - Functions for checking if today is a working day
- `holiday_updater_minimal.py` - Functions for updating the holiday calendar

### Shell Scripts
- `run_bot.sh` - Script for running the bot directly
- `run_bot_with_holidays.sh` - Script for running the bot with holiday checking
- `run_holiday_updater.sh` - Script for updating the holiday calendar

### Configuration
- `.env` - Environment variables (not in repository)
- `config.py` - Configuration settings
- `contacts.py` - Bot-specific configurations

### Deployment
- GitHub Actions workflows for automated testing and deployment
- SSH deployment to production server

## Performance Optimization
The application has been optimized to reduce API calls:
- Leveraging the `summary` field in the `/account` endpoint to get balances in a single call
- Reducing API requests from 18+ to 2-3 per execution
- Eliminating redundant `get_current_balance()` function

## API Usage
The application uses the Finolog API to retrieve account information:
- `/account` endpoint to get all accounts with summaries
- Account balances are extracted from the summary field

## Telegram Integration
Two Telegram bots are used:
- Main bot for production use
- Test bot for testing changes

Messages are sent using the `send_telegram_message_wrapper` function which supports:
- Regular messages
- Test mode messages (prefixed with "🧪 ТЕСТ: ")

## Holiday Handling
The application is aware of holidays and working days:
- Uses JSON files (`holidays_2025.json`, `holidays_2026.json`) to store holiday information
- Automatically skips checks on non-working days
- Can be forced to run regardless of holidays using `launcher_force.py`
- Holiday calendar is automatically updated on the first Monday of each month

## CI/CD Pipeline
The project uses GitHub Actions for continuous integration and deployment:
- Automated testing on code changes
- Manual or automated deployment to production
- Release management with versioning
- Automatic verification of deployment success

## Troubleshooting
Common issues and their solutions:
- **Bot not running**: Check cron jobs with `crontab -l` and logs in `logs/bot.log`
- **API errors**: Verify API keys in `.env` file
- **Holiday detection issues**: Check holiday files and run `holiday_checker_json.py` manually
- **Deployment failures**: Check GitHub Actions logs and SSH connectivity