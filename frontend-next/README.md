# LookLike Nearby - Next.js Frontend

This is the Next.js frontend for the LookLike Nearby B2B lead generation platform.

## Deployment Instructions

### Deploy Backend to Railway

1. Push your code to GitHub
2. Create a new project on [Railway](https://railway.app)
3. Connect your GitHub repository
4. Railway will automatically detect the Python backend
5. Add PostgreSQL database from Railway's marketplace
6. Set environment variables:
   - `GOOGLE_API_KEY` - Your Google Maps API key
   - `APP_PASSWORD` - Your chosen password
   - `SECRET_KEY` - A random secret key
   - `FRONTEND_URL` - Your Vercel frontend URL (after deployment)

### Deploy Frontend to Vercel

1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to the frontend-next directory: `cd frontend-next`
3. Run: `vercel`
4. Follow the prompts to link to your Vercel account
5. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` - Your Railway backend URL
   - `NEXT_PUBLIC_GOOGLE_MAPS_KEY` - Your Google Maps API key

### Local Development

1. Install dependencies: `npm install`
2. Copy environment variables: `cp .env.local.example .env.local`
3. Update `.env.local` with your backend URL
4. Run development server: `npm run dev`
5. Open [http://localhost:3000](http://localhost:3000)

## Features

- Password-based authentication
- Reference client management
- Business search with radius filtering
- Campaign organization
- Responsive design with Tailwind CSS