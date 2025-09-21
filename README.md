# WatchDog - Finolog Monitoring Bot

## Overview
WatchDog is a monitoring system that tracks financial accounts in Finolog and sends alerts via Telegram when certain conditions are met.

## Features
- Monitor account balances in Finolog
- Send notifications about threatening balances
- Provide balance reports on demand
- Support for both production and test environments

## Project Structure
- `launcher.py` - Main entry point for the production bot
- `launcher_test.py` - Entry point for the test bot
- `api_functions.py` - Functions for interacting with the Finolog API
- `telegram_functions.py` - Functions for sending Telegram messages
- `config.py` - Configuration settings
- `contacts.py` - Bot-specific configurations
- `.github/workflows/` - GitHub Actions workflow files

## Setup
1. Clone the repository
2. Create a `.env` file with required environment variables
3. Install dependencies: `pip install requests python-telegram-bot`

## Environment Variables
- `FINOLOG_API_KEY` - API key for Finolog
- `FINOLOG_BIZ_ID` - Business ID for Finolog
- `THREATENING_ACCOUNT_IDS` - Comma-separated list of account IDs to monitor
- `THREATENING_THRESHOLD` - Balance threshold for alerts
- `THREATENING_DAYS_AHEAD` - Days to look ahead for forecasting
- `MAIN_BOT_TOKEN` - Telegram token for the main bot
- `MAIN_BOT_ALLOWED_USERS` - Comma-separated list of allowed Telegram user IDs for main bot
- `TEST_BOT_TOKEN` - Telegram token for the test bot
- `TEST_BOT_ALLOWED_USERS` - Comma-separated list of allowed Telegram user IDs for test bot

## Usage
- Run the production bot: `python launcher.py`
- Run the test bot: `python launcher_test.py`

## Automated Deployment
This project uses GitHub Actions for automated testing and deployment:
- `test.yml` - Runs basic tests
- `server-test.yml` - Runs the test launcher on the production server
- `deploy-test.yml` - Deploys and runs the test bot
- `deploy.yml` - Deploys to production
- `release.yml` - Creates a new release and triggers deployment

For more information, see [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md).

## Documentation
- [PRODUCT_DOCUMENTATION.md](PRODUCT_DOCUMENTATION.md) - Detailed product documentation
- [DEPLOYMENT_PROCESS.md](DEPLOYMENT_PROCESS.md) - Deployment process
- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md) - GitHub Actions setup guide