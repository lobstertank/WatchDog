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
The bot is configured to run every 15 minutes via cron:

```
*/15 * * * * cd ~/watchdog && python3 launcher.py >> logs/launcher.log 2>&1
```

To edit the cron job:
```
crontab -e
```