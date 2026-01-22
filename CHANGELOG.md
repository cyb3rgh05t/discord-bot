# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.2.0] - 2025-11-17

### Added

- Global notification system across all web UI pages
  - Unified notification component in base template
  - Color-coded notifications with transparency: success (green), error (red), warning (orange), info (blue)
  - Slide-in animation from right with auto-dismiss after 3 seconds
  - Progress bar indicator showing remaining time
  - Replaced all alert() popups with styled notifications
- Success notifications for user actions
  - Invite removal: "Invite removed successfully"
  - Ticket closing: "Ticket closed successfully"
  - Role management: "Role added/removed successfully"
- Automatic Plex role removal on invite deletion
  - Discord Plex role is automatically removed when deleting an invite via web UI
  - Handles various Discord user ID formats in invite records
  - Logs warnings for role removal failures while still deleting the invite
- Enhanced ticket closing functionality
  - Full Discord channel closing when closing tickets via web UI
  - Automatic transcript generation matching Discord bot behavior
  - Transcript sent to designated channel and ticket creator via DM
  - Channel deletion after 5-second delay
  - Comprehensive debug logging for troubleshooting

### Changed

- Settings page action buttons card redesign
  - Removed unnecessary nested wrappers causing visual separators
  - Created custom `actions-bar` class replacing generic card styling
  - Simplified structure for cleaner appearance
  - Eliminated unwanted header separator line
- Members page notification styling
  - Updated to use global notification system
  - Removed duplicate notification code
  - Consistent theming with rest of application
- Invite removal behavior
  - Now returns invite data before deletion for role removal processing
  - Modified database helper to return invite details
  - Added 1-second delay before page reload to show success notification

### Fixed

- Notification appearance inconsistencies
  - Members page notifications now match global theme
  - All notifications use CSS variables for consistent theming
  - Border colors properly applied across all notification types

## [4.1.2] - 2025-11-16

### Changed

- Log color scheme for better readability
  - INFO messages now display in blue (previously green)
  - DEBUG messages now display in green (previously blue)
  - ERROR messages remain red
  - WARNING messages remain yellow
  - CRITICAL messages remain red with bold formatting

## [4.1.1] - 2025-11-16

### Fixed

- Web UI startup failure
  - Fixed `WEB_DEBUG` import error in `bot.py` (setting was renamed to `WEB_VERBOSE_LOGGING`)
  - Corrected import statement and usage in Flask's `run_simple()` debugger parameter
  - Web UI now starts correctly on bot launch
- Members management role removal functionality
  - Fixed `remove_role_from_member()` function logic (was adding roles instead of removing)
  - Corrected role check condition to verify member has the role before removal
  - Fixed success message to show "Removed" instead of "Added"
  - Renamed internal async function from `add_role_async()` to `remove_role_async()`
  - Added missing `current_app` import for logging
- GitHub webhook avatar URLs
  - Fixed incorrect URL path using `${{ github.repository }}` variable
  - Corrected both `avatar_url` and `footer_icon_url` to use hardcoded repository path
- Code cleanup
  - Removed unused `concurrent.futures` imports from role management functions

## [4.1.0] - 2025-11-16

### Added

- Comprehensive Plex operation logging system
  - User tracking: Logs Discord username and ID for all Plex invite/remove requests
  - Email validation logging with detailed pass/fail indicators
  - Library sharing details: Shows which Plex libraries are shared during invites
  - Database operation tracking: Logs all save, retrieve, update, and delete operations
  - Process flow logging: Tracks each step of invite and removal workflows
  - Standardized log prefixes: [PLEX], [PLEX INVITE], [PLEX REMOVE], [PLEX DB]
  - SUCCESS/FAILED indicators for quick log scanning and troubleshooting
  - Configuration validation logging with warnings for missing Plex setup

### Changed

- Simplified database path configuration by hardcoding "databases" directory
  - Removed DATABASE_PATH setting from settings.py and settings.py.example
  - Hardcoded database path across all modules for consistency
  - Updated 8 files: web utilities, database initialization, and ticket system
  - Eliminates configuration complexity while maintaining standard project structure

### Fixed

- Log file formatting with ANSI color codes
  - Implemented dual formatter system for logging
  - Console output: Colorful formatting with ANSI codes for easy visual scanning
  - File output: Clean plain text without ANSI codes for parsing and archival
  - StreamlinedFormatter now accepts use_colors parameter (True for console, False for file)
  - Separate formatters applied to console handlers and file handlers
  - Log files now readable and parseable without color code clutter

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
