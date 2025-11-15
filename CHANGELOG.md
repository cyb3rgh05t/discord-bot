# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.0.3] - 2025-11-15

### Fixed

- GitHub Actions workflow release tagging
  - Added conditional enable for semver patterns to prevent failures on non-release events
  - Semver tags now only generated for release events
  - Workflow dispatch and branch events no longer cause semver pattern errors

## [4.0.2] - 2025-11-15

### Added

- Automatic database initialization on bot startup
  - Invites database (invites.db)
  - Ticket system database (ticket_system.db)
  - Plex clients database (plex_clients.db)
- ANNOUNCEMENT_ROLE setting for auto-assignment during verification
- Multi-role assignment on CAPTCHA verification
  - Verified role
  - Member role
  - Announcement role (new)
- Improved database initialization logging (no emojis, cleaner output)

### Changed

- Plex user count now sourced from invites database (active status) instead of Plex API friends list
- Database initialization moved to centralized bot startup process
- Test ticket line identifier changed from lowercase to uppercase (test-line → TEST-LINE)
- GitHub Actions workflow updated for better branch handling
  - Main branch: version tags + latest tag
  - Dev/other branches: branch name tags only
  - Improved caching strategy for faster builds
- Suppressed Werkzeug development server logs for cleaner console output

### Removed

- LIVE_TICKET setting (unused/obsolete)
- PLEX_TICKET_CATEGORY_ID setting (replaced by database configuration)
- TV_TICKET_CATEGORY_ID setting (replaced by database configuration)
- DEFAULT_STAFF_ROLE setting (replaced by database configuration)
- All emojis from README.md for cleaner professional appearance

### Fixed

- Database initialization now ensures all tables exist before bot operations
- Settings example file updated to match current configuration structure

### Documentation

- Updated README.md with centered documentation links
- Added prominent API Reference, Changelog, and License links at top of README
- Improved professional appearance without emoji clutter

## [4.0.1] - 2025-11-15

### Added

- Web Dashboard UI with comprehensive management features
  - Real-time bot monitoring with auto-refresh (30s intervals)
  - Database browser with hierarchical navigation and query executor
  - Ticket management system with search and filtering
  - Invite tracking and analytics
  - Settings management interface with auto-save functionality
  - About page with version tracking and system information
  - Service status monitoring for Plex and other integrations
- Version checking system against GitHub releases
- Mobile-responsive design with adaptive navigation
- Dark theme optimized for readability
- Discord bot icon as favicon
- Auto-save toggle for settings with enable/disable control
- Ko-fi webhook multi-language support
  - Custom messages per language (EN, DE, FR)
  - Custom footers per language (EN, DE, FR)
- New admin commands:
  - `!clearguild` - Clear guild-specific commands to remove duplicates
- Database table view improvements:
  - Expandable/collapsible schema section (collapsed by default)
  - Reordered cards (data first, schema second)
  - Back button in header matching tickets view style

### Changed

- Updated Docker configuration
  - Added port 5000 for Web Dashboard
  - Added version.txt to Docker image for version tracking
  - Updated Traefik routing for both web UI and webhook
    - Web UI: `https://bot.${DOMAIN}/` (port 5000, with Authelia auth)
    - Webhook: `https://bot.${DOMAIN}/webhook` (port 3033, no auth)
- Command sync strategy
  - Changed from dual sync (guild + global) to global-only sync
  - Fixes duplicate command issue
  - Enables DM functionality for commands like `/plex-walkthrough`
- Settings UI improvements
  - Form actions card now right-aligned with no separator line
  - Ko-fi settings split into language-specific fields
  - Better mobile responsiveness
- Database view navigation changed from modal to dedicated page (tickets-style)
- README updated with Web Dashboard documentation and features

### Fixed

- Bot status card in About page now displays correct values
  - Uptime display working
  - Latency showing with "ms" unit
  - Guild count displaying correctly
  - User count displaying correctly
- Duplicate Discord slash commands removed
- Form separator lines removed from settings page
- Ko-fi webhook compatibility maintained with new routing
- Mobile navigation hamburger menu conditional display

### Technical

- Flask 3.0.0 web framework with blueprints architecture
- SQLite database browser with schema viewer
- AJAX for dynamic content loading
- CSS Grid/Flexbox responsive layouts
- Media queries at 768px breakpoint
- GitHub API integration for version checking
- Jinja2 templating with dark theme variables

## [4.0.0] - Previous Release

Initial major release with core bot functionality.

[4.0.1]: https://github.com/cyb3rgh05t/discord-bot/compare/v4.0.0...v4.0.1
[4.0.0]: https://github.com/cyb3rgh05t/discord-bot/releases/tag/v4.0.0
