# LookLike Nearby - Frontend (Next.js)

This is the Next.js frontend for the LookLike Nearby lead generation platform.

## Architecture

- **Frontend (Vercel)**: Next.js React app
- **Backend (Railway)**: FastAPI Python API with PostgreSQL

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
```

## Deployment

### Vercel (Recommended)

1. Push to GitHub
2. Connect repository to Vercel
3. Set environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy automatically

### Manual

```bash
npm run build
npm start
```

## Features

- 🔐 **Authentication** with Railway backend
- 🔍 **Business search** using Google Places API
- 📊 **Campaign management** for organizing prospects  
- 📱 **Responsive design** with Bootstrap 5
- ⚡ **Fast loading** with Next.js optimization

## API Integration

The frontend communicates with the Railway backend via:

- Authentication: `/api/auth/login`, `/api/auth/logout`
- Search: `/api/search/prospects`
- Campaigns: `/api/campaigns/*`
- Reference Clients: `/api/reference-clients/*`
- Prospects: `/api/prospects/*`
