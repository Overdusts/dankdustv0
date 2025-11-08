# Deployment Guide

This guide will help you deploy the Discord Economy Bot to various platforms.

## Table of Contents
- [Local Deployment](#local-deployment)
- [VPS Deployment](#vps-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)

## Local Deployment

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Discord Bot Token

### Steps

1. **Clone or download the repository**
```bash
git clone <your-repo-url>
cd discord-economy-bot
```

2. **Create virtual environment (recommended)**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure the bot**
```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
```env
DISCORD_TOKEN=your_bot_token_here
GUILD_ID=your_guild_id_here
PREFIX=,
ADMIN_IDS=123456789,987654321
```

5. **Run the bot**
```bash
python main.py
```

The bot should now be online!

## VPS Deployment

### Prerequisites
- Ubuntu/Debian VPS with SSH access
- Root or sudo access
- Domain name (optional, for webhooks)

### Installation Steps

1. **Connect to your VPS**
```bash
ssh user@your-vps-ip
```

2. **Update system packages**
```bash
sudo apt update && sudo apt upgrade -y
```

3. **Install Python 3.9+**
```bash
sudo apt install python3 python3-pip python3-venv git -y
```

4. **Clone the repository**
```bash
cd ~
git clone <your-repo-url>
cd discord-economy-bot
```

5. **Setup virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

6. **Configure the bot**
```bash
cp .env.example .env
nano .env  # Edit with your values
```

7. **Setup systemd service for auto-restart**

Create service file:
```bash
sudo nano /etc/systemd/system/economy-bot.service
```

Add this content:
```ini
[Unit]
Description=Discord Economy Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/home/your-username/discord-economy-bot
Environment="PATH=/home/your-username/discord-economy-bot/venv/bin"
ExecStart=/home/your-username/discord-economy-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

8. **Start the service**
```bash
sudo systemctl daemon-reload
sudo systemctl enable economy-bot
sudo systemctl start economy-bot
```

9. **Check status**
```bash
sudo systemctl status economy-bot
```

10. **View logs**
```bash
sudo journalctl -u economy-bot -f
```

## Docker Deployment

### Prerequisites
- Docker installed
- Docker Compose (optional)

### Using Docker

1. **Create Dockerfile**

Create `Dockerfile` in the project root:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy bot files
COPY . .

# run the bot
CMD ["python", "main.py"]
```

2. **Create docker-compose.yml**
```yaml
version: '3.8'

services:
  bot:
    build: .
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./economy.db:/app/economy.db
      - ./bot.log:/app/bot.log
```

3. **Build and run**
```bash
docker-compose up -d
```

4. **View logs**
```bash
docker-compose logs -f
```

5. **Stop the bot**
```bash
docker-compose down
```

## Cloud Platform Deployment

### Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repository
4. Add environment variables in the "Variables" tab
5. Railway will automatically detect Python and deploy

### Heroku

1. Install Heroku CLI
2. Login to Heroku:
```bash
heroku login
```

3. Create a new app:
```bash
heroku create your-bot-name
```

4. Add Procfile:
```
worker: python main.py
```

5. Set environment variables:
```bash
heroku config:set DISCORD_TOKEN=your_token
heroku config:set GUILD_ID=your_guild_id
```

6. Deploy:
```bash
git push heroku main
```

7. Scale the worker:
```bash
heroku ps:scale worker=1
```

### DigitalOcean App Platform

1. Go to DigitalOcean App Platform
2. Click "Create App"
3. Select your GitHub repository
4. Configure the app:
   - Type: Worker
   - Run Command: `python main.py`
5. Add environment variables
6. Click "Deploy"

## Production Considerations

### Security

1. **Never commit .env file**
   - Add `.env` to `.gitignore`
   - Use environment variables or secrets managers

2. **Use strong bot token**
   - Keep it private
   - Regenerate if exposed

3. **Limit bot permissions**
   - Only grant necessary permissions
   - Use slash commands for better security

### Performance

1. **Database optimization**
   - For high traffic, consider PostgreSQL
   - Regular backups
   - Indexed queries

2. **Caching**
   - Cache frequently accessed data
   - Use Redis for distributed caching

3. **Rate limiting**
   - Implement per-user cooldowns
   - Global rate limits for expensive operations

### Monitoring

1. **Logging**
   - Centralized logging (e.g., Logtail, Papertrail)
   - Error tracking (e.g., Sentry)

2. **Uptime monitoring**
   - Use services like UptimeRobot
   - Set up alerts for downtime

3. **Resource monitoring**
   - CPU and memory usage
   - Database size
   - API rate limits

### Backups

1. **Database backups**
```bash
# Backup SQLite
cp economy.db economy.db.backup

# Automated backup script
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
cp economy.db "$BACKUP_DIR/economy_$DATE.db"

# Keep only last 7 days
find "$BACKUP_DIR" -name "economy_*.db" -mtime +7 -delete
```

2. **Setup cron job for automatic backups**
```bash
crontab -e

# Add this line for daily backups at 3 AM
0 3 * * * /path/to/backup_script.sh
```

### Scaling

1. **Horizontal scaling**
   - Multiple bot instances with shared database
   - Load balancing

2. **Database scaling**
   - Move to PostgreSQL
   - Read replicas for queries
   - Connection pooling

## Troubleshooting

### Bot won't start

1. Check Python version: `python --version`
2. Verify dependencies: `pip install -r requirements.txt`
3. Check logs: `tail -f bot.log`
4. Verify token in `.env`

### Commands not working

1. Check bot permissions
2. Sync slash commands manually
3. Verify intents are enabled in Discord Developer Portal
4. Check command prefixes

### Database errors

1. Check file permissions
2. Verify database file exists
3. Check disk space
4. Backup and recreate if corrupted

### High memory usage

1. Check for memory leaks
2. Restart bot periodically
3. Optimize database queries
4. Implement caching

## Support

For issues and questions:
- Open an issue on GitHub
- Join our Discord server
- Check the documentation

## Updates

To update the bot:

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the bot
sudo systemctl restart economy-bot  # For systemd
# OR
docker-compose restart  # For Docker
```

Remember to backup your database before updating!
