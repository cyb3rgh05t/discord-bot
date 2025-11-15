# API Reference

Complete documentation of all commands, slash commands, and API endpoints available in the Discord Bot.

## Table of Contents

- [Web UI Endpoints](#web-ui-endpoints)
- [API Endpoints](#api-endpoints)
- [Discord Prefix Commands](#discord-prefix-commands)
- [Discord Slash Commands](#discord-slash-commands)
- [Ko-fi Webhook](#ko-fi-webhook)

---

## Web UI Endpoints

Base URL: `http://localhost:5000` (or your configured host/port)

### Dashboard

| Endpoint | Method | Description                                    | Auth Required |
| -------- | ------ | ---------------------------------------------- | ------------- |
| `/`      | GET    | Main dashboard with bot status and quick stats | Yes           |

### Tickets

| Endpoint                     | Method | Description                                      | Auth Required |
| ---------------------------- | ------ | ------------------------------------------------ | ------------- |
| `/tickets/`                  | GET    | List all support tickets with search and filters | Yes           |
| `/tickets/<ticket_id>`       | GET    | View detailed ticket information                 | Yes           |
| `/tickets/<ticket_id>/close` | POST   | Close a specific ticket                          | Yes           |

### Invites

| Endpoint                      | Method | Description                     | Auth Required |
| ----------------------------- | ------ | ------------------------------- | ------------- |
| `/invites/`                   | GET    | View and manage server invites  | Yes           |
| `/invites/add`                | POST   | Add a new invite tracking entry | Yes           |
| `/invites/<invite_id>/remove` | POST   | Remove an invite from tracking  | Yes           |

### Databases

| Endpoint                                   | Method | Description                                | Auth Required |
| ------------------------------------------ | ------ | ------------------------------------------ | ------------- |
| `/databases/`                              | GET    | Browse all SQLite databases                | Yes           |
| `/databases/table/<table_name>`            | GET    | View table schema and data with pagination | Yes           |
| `/databases/query`                         | POST   | Execute custom SQL query                   | Yes           |
| `/databases/schema/<db_name>/<table_name>` | GET    | Get table schema information               | Yes           |

### Settings

| Endpoint                | Method | Description                               | Auth Required |
| ----------------------- | ------ | ----------------------------------------- | ------------- |
| `/settings/`            | GET    | View bot configuration settings           | Yes           |
| `/settings/edit`        | POST   | Update bot settings (auto-save or manual) | Yes           |
| `/settings/restart-bot` | POST   | Restart the Discord bot                   | Yes           |

### Services

| Endpoint               | Method | Description                      | Auth Required |
| ---------------------- | ------ | -------------------------------- | ------------- |
| `/services/`           | GET    | View service status (Plex, etc.) | Yes           |
| `/services/api/status` | GET    | Get service status as JSON       | Yes           |
| `/services/restart`    | POST   | Restart a specific service       | Yes           |

### About

| Endpoint  | Method | Description                              | Auth Required |
| --------- | ------ | ---------------------------------------- | ------------- |
| `/about/` | GET    | Bot information, version, system details | Yes           |

---

## API Endpoints

Base URL: `http://localhost:5000/api`

### Bot Status & Stats

| Endpoint             | Method | Response | Description                                           |
| -------------------- | ------ | -------- | ----------------------------------------------------- |
| `/api/bot-status`    | GET    | JSON     | Current bot online status, latency, uptime            |
| `/api/bot-stats`     | GET    | JSON     | Bot statistics (uptime, latency, guilds, users, etc.) |
| `/api/version`       | GET    | JSON     | Current version and latest GitHub release info        |
| `/api/check-updates` | GET    | JSON     | Check if updates are available                        |

#### Example Responses

**GET /api/bot-status**

```json
{
  "online": true,
  "latency": 45.23,
  "uptime": "2d 5h 30m 15s",
  "guilds": 3,
  "users": 1250
}
```

**GET /api/bot-stats**

```json
{
  "uptime": "2d 5h 30m 15s",
  "latency": "45.23ms",
  "guild_count": 3,
  "user_count": 1250,
  "commands": 15,
  "channels": 48,
  "roles": 23
}
```

**GET /api/version**

```json
{
  "current_version": "4.0.1",
  "latest_version": "4.0.1",
  "update_available": false,
  "release_url": "https://github.com/cyb3rgh05t/discord-bot/releases/tag/v4.0.1"
}
```

---

## Discord Prefix Commands

Default prefix: `!` (configurable in settings)

### Bot Management Commands

| Command          | Parameters | Description                                            | Permissions   |
| ---------------- | ---------- | ------------------------------------------------------ | ------------- |
| `!sync`          | None       | Manually sync slash commands to current guild          | Administrator |
| `!syncglobal`    | None       | Manually sync global slash commands (for DM support)   | Owner Only    |
| `!clearguild`    | None       | Clear all guild-specific commands to remove duplicates | Owner Only    |
| `!list_guilds`   | None       | List all guilds the bot is in                          | Any           |
| `!list_commands` | None       | List all registered slash commands                     | Any           |
| `!list_cogs`     | None       | List all loaded cogs/modules                           | Any           |

### Server Setup Commands

| Command       | Parameters | Description                                 | Permissions   |
| ------------- | ---------- | ------------------------------------------- | ------------- |
| `!serverinfo` | None       | Create or update server information message | Administrator |
| `!verify`     | None       | Setup member verification system            | Administrator |
| `!welcome`    | None       | Setup welcome message in welcome channel    | Administrator |
| `!rules`      | None       | Post server rules message                   | Administrator |

### Channel Message Commands

| Command            | Parameters | Description                          | Permissions   |
| ------------------ | ---------- | ------------------------------------ | ------------- |
| `!channelsmessage` | None       | Send TV channels information message | Administrator |
| `!plexmessage`     | None       | Send Plex channel setup message      | Administrator |
| `!tvmessage`       | None       | Send LiveTV channel message          | Administrator |
| `!appstore`        | None       | Send App Store channel message       | Administrator |
| `!invitemessage`   | None       | Send invite information message      | Administrator |
| `!donatemessage`   | None       | Send donation channel message        | Administrator |
| `!paylink`         | None       | Send donation payment links          | Administrator |
| `!thankyou`        | None       | Send thank-you message for donations | Administrator |

### Ticket Setup Commands

| Command               | Parameters | Description                    | Permissions   |
| --------------------- | ---------- | ------------------------------ | ------------- |
| `!plexticketsmessage` | None       | Send Plex ticket setup message | Administrator |
| `!tvticketsmessage`   | None       | Send TV ticket setup message   | Administrator |

### Moderation Commands

| Command  | Parameters | Description                    | Permissions   |
| -------- | ---------- | ------------------------------ | ------------- |
| `!lines` | None       | Add decorative separator lines | Administrator |

---

## Discord Slash Commands

### General Commands

| Command | Parameters | Description                           | Permissions |
| ------- | ---------- | ------------------------------------- | ----------- |
| `/ping` | None       | Check bot's latency and response time | Everyone    |

### Member Management

| Command | Parameters     | Description                   | Permissions  |
| ------- | -------------- | ----------------------------- | ------------ |
| `/kick` | `member: User` | Kick a member from the server | Kick Members |

### Ticket System

| Command               | Parameters                                    | Description                      | Permissions   |
| --------------------- | --------------------------------------------- | -------------------------------- | ------------- |
| `/setup-plex-tickets` | `category: TextChannel`<br>`staff_role: Role` | Setup Plex support ticket system | Administrator |
| `/setup-tv-tickets`   | `category: TextChannel`<br>`staff_role: Role` | Setup TV support ticket system   | Administrator |

### Plex Commands

All Plex commands are under the `/plex` command group.

#### Plex Setup & Configuration

| Command            | Parameters            | Description                                       | Permissions   |
| ------------------ | --------------------- | ------------------------------------------------- | ------------- |
| `/plex setup`      | None                  | Initial Plex integration setup wizard             | Administrator |
| `/plex set-server` | `server_name: String` | Set Plex server name                              | Administrator |
| `/plex set-roles`  | `roles: String`       | Set roles eligible for Plex (comma-separated)     | Administrator |
| `/plex set-libs`   | `libraries: String`   | Set libraries to share ("all" or comma-separated) | Administrator |
| `/plex enable`     | None                  | Enable Plex integration                           | Administrator |
| `/plex disable`    | None                  | Disable Plex integration                          | Administrator |

#### Plex User Management

| Command        | Parameters                        | Description                     | Permissions |
| -------------- | --------------------------------- | ------------------------------- | ----------- |
| `/plex invite` | `member: User`<br>`email: String` | Invite a user to Plex server    | Staff Role  |
| `/plex remove` | `member: User`                    | Remove a user from Plex server  | Staff Role  |
| `/plex dbls`   | None                              | List all users in Plex database | Staff Role  |
| `/plex dbadd`  | `member: User`<br>`email: String` | Add user to Plex database       | Staff Role  |
| `/plex dbdel`  | `member: User`                    | Delete user from Plex database  | Staff Role  |

#### Plex Walkthrough (DM-Enabled)

| Command             | Parameters | Description                                 | Permissions | DM Support |
| ------------------- | ---------- | ------------------------------------------- | ----------- | ---------- |
| `/plex-walkthrough` | None       | Interactive Plex setup guide (works in DMs) | Everyone    | ✅ Yes     |

This command provides:

- Step-by-step Plex account setup
- Email verification
- Server invitation process
- Troubleshooting help

---

## Ko-fi Webhook

Base URL: `http://localhost:3033` (or your configured port)

### Webhook Endpoints

| Endpoint   | Method | Description                                 | Auth               |
| ---------- | ------ | ------------------------------------------- | ------------------ |
| `/`        | GET    | Health check - shows webhook service status | None               |
| `/health`  | GET    | Health check endpoint                       | None               |
| `/webhook` | GET    | Show webhook status and info                | None               |
| `/webhook` | POST   | Receive Ko-fi donation notifications        | Verification Token |

### Ko-fi Webhook Configuration

#### Required Headers

- `Content-Type`: `application/x-www-form-urlencoded` or `application/json`

#### Verification

- Uses `KOFI_VERIFICATION_TOKEN` from settings for security

#### Webhook URL Setup

Configure in Ko-fi Dashboard:

```
https://bot.yourdomain.com/webhook
```

Or with Traefik:

```
https://bot.${DOMAIN}/webhook
```

#### Supported Languages

- English (`en`)
- German (`de`)
- French (`fr`)

#### Donation Types Supported

- One-time donations
- Subscriptions
- Shop purchases

#### Example Ko-fi Payload

```json
{
  "verification_token": "your-token-here",
  "message_id": "12345678-1234-1234-1234-123456789012",
  "timestamp": "2025-11-15T10:30:00Z",
  "type": "Donation",
  "is_public": true,
  "from_name": "John Doe",
  "message": "Keep up the great work!",
  "amount": "5.00",
  "url": "https://ko-fi.com/Transaction/12345",
  "email": "supporter@example.com",
  "currency": "USD",
  "is_subscription_payment": false,
  "is_first_subscription_payment": false,
  "kofi_transaction_id": "12345678-1234-1234-1234-123456789012"
}
```

---

## Authentication

### Web UI Authentication

The Web UI supports optional built-in authentication or can use reverse proxy authentication (e.g., Authelia).

**Settings:**

- `WEB_AUTH_ENABLED`: Enable/disable built-in auth
- `WEB_USERNAME`: Admin username (if enabled)
- `WEB_PASSWORD`: Admin password (if enabled)

**Default Credentials:**

- Username: `admin`
- Password: `changeme`

⚠️ **Security Note:** Change default credentials before deploying to production!

### Discord Command Permissions

Commands use Discord's built-in permission system:

- **Owner Only**: Requires bot owner (from Discord application settings)
- **Administrator**: Requires Administrator permission
- **Staff Role**: Requires configured staff role
- **Specific Permissions**: Requires permissions like "Kick Members"

---

## Rate Limiting

### Web UI

- No built-in rate limiting by default
- Can be configured via reverse proxy (recommended)

### Discord Commands

- Subject to Discord's global rate limits
- 50 slash command interactions per second
- Additional rate limits per command type

### API Endpoints

- No built-in rate limiting
- Auto-refresh on dashboard: 30 seconds

---

## Error Responses

### Web UI Errors

| Status Code | Description                      |
| ----------- | -------------------------------- |
| 200         | Success                          |
| 302         | Redirect (after form submission) |
| 401         | Unauthorized (login required)    |
| 404         | Page not found                   |
| 500         | Internal server error            |

### API Errors

```json
{
  "error": "Error description",
  "success": false
}
```

### Discord Command Errors

Commands respond with error messages directly in Discord:

- Permission errors
- Invalid parameters
- Bot configuration issues
- External service failures (Plex, etc.)

---

## Versioning

Current Version: **4.0.1**

Version format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Check version via:

- Web UI: About page
- API: `/api/version`
- File: `version.txt`

---

## Support & Documentation

- **GitHub Repository**: https://github.com/cyb3rgh05t/discord-bot
- **Issues**: https://github.com/cyb3rgh05t/discord-bot/issues
- **Changelog**: See `CHANGELOG.md`
- **License**: MIT License

---

_Last Updated: November 15, 2025 - Version 4.0.1_
