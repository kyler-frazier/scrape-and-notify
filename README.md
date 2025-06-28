# Web Scraper with Notifications

A Python-based web scraper that monitors specific websites for target content and sends notifications when found.

## Features

- 🔍 **Web Scraping**: Monitor any website for specific text or JSON content
- 🎯 **Flexible Search**: Support for both HTML text search and JSON path queries
- 💬 **Discord Integration**: Send alerts to Discord channels via bot
- 🐳 **Dockerized**: Easy deployment with Docker Compose (recommended)
- ⚙️ **Configurable**: Flexible configuration via environment variables
- 📝 **Logging**: Comprehensive logging to files and console

## Quick Start

### Prerequisites

- Docker and Docker Compose (recommended)
- Python 3.10+ and Poetry (alternative)

### Setup

1. **Clone and enter the project directory**:
   ```bash
   cd scrape-and-notify
   ```

2. **Configure your scraper**:
   Create a `.env` file based on the configuration options below:
   ```bash
   # Required
   TARGET_URL=https://example.com/api/data
   TARGET_MATCH=your target value here
   
   # Search configuration
   SEARCH_TYPE=json  # or 'html'
   TARGET_LOCATION=$.data.status  # JSONPath for JSON search (required for json type)
   
   # Optional - Discord notifications
   DISCORD_BOT_TOKEN=your-discord-bot-token
   DISCORD_CHANNEL_ID=your-discord-channel-id
   
   # Optional - Timing and request settings
   CHECK_INTERVAL=900  # seconds between checks (default: 15 minutes)
   REQUEST_TIMEOUT=30  # request timeout in seconds
   REQUEST_DELAY=1.0   # delay between requests in seconds
   
   # Optional - Logging
   LOG_LEVEL=INFO
   ```

### Running the Application

#### Option 1: With Docker Compose (Recommended)

```bash
# Build and run with docker-compose
docker compose up --build

# Run in the background
docker compose up -d --build
```

#### Option 2: With Poetry (Alternative)

```bash
# Install dependencies
poetry install

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
| `TARGET_URL` | Website or API endpoint to monitor | *Required* |
| `TARGET_MATCH` | Value to search for | *Required* |
| `SEARCH_TYPE` | Search method: `json` or `html` | `json` |
| `TARGET_LOCATION` | JSONPath location for JSON searches | *Required for JSON* |
| `CHECK_INTERVAL` | Seconds between checks | `900` (15 minutes) |
| `REQUEST_TIMEOUT` | Request timeout in seconds | `30` |
| `REQUEST_DELAY` | Delay between requests in seconds | `1.0` |
| `DISCORD_BOT_TOKEN` | Discord bot token for notifications | None |
| `DISCORD_CHANNEL_ID` | Discord channel ID for notifications | None |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### Search Types

- **JSON Search** (`SEARCH_TYPE=json`): Use JSONPath expressions to search within JSON responses
  - Example: `TARGET_LOCATION=$.products[0].availability` 
- **HTML Search** (`SEARCH_TYPE=html`): Search for text content within HTML pages
  - No `TARGET_LOCATION` needed for HTML searches

## Project Structure

```
├── src/
│   └── scrape_and_notify/
│       ├── __init__.py
│       ├── main.py              # Main application entry point
│       ├── scraper.py           # Web scraping functionality
│       ├── notifier.py          # Notification handling
│       ├── config.py            # Configuration management
│       └── logging_formatter.py # Custom logging formatter
├── README.md                    # Project documentation
├── LICENSE                      # MIT License
├── Dockerfile                   # Docker configuration
├── docker-compose.yml           # Docker Compose configuration
├── pyproject.toml              # Poetry dependencies and project config
├── .gitignore                  # Git ignore rules
├── .dockerignore               # Docker ignore rules
└── .cursorignore               # Cursor IDE ignore rules
```

## Notifications

### Discord
To set up Discord notifications:
1. Create a Discord bot in the Discord Developer Portal
2. Add the bot to your server with necessary permissions
3. Set `DISCORD_BOT_TOKEN` and `DISCORD_CHANNEL_ID` in your `.env` file

### Console/File Logging
All notifications and status updates are logged to both console and `logs/scraper.log`

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
For development with live code reloading, you can mount the source code:
```yaml
# Add to docker-compose.yml under the scraper service
volumes:
  - .:/app
  - ./logs:/app/logs
```

## Customization

### Different Scraping Methods
The scraper supports:
- **JSON API monitoring**: Perfect for REST APIs, use JSONPath expressions
- **HTML content monitoring**: Search for text within web pages

### Adding New Notification Methods
Extend the notification system in `src/scrape_and_notify/notifier.py` to add new notification channels.

## Security Notes

- Never commit `.env` files with real credentials
- For production, use proper secrets management
- Store Discord bot tokens securely
- Be respectful with scraping frequency to avoid being blocked
- Consider the website's robots.txt and terms of service

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
