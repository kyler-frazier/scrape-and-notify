# Web Scraper with Notifications

A Python-based web scraper that monitors specific websites for target content and sends notifications when found.

## Features

- 🔍 **Web Scraping**: Monitor any website for specific text or HTML elements
- 📧 **Email Notifications**: Get notified via email when target content is found
- 🔗 **Webhook Support**: Send notifications to custom webhooks
- 💬 **Slack Integration**: Send alerts to Slack channels
- 🐳 **Dockerized**: Easy deployment with Docker and docker-compose
- ⚙️ **Configurable**: Flexible configuration via environment variables
- 📝 **Logging**: Comprehensive logging to files and console

## Quick Start

### Prerequisites

- Python 3.10+
- Poetry
- Docker and docker-compose

### Setup

1. **Clone and enter the project directory**:
   ```bash
   cd scrape-and-notify
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **Configure your scraper**:
   Create a `.env` file based on the configuration options in `src/config.py`:
   ```bash
   # Required
   TARGET_URL=https://example.com
   TARGET_TEXT=your target text here
   
   # Optional - Email notifications
   EMAIL_USER=your-email@gmail.com
   EMAIL_PASSWORD=your-app-password
   EMAIL_RECIPIENT=recipient@email.com
   
   # Optional - Slack notifications
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
   
   # Optional - Custom webhook
   WEBHOOK_URL=https://your-webhook-endpoint.com/webhook
   ```

4. **Update the target configuration**:
   Edit `src/main.py` to set your specific URL and target text, or use environment variables.

### Running the Application

#### Option 1: With Docker (Recommended)

```bash
# Build and run with docker-compose
docker-compose up --build

# Run in the background
docker-compose up -d --build
```

#### Option 2: With Poetry

```bash
# Run directly
poetry run python src/main.py

# Or activate the virtual environment first
poetry shell
python src/main.py
```

## Configuration

All configuration is handled through environment variables. Key settings include:

| Variable | Description | Default |
|----------|-------------|---------|
| `TARGET_URL` | Website to monitor | `https://example.com` |
| `TARGET_TEXT` | Text to search for | `target text` |
| `CHECK_INTERVAL` | Seconds between checks | `3600` (1 hour) |
| `EMAIL_USER` | Email username | None |
| `EMAIL_PASSWORD` | Email password/app password | None |
| `EMAIL_RECIPIENT` | Email recipient | None |
| `SLACK_WEBHOOK_URL` | Slack webhook URL | None |
| `WEBHOOK_URL` | Custom webhook URL | None |

## Project Structure

```
├── src/
│   ├── main.py          # Main application entry point
│   ├── scraper.py       # Web scraping functionality
│   ├── notifier.py      # Notification handling
│   └── config.py        # Configuration management
├── logs/                # Log files (created automatically)
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── pyproject.toml       # Poetry dependencies
└── ruff.toml           # Code formatting configuration
```

## Notifications

The scraper supports multiple notification methods:

### Email
Configure email notifications using Gmail or any SMTP server:
- Set `EMAIL_USER`, `EMAIL_PASSWORD`, and `EMAIL_RECIPIENT`
- For Gmail, use an app password instead of your regular password

### Slack
Create a Slack webhook and set `SLACK_WEBHOOK_URL`

### Custom Webhooks
Set `WEBHOOK_URL` to send JSON payloads to any endpoint

### Console/File Logging
All notifications are logged to both console and `logs/scraper.log`

## Development

### Code Formatting
```bash
# Format code with ruff
poetry run ruff format

# Check for issues
poetry run ruff check

# Fix auto-fixable issues
poetry run ruff check --fix
```

### Docker Development
For development with live code reloading, uncomment the volume mount in `docker-compose.yml`:
```yaml
volumes:
  - .:/app
  - ./logs:/app/logs
```

## Customization

### Different Scraping Methods
The `WebScraper` class supports:
- Text search: `check_for_text(url, text)`
- CSS selector search: `check_for_element(url, selector)`

### Adding New Notification Methods
Extend the `Notifier` class in `src/notifier.py` to add new notification channels.

## Security Notes

- Never commit `.env` files with real credentials
- For production, use proper secrets management
- Consider using app passwords for email instead of regular passwords
- Be respectful with scraping frequency to avoid being blocked

## License

[Add your license information here] 