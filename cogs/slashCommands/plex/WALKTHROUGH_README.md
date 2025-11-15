# Plex Walkthrough Feature

Inspired by [Wizarr](https://github.com/wizarrrr/wizarr), this feature provides an interactive Plex setup guide for new users.

## Features

### 📚 Three-Step Wizard

1. **Welcome Step** - Introduction to Plex and what users get access to
2. **Download Step** - Links to Plex clients for all platforms (iOS, Android, Desktop, TV, Console, Web)
3. **Tips Step** - Best practices for quality settings and optimal experience

### 🎯 Key Features

- **Interactive Buttons** - Users click "Weiter →" to progress through steps
- **Direct Links** - Quick access to download pages and Plex web app
- **StreamNet Branding** - Custom emoji thumbnails and footers
- **Auto-Triggered** - Automatically starts after successful Plex invitation
- **Manual Command** - Users can restart with `/plex-walkthrough`
- **Timeout Handling** - 5-minute timeout per step with helpful messages

## How It Works

### Automatic Flow

When a user receives the Plex role:

1. Bot asks for email
2. User is added to Plex
3. Success message is sent
4. **Walkthrough automatically starts** (3-second delay)
5. User clicks through 3 interactive steps
6. Completion message

### Manual Trigger

Users can manually start the walkthrough:

```
/plex-walkthrough
```

## Customization

### Editing Steps

Steps are defined in `cogs/slashCommands/plex/plex_walkthrough.py`:

- `step_1_welcome()` - Introduction
- `step_2_download()` - Client downloads
- `step_3_tips()` - Best practices

### Adding More Steps

1. Add a new method in `PlexWalkthroughSteps` class:

```python
@staticmethod
def step_4_custom(server_name: str) -> tuple[discord.Embed, discord.ui.View]:
    embed = discord.Embed(
        title="Your Title",
        description="Your content",
        color=0xE5A00D,
    )
    # ... customize embed ...

    view = discord.ui.View()
    button = discord.ui.Button(
        label="Next Button",
        custom_id="plex_step_5",
        style=discord.ButtonStyle.primary
    )
    view.add_item(button)

    return embed, view
```

2. Add the step to `send_walkthrough()` method
3. Update step counters in footers

### Disabling Auto-Trigger

Comment out these lines in `plex_commands.py`:

```python
# walkthrough_cog = self.bot.get_cog("PlexWalkthrough")
# if walkthrough_cog:
#     await walkthrough_cog.send_walkthrough(after)
```

## Configuration

The walkthrough uses your existing Plex configuration:

- Server name from `PLEX_SERVER_NAME` in `config/settings.py`
- Custom emojis (update URLs in the step methods)
- Plex web URL (currently `https://app.plex.tv/desktop/`)

## Comparison to Wizarr

| Feature              | Wizarr              | This Implementation   |
| -------------------- | ------------------- | --------------------- |
| Platform             | Web-based           | Discord DMs           |
| Format               | Markdown files      | Python embeds         |
| Navigation           | Page navigation     | Button clicks         |
| Pre/Post Steps       | ✅ Separate phases  | 🟡 Post-invite only   |
| Customization        | Admin panel         | Code editing          |
| Interaction Required | Optional            | Optional (timeout)    |
| Multi-language       | ✅ Via translations | 🟡 German (hardcoded) |

## Future Enhancements

- [ ] Database-backed steps (like Wizarr)
- [ ] Admin command to edit steps
- [ ] Multi-language support
- [ ] Pre-invite steps (before role assignment)
- [ ] Conditional steps based on user preferences
- [ ] Progress tracking in database
- [ ] Skip button for experienced users
- [ ] Integration with Overseerr/Ombi for requests guide

## Credits

Inspired by the excellent [Wizarr](https://github.com/wizarrrr/wizarr) project by [@wizarrrr](https://github.com/wizarrrr).
