# WatchDog - Finolog Monitoring Bot

## Overview
WatchDog is a monitoring system that tracks financial accounts in Finolog and sends alerts via Telegram when certain conditions are met. It provides real-time monitoring of account balances and can forecast potential issues.

## Features
- Monitor account balances in Finolog
- Send notifications about threatening balances
- Provide balance reports on demand
- Support for both production and test environments
- Automated deployment via GitHub Actions

## Architecture
The application is structured in a modular way with the following components:

### Core Modules
- `launcher.py` - Main entry point for the production bot
- `launcher_test.py` - Entry point for the test bot
- `api_functions.py` - Functions for interacting with the Finolog API
- `telegram_functions.py` - Functions for sending Telegram messages
- `config.py` - Configuration settings
- `contacts.py` - Bot-specific configurations

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

## CI/CD Pipeline
The project uses GitHub Actions for continuous integration and deployment:
- Automated testing on code changes
- Manual or automated deployment to production
- Release management with versioning