# Centralized Theming Guide

The entire UI now uses CSS custom properties (variables) for centralized theme management. This means you can change colors in **one place** and the entire UI updates automatically.

## How It Works

All theme colors are defined in `src/index.css` under the `:root` selector:

```css
:root {
  /* Base Colors */
  --navbar-bg: #252525;
  --sidebar-bg: #252525;
  --card-bg: rgba(45, 45, 45, 0.95);
  --text: #ddd;
  --text-hover: #fff;
  --text-muted: #999;

  /* Status Colors */
  --status-online: #38ef7d;
  --status-offline: #f04747;

  /* And many more... */
}
```

## Changing the Theme

### Example 1: Change to a Blue Theme

Edit `src/index.css` and update the `:root` variables:

```css
:root {
  --navbar-bg: #1e3a5f; /* Dark blue */
  --sidebar-bg: #1e3a5f; /* Dark blue */
  --card-bg: rgba(30, 58, 95, 0.95);
  --accent-color: #4a90e2; /* Light blue */
  --status-online: #4a90e2; /* Light blue for online */

  /* Keep other colors or change them too */
}
```

Save the file and the entire UI will update instantly!

### Example 2: Change to a Purple Theme

```css
:root {
  --navbar-bg: #2d1b3d; /* Dark purple */
  --sidebar-bg: #2d1b3d; /* Dark purple */
  --card-bg: rgba(45, 27, 61, 0.95);
  --accent-color: #9b59b6; /* Purple */
  --status-online: #9b59b6; /* Purple for online */
  --stat-channels: #8e44ad; /* Different purple */
  --stat-roles: #c39bd3; /* Light purple */
}
```

### Example 3: High Contrast Theme

```css
:root {
  --navbar-bg: #000000; /* Pure black */
  --sidebar-bg: #000000; /* Pure black */
  --card-bg: rgba(0, 0, 0, 0.95);
  --text: #ffffff; /* Pure white */
  --text-muted: #cccccc; /* Light gray */
  --border-color: rgba(255, 255, 255, 0.3); /* Brighter borders */
}
```

## Available Theme Variables

### Component Colors

- `--navbar-bg` - Top navigation bar background
- `--sidebar-bg` - Left sidebar background
- `--card-bg` - Card/panel background
- `--input-bg` - Input field background
- `--border-color` - Border colors throughout

### Button Colors

- `--button-color` - Default button background
- `--button-color-hover` - Button hover state
- `--button-text` - Button text color
- `--button-text-hover` - Button text hover color

### Text Colors

- `--text` - Default text color
- `--text-hover` - Text hover color
- `--text-muted` - Muted/secondary text

### Status Colors

- `--status-online` - Online/success status
- `--status-offline` - Offline/error status
- `--success-color` - Success messages
- `--warning-color` - Warning messages
- `--danger-color` - Error messages
- `--info-color` - Info messages

### Stat Card Colors

- `--stat-channels` - Channels stat card
- `--stat-roles` - Roles stat card
- `--stat-commands` - Commands stat card
- `--stat-services` - Services stat card

### Discord Brand Colors

- `--discord-blurple` - Discord blurple
- `--discord-green` - Discord green
- `--discord-yellow` - Discord yellow
- `--discord-fuchsia` - Discord fuchsia
- `--discord-red` - Discord red

### Spacing

- `--sidebar-width` - Sidebar width (default: 250px)
- `--navbar-height` - Navbar height (default: 60px)

## Tips

1. **Start Small**: Change one or two colors first to see the effect
2. **Use Color Pickers**: Browser dev tools have built-in color pickers
3. **Test Contrast**: Make sure text is readable against backgrounds
4. **Hot Reload**: Vite will automatically refresh the page when you save
5. **Backup**: Keep the original colors commented out if you want to revert

## Original Dark Theme

Here are the original values for reference:

```css
:root {
  --navbar-bg: #252525;
  --sidebar-bg: #252525;
  --card-bg: rgba(45, 45, 45, 0.95);
  --input-bg: #1a1a1a;
  --border-color: rgba(255, 255, 255, 0.1);

  --button-color: #7a7a7a;
  --button-color-hover: #9b9b9b;

  --text: #ddd;
  --text-hover: #fff;
  --text-muted: #999;

  --status-online: #38ef7d;
  --status-offline: #f04747;
  --success-color: #66bb55;
  --warning-color: #e5a00d;
  --danger-color: #dc3545;

  --stat-channels: #667eea;
  --stat-roles: #f5576c;
  --stat-commands: #faa61a;
  --stat-services: #38ef7d;
}
```
