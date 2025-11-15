# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
