# Discord Bot

A feature-rich Discord bot written in Python with support for ticketing, Plex integration, Ko-fi webhooks, and moderation tools.

<div align="center">

![GitHub release](https://img.shields.io/github/v/release/cyb3rgh05t/discord-bot?style=for-the-badge)
![GitHub stars](https://img.shields.io/github/stars/cyb3rgh05t/discord-bot?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/cyb3rgh05t/discord-bot?style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/cyb3rgh05t/discord-bot?style=for-the-badge)
![GitHub license](https://img.shields.io/github/license/cyb3rgh05t/discord-bot?style=for-the-badge)

</div>

## Features

- 🎫 **Ticket System** - Automated support tickets for Plex and TV services
- 🎬 **Plex Integration** - Automatic user management and library sharing
- 💰 **Ko-fi Webhooks** - Real-time donation notifications with multi-language support
- 🔐 **Captcha Verification** - Secure member verification system
- 🛠️ **Moderation Tools** - Comprehensive server management commands
- 📝 **Custom Logos & Embeds** - Branded channel setup and server customization
- 🤖 **Slash & Prefix Commands** - Modern slash commands with legacy prefix support
- 🌐 **Web Dashboard** - Comprehensive web interface for bot management and monitoring

## Web Dashboard

The bot includes a modern, mobile-responsive web dashboard with the following features:

### Dashboard Features

- **Real-time Bot Monitoring** - Live bot status, uptime, and system statistics with auto-refresh
- **Ticket Management** - View, search, filter, and manage support tickets
- **Database Browser** - Explore and query SQLite databases with hierarchical navigation
- **Invite Tracking** - Monitor server invites and usage analytics
- **Settings Management** - Configure bot settings through an intuitive interface
- **Service Status** - Monitor Plex and other integrated services
- **About Page** - Bot information, version tracking, and system details

### Web UI Features

- 🎨 **Dark Theme** - Modern dark interface optimized for readability
- 📱 **Mobile Responsive** - Fully functional on desktop, tablet, and mobile devices
- 🔄 **Auto Version Checking** - Automatic GitHub release version comparison
- 🔍 **Advanced Search** - Filter and search across all data views
- 📊 **Live Updates** - Real-time dashboard updates without page refresh
- 🗃️ **Database Tools** - Query executor and schema viewer for database management

### Accessing the Web Dashboard

The dashboard is accessible at `http://your-server:5000` once the bot is running. The web interface runs alongside the Discord bot automatically.

## Requirements

- Python 3.12+
- Discord Bot Token
- (Optional) Plex Media Server
- (Optional) Ko-fi account for donations

## Installation

### Using Docker (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/cyb3rgh05t/discord-bot.git
cd discord-bot
```

2. Configure settings:

```bash
cp config/settings.py.example config/settings.py
```

Edit `config/settings.py` with your configuration.

3. Run with Docker Compose:

```bash
docker-compose up -d
```

### Manual Installation

1. Clone the repository:

```bash
git clone https://github.com/cyb3rgh05t/discord-bot.git
cd discord-bot
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Configure settings:

```bash
cp config/settings.py.example config/settings.py
```

Edit `config/settings.py` with your configuration.

5. Run the bot:

```bash
python bot.py
```

## Configuration

### Required Settings

Edit `config/settings.py` with the following required values:

```python
BOT_TOKEN = "your_discord_bot_token"
GUILD_ID = "your_server_id"
COMMAND_PREFIX = "!"  # Default command prefix
```

### Optional: Plex Integration

```python
PLEX_ENABLED = True
PLEX_TOKEN = "your_plex_token"
PLEX_BASE_URL = "http://your-plex-server:32400"
PLEX_SERVER_NAME = "Your Server Name"
PLEX_ROLES = "member"  # Roles eligible for Plex access
PLEX_LIBS = "all"  # Libraries to share
```

### Optional: Ko-fi Webhooks

```python
KOFI_WEBHOOK_PORT = 3033
KOFI_VERIFICATION_TOKEN = "your_kofi_verification_token"
KOFI_CHANNEL_ID = 123456789012345678
KOFI_NAME = "Your Ko-fi Name"
KOFI_LANGUAGE = "en"  # Supported: 'en', 'de', 'fr'
```

### Channel & Role Configuration

```python
WELCOME_CHANNEL_ID = 123456789012345678
SYSTEM_CHANNEL_ID = 123456789012345678
TICKET_CATEGORY_ID = 123456789012345678
RULES_CHANNEL_ID = 123456789012345678

UNVERIFIED_ROLE = "unverified"
VERIFIED_ROLE = "verified"
MEMBER_ROLE = "member"
STAFF_ROLE = "staff"
```

## Commands

### Slash Commands

- `/ping` - Check bot latency
- `/kick` - Kick a member (requires permissions)
- `/plex` - Plex management commands
- `/ticket` - Create support tickets

### Prefix Commands (Default: `!`)

**Moderation:**

- `!verify` - Setup verification system
- `!rules` - Manage server rules
- `!channels` - Channel management

**Logos & Branding:**

- `!welcome` - Set welcome channel logo
- `!plex` - Set Plex channel logo
- `!donate` - Set donation channel logo

## Ko-fi Webhook Setup

1. Configure Ko-fi settings in `config/settings.py`
2. Start the bot (webhook server runs on configured port)
3. In your Ko-fi settings, add webhook URL:
   ```
   http://your-server-ip:3033/kofi-webhook
   ```
4. Set the verification token in both Ko-fi and your config

The bot will post donation notifications to the configured channel with:

- Donor information
- Amount and type (one-time/subscription)
- Custom message support
- Multi-language support (EN, DE, FR)

## Docker Support

The bot includes full Docker support with:

- Multi-stage builds for efficiency
- Python 3.14 slim base image
- Automatic restart policies
- Volume mounts for persistent data
- Integrated web dashboard on port 5000

### Docker Environment

The Docker container includes:

- Discord bot functionality
- Web dashboard server
- Database persistence
- Automatic version tracking
- Log file management

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop bot
docker-compose down

# Access web dashboard
# Navigate to http://localhost:5000 in your browser
```

### Port Configuration

- **Port 5000** - Web Dashboard (HTTP)
- **Port 3033** - Ko-fi Webhook (if enabled)

Make sure these ports are exposed in your `docker-compose.yml`:

```yaml
ports:
  - "5000:5000" # Web Dashboard
  - "3033:3033" # Ko-fi Webhook (optional)
```

## Logging

Logs are stored in the `logs/` directory with configurable levels:

- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages
- `ERROR` - Error messages
- `CRITICAL` - Critical issues

Set logging level in `config/settings.py`:

```python
LOGGING_LEVEL = "INFO"
LOG_FILE = "logs/bot.log"
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

##

<div align="center">

**Created with ❤️ by [cyb3rgh05t](https://github.com/cyb3rgh05t) for the Community**

If you find this project useful, please consider giving it a ⭐!

[Report Bug](https://github.com/cyb3rgh05t/discord-bot/issues) · [Request Feature](https://github.com/cyb3rgh05t/discord-bot/issues) · [Documentation](https://cyb3rgh05t.github.io/discord-bot/)

</div>
