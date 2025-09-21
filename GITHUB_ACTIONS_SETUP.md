# GitHub Actions Setup Guide

## Overview
This project uses GitHub Actions for automated testing, deployment, and release management. This guide explains how to set up the required secrets and how to use the workflows.

## Required Secrets
Add the following secrets to your GitHub repository (Settings > Secrets and variables > Actions > New repository secret):

1. `SSH_PRIVATE_KEY` - Private SSH key for connecting to the server
2. `SSH_USER` - SSH username (e.g., sheinin)
3. `SSH_HOST` - Server hostname (e.g., n8n.bpmdoc.com)
4. `FINOLOG_API_KEY` - API key for Finolog
5. `FINOLOG_BIZ_ID` - Business ID for Finolog
6. `THREATENING_ACCOUNT_IDS` - Comma-separated list of account IDs to monitor
7. `THREATENING_THRESHOLD` - Balance threshold for alerts (default: 100000)
8. `THREATENING_DAYS_AHEAD` - Days to look ahead for forecasting (default: 356)
9. `MAIN_BOT_TOKEN` - Telegram token for the main bot
10. `MAIN_BOT_ALLOWED_USERS` - Comma-separated list of allowed Telegram user IDs for main bot
11. `TEST_BOT_TOKEN` - Telegram token for the test bot
12. `TEST_BOT_ALLOWED_USERS` - Comma-separated list of allowed Telegram user IDs for test bot

## Available Workflows

### 1. Run Tests (`test.yml`)
Runs basic import and configuration tests.
- Trigger: Push to main, pull requests to main, manual
- Usage: Automatically runs on code changes or can be triggered manually from Actions tab

### 2. Run Test on Server (`server-test.yml`)
Runs the test launcher on the production server.
- Trigger: Manual only
- Usage: Trigger from Actions tab to test the bot on the server

### 3. Deploy & Run Test Bot (`deploy-test.yml`)
Deploys the code and runs the test bot on the server.
- Trigger: Manual only
- Usage: Trigger from Actions tab to deploy and test

### 4. Deploy to Production (`deploy.yml`)
Deploys the code to production.
- Trigger: Manual or on release publish
- Usage: Trigger from Actions tab or automatically on release

### 5. Create Release (`release.yml`)
Creates a new release and triggers deployment.
- Trigger: Manual only
- Usage: Trigger from Actions tab, provide version number and description