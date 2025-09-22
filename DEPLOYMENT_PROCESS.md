# Deployment Process

## Manual Deployment
If you need to deploy manually, follow these steps:

1. Ensure all changes are committed and pushed to the repository
2. Connect to the server via SSH:
   ```
   ssh sheinin@n8n.bpmdoc.com
   ```
3. Navigate to the watchdog directory:
   ```
   cd ~/watchdog
   ```
4. Stop any running instances:
   ```
   pkill -f launcher.py
   ```
5. Pull the latest changes:
   ```
   git pull
   ```
6. Update the environment variables if needed:
   ```
   nano .env
   ```
7. Start the bot:
   ```
   nohup python3 launcher.py > logs/launcher.log 2>&1 &
   ```
8. Verify the bot is running:
   ```
   ps aux | grep launcher.py
   ```
9. Check the logs:
   ```
   tail -f logs/launcher.log
   ```

## Automated Deployment with GitHub Actions

### Production Deployment
1. Go to the GitHub repository's Actions tab
2. Select "Deploy to Production" workflow
3. Click "Run workflow"
4. Select the branch to deploy (usually main)
5. Click "Run workflow" button

### Test Deployment
1. Go to the GitHub repository's Actions tab
2. Select "Deploy & Run Test Bot" workflow
3. Click "Run workflow"
4. Select the branch to deploy (usually main)
5. Click "Run workflow" button

### Server Testing
1. Go to the GitHub repository's Actions tab
2. Select "Run Test on Server" workflow
3. Click "Run workflow"
4. Select the branch to test (usually main)
5. Click "Run workflow" button

## Creating a New Release
1. Go to the GitHub repository's Actions tab
2. Select "Create Release" workflow
3. Click "Run workflow"
4. Enter the version number (e.g., 1.2.3)
5. Enter the release description
6. Click "Run workflow" button

## Cron Job Configuration
The bot is configured to run via cron with the following schedule:

```
# Основной бот: 9:00-18:00 каждый час (скрипт сам пропускает праздники)
0 9-18 * * * cd /home/sheinin/watchdog && ./run_bot_with_holidays.sh

# Обновление праздников: первый понедельник месяца в 14:00
0 14 1-7 * 1 cd /home/sheinin/watchdog && ./run_holiday_updater.sh
```

To edit the cron job:
```
crontab -e
```

## Verification After Deployment

After deploying, verify that the system is working correctly:

1. Check that all files were deployed:
   ```
   ls -la ~/watchdog
   ```

2. Verify cron jobs are configured correctly:
   ```
   crontab -l
   ```

3. Check logs directory exists and has proper permissions:
   ```
   ls -la ~/watchdog/logs
   ```

4. Test the bot manually:
   ```
   cd ~/watchdog && ./run_bot_with_holidays.sh
   ```

5. Check the logs for any errors:
   ```
   tail -f ~/watchdog/logs/bot.log
   ```