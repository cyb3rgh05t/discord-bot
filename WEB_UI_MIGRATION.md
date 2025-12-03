# Discord Bot Web UI - Migration to FastAPI + React

## 🚀 Major Update: Modern SPA Architecture

The web UI has been completely migrated from Flask + Jinja2 to **FastAPI + React 18 + Vite + TailwindCSS**.

### Why This Migration?

**Problem Solved:** The old Flask-based UI reloaded the entire page on every navigation, causing poor UX.

**Solution:** True Single Page Application (SPA) with client-side routing - **zero page reloads** when switching tabs!

---

## Architecture Overview

### Backend: FastAPI

- **Location:** `api/` directory
- **Features:**
  - Async API endpoints
  - JWT authentication
  - WebSocket support for real-time updates
  - Automatic OpenAPI docs at `/api/docs`
  - Better performance with async/await

### Frontend: React 18 + Vite

- **Location:** `frontend/` directory
- **Features:**
  - Lightning-fast development with Vite HMR
  - TailwindCSS for modern styling
  - Lucide Icons for beautiful UI
  - Client-side routing (no page reloads!)
  - Real-time bot status updates

---

## Setup Instructions

### 1. Backend Setup (FastAPI)

The FastAPI backend runs alongside your Discord bot in the same process.

**Dependencies are already in `requirements.txt`:**

```bash
pip install -r requirements.txt
```

**Start the bot (API starts automatically if `WEB_ENABLED=True`):**

```bash
python bot.py
```

The API will be available at: `http://localhost:5000/api`

### 2. Frontend Setup (React)

**Navigate to frontend directory:**

```bash
cd frontend
```

**Install Node.js dependencies:**

```bash
npm install
```

**Development mode (with hot reload):**

```bash
npm run dev
```

The frontend dev server runs at: `http://localhost:5173`

**Production build:**

```bash
npm run build
```

This creates optimized files in `frontend/dist/` ready for deployment.

---

## Configuration

### Environment Variables

The same settings in `config/settings.py` apply:

```python
WEB_ENABLED = True          # Enable/disable web UI
WEB_HOST = "0.0.0.0"        # API host
WEB_PORT = 5000             # API port
WEB_AUTH_ENABLED = True     # Require login
WEB_USERNAME = "admin"      # Login username
WEB_PASSWORD = "password"   # Login password (change this!)
WEB_SECRET_KEY = "..."      # JWT secret (generate a secure one!)
WEB_VERBOSE_LOGGING = False # Debug mode
```

**Important:** Change `WEB_PASSWORD` and generate a strong `WEB_SECRET_KEY`!

### CORS Configuration

The FastAPI backend allows the Vite dev server (`localhost:5173`) by default.

For production, update the `allow_origins` in `api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Your production URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## API Endpoints

### Authentication

- `POST /api/auth/login` - Login with username/password (returns JWT)
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - Logout (client discards token)

### Dashboard

- `GET /api/dashboard` - Get bot status + system stats
- `GET /api/dashboard/bot-status` - Bot status only

### Other Endpoints

- `/api/settings` - Bot settings management
- `/api/tickets` - Ticket system
- `/api/members` - Server members
- `/api/invites` - Invite tracking
- `/api/commands` - Command reference
- `/api/databases` - Database management
- `/api/services` - Service monitoring
- `/api/guild-stats` - Guild statistics

### WebSocket

- `WS /ws/updates` - Real-time bot status updates

**Explore all endpoints:** `http://localhost:5000/api/docs` (when running)

---

## Development Workflow

### Running Both Backend + Frontend

**Terminal 1 (Backend/Bot):**

```bash
python bot.py
```

**Terminal 2 (Frontend Dev Server):**

```bash
cd frontend
npm run dev
```

Now you can:

- Access frontend at `http://localhost:5173`
- Make frontend changes → instant hot reload
- Make backend changes → restart bot
- API automatically proxies through Vite dev server

---

## Production Deployment

### Option 1: Separate Frontend/Backend

1. **Build frontend:**

   ```bash
   cd frontend
   npm run build
   ```

2. **Serve static files** from `frontend/dist/` with Nginx/Caddy

3. **Run API** with your bot:

   ```bash
   python bot.py
   ```

### Option 2: Serve Frontend from FastAPI

Add static file serving to `api/main.py`:

```python
from fastapi.staticfiles import StaticFiles

# After all routers
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

Then just run `python bot.py` and everything is served from port 5000.

---

## Features

### ✅ Completed

- FastAPI backend with all major endpoints
- JWT authentication system
- React 18 SPA with routing
- TailwindCSS dark theme
- Responsive mobile layout
- Dashboard with real-time stats
- WebSocket support for live updates
- All page stubs (Settings, Tickets, etc.)

### 🚧 To Implement

Each page currently shows "Coming soon" - you'll need to:

1. Implement actual data fetching in backend routers
2. Build out React components for each page
3. Connect to existing bot databases/functions
4. Add more real-time features via WebSocket

The foundation is solid - just flesh out the endpoints!

---

## File Structure

```
discord-bot/
├── api/                          # FastAPI backend
│   ├── main.py                   # Main FastAPI app
│   ├── __init__.py
│   └── routers/                  # API endpoints
│       ├── auth.py               # Authentication
│       ├── dashboard.py          # Dashboard data
│       ├── settings.py
│       ├── tickets.py
│       ├── members.py
│       ├── invites.py
│       ├── commands.py
│       ├── databases.py
│       ├── services.py
│       ├── guild_stats.py
│       └── websocket.py          # Real-time updates
├── frontend/                     # React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── index.html
│   └── src/
│       ├── main.tsx              # Entry point
│       ├── App.tsx               # Router setup
│       ├── index.css             # Global styles
│       ├── components/
│       │   ├── Layout.tsx        # Main layout with sidebar
│       │   └── ProtectedRoute.tsx
│       ├── contexts/
│       │   └── AuthContext.tsx   # Auth state management
│       ├── lib/
│       │   ├── api.ts            # Axios instance
│       │   └── utils.ts          # Helper functions
│       └── pages/                # All pages
│           ├── Login.tsx
│           ├── Dashboard.tsx
│           ├── Settings.tsx
│           ├── Tickets.tsx
│           ├── Members.tsx
│           ├── Invites.tsx
│           ├── Commands.tsx
│           ├── Databases.tsx
│           ├── Services.tsx
│           └── GuildStats.tsx
├── bot.py                        # Main bot (updated to use FastAPI)
├── requirements.txt              # Python deps (updated)
└── web/                          # OLD Flask UI (can be deleted)
```

---

## Migration Notes

### What Changed

- ❌ **Removed:** Flask, Flask-Login, Jinja2 templates, old `web/` directory
- ✅ **Added:** FastAPI, Uvicorn, PyJWT, React, Vite, TailwindCSS
- 🔄 **Updated:** `bot.py` now imports from `api.main` and database init moved to `cogs/helpers/init_databases.py`

### Database & Bot Code

**No changes needed!** The new API uses the same:

- Bot instance reference
- Database files
- Helper functions
- Config settings

---

## Troubleshooting

### Backend won't start

- Check `requirements.txt` installed: `pip install -r requirements.txt`
- Verify `WEB_ENABLED=True` in `config/settings.py`
- Check port 5000 not in use

### Frontend won't start

- Install dependencies: `cd frontend && npm install`
- Check Node.js version: `node -v` (should be 18+)
- Clear cache: `rm -rf node_modules && npm install`

### API 401 Unauthorized

- Login at `/login` to get JWT token
- Token stored in `localStorage`
- Check `WEB_USERNAME` and `WEB_PASSWORD` in settings

### WebSocket not connecting

- Backend must be running
- Check browser console for errors
- Verify proxy config in `vite.config.ts`

---

## Next Steps

1. **Test the stack:**

   ```bash
   # Terminal 1
   python bot.py

   # Terminal 2
   cd frontend && npm run dev
   ```

2. **Login at** `http://localhost:5173/login`

   - Default: `admin` / `password` (change this!)

3. **Start implementing features:**

   - Fill out API endpoints with real data
   - Build React components
   - Add database queries
   - Enhance WebSocket events

4. **Production:**
   - Build frontend: `npm run build`
   - Deploy static files
   - Secure your API
   - Use HTTPS

---

## Technologies Used

- **Backend:** Python 3.10+, FastAPI, Uvicorn, PyJWT
- **Frontend:** React 18, TypeScript, Vite
- **Styling:** TailwindCSS
- **Icons:** Lucide React
- **State:** React Context API
- **HTTP:** Axios
- **WebSocket:** Native WebSocket API

---

## Support

Questions? Issues?

- Check API docs: `http://localhost:5000/api/docs`
- Review FastAPI logs in console
- Check browser DevTools console
- Review this README!

**Happy coding! 🎉**
