# Discord Bot Web UI - Frontend

Modern React 18 Single Page Application built with Vite, TailwindCSS, and Lucide Icons.

## Tech Stack

- **React 18** - UI library with concurrent features
- **TypeScript** - Type-safe JavaScript
- **Vite** - Lightning-fast build tool with HMR
- **React Router v6** - Client-side routing
- **TailwindCSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon set
- **Axios** - HTTP client with interceptors

## Getting Started

### Install Dependencies

```bash
npm install
```

### Development Server

```bash
npm run dev
```

Runs at http://localhost:5173 with hot module replacement.

### Production Build

```bash
npm run build
```

Outputs optimized static files to `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── main.tsx              # Entry point
├── App.tsx               # Router configuration
├── index.css             # Global styles + Tailwind
├── components/           # Reusable components
│   ├── Layout.tsx        # Main layout with sidebar
│   └── ProtectedRoute.tsx
├── contexts/             # React contexts
│   └── AuthContext.tsx   # Authentication state
├── lib/                  # Utilities
│   ├── api.ts            # Axios instance with JWT
│   └── utils.ts          # Helper functions
└── pages/                # Route components
    ├── Login.tsx
    ├── Dashboard.tsx
    └── ...
```

## Features

- ✅ JWT-based authentication
- ✅ Protected routes
- ✅ Responsive sidebar navigation
- ✅ Real-time dashboard updates
- ✅ Dark theme by default
- ✅ Mobile-friendly layout
- ✅ Type-safe with TypeScript

## API Integration

The app connects to the FastAPI backend running on port 5000.

API client is configured in `src/lib/api.ts` with:

- Automatic JWT token injection
- 401 error handling (auto-logout)
- Request/response interceptors

## Customization

### Colors

Edit `tailwind.config.js` to customize the color scheme:

```js
colors: {
  discord: {
    blurple: '#5865F2',
    green: '#57F287',
    // ... add more colors
  }
}
```

### Icons

All icons from [Lucide](https://lucide.dev/) are available:

```tsx
import { Heart, Star, Users } from "lucide-react";
```

### Routing

Add new routes in `src/App.tsx`:

```tsx
<Route path="new-page" element={<NewPage />} />
```

## Environment Variables

Create `.env.local` for local overrides:

```env
VITE_API_URL=http://localhost:5000
```

Access in code:

```ts
const apiUrl = import.meta.env.VITE_API_URL;
```

## Development Tips

- **Hot Reload:** Changes reflect instantly
- **TypeScript:** Errors show in terminal and browser
- **DevTools:** React DevTools extension recommended
- **Proxy:** API requests auto-proxy to backend (see `vite.config.ts`)

## Building for Production

1. Build the frontend:

   ```bash
   npm run build
   ```

2. Files are in `dist/` - ready to deploy!

3. Options:
   - Serve with Nginx/Caddy
   - Serve from FastAPI (mount static files)
   - Deploy to Vercel/Netlify/Cloudflare Pages

## Troubleshooting

### `Cannot find module 'react'`

```bash
rm -rf node_modules package-lock.json
npm install
```

### Types not working

```bash
npm install --save-dev @types/node @types/react @types/react-dom
```

### Port 5173 in use

Change in `vite.config.ts`:

```ts
server: {
  port: 3000; // or any other port
}
```

## Scripts

- `npm run dev` - Start dev server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Learn More

- [React Docs](https://react.dev/)
- [Vite Guide](https://vitejs.dev/guide/)
- [TailwindCSS](https://tailwindcss.com/docs)
- [React Router](https://reactrouter.com/)
- [Lucide Icons](https://lucide.dev/guide/)
