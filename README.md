# LookLike Nearby - B2B Referral Lead Generation Platform

> **Find similar businesses nearby your best clients to unlock warm referral opportunities**

## 🎯 Product Vision

LookLike Nearby helps sales teams identify high-potential prospects by finding businesses similar to their existing successful clients within the same geographic area. By leveraging Google Maps API and intelligent matching algorithms, sales teams can discover warm referral opportunities through their existing client relationships.

### Why LookLike Nearby?

- **Warm Introductions**: Leverage existing client relationships for referrals to similar nearby businesses
- **Geographic Clustering**: Focus on businesses within reasonable travel distance for efficient territory management
- **Industry Intelligence**: Identify lookalike companies based on industry, size, and business characteristics
- **Sales Efficiency**: Prioritize outreach to businesses most likely to need your products/services

## 🚀 User Journey

### Primary Use Case: Regional Sales Manager

1. **Simple Access Control**
   - Single password access (default: "airfare")
   - No user accounts - everyone sees the same shared data
   - Session-based authentication

2. **Reference Client Management**
   - Add successful existing clients as reference points
   - Store business name, address, type, and notes
   - Use clients as starting points for geographic searches

3. **Search & Discovery**
   - Select reference client or enter new business details
   - Set search radius (5, 10, 25, 50 miles)
   - Find similar businesses using Google Places API
   - View results in list and map format

4. **Campaign Organization**
   - Create named campaigns (e.g., "Q1 2025 Chicago Expansion")
   - Add prospects to campaigns with status tracking
   - Track outreach progress (New, Contacted, Qualified, etc.)

5. **Export & Reporting**
   - CSV export with contact information
   - PDF reports with maps and prospect details
   - Contact lists for outreach campaigns

## 🏗️ Technical Architecture

### System Components

```
looklike-nearby/
├── backend/                  # FastAPI Backend
│   ├── main.py              # FastAPI application entry
│   ├── database/            # Database configuration
│   ├── models/              # SQLAlchemy models
│   ├── api/                 # API route handlers
│   ├── auth/                # Authentication system
│   └── services/            # Business logic services
│
├── frontend/                # Frontend Assets
│   ├── templates/           # HTML templates
│   └── static/              # CSS, JS, images
│       ├── css/
│       └── js/
│
├── leadgen/                 # Core Business Logic (Reusable)
│   ├── google_places.py    # Google Maps/Places integration
│   ├── matching.py         # Similarity algorithms
│   └── salesforce_utils.py # Salesforce integration
│
├── run.py                   # Development startup script
├── requirements.txt         # Python dependencies
└── env.example             # Environment configuration template
```

### Technology Stack

- **Backend**: FastAPI with async/await, SQLAlchemy 2.0, PostgreSQL
- **Frontend**: Bootstrap 5, Vanilla JavaScript, Font Awesome icons
- **APIs**: Google Maps Platform (Places, Geocoding), Salesforce REST API
- **Database**: PostgreSQL with async support
- **Authentication**: Simple password-only access with session tokens

## 📋 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 13+ (or use Railway/Supabase)
- Google Cloud Platform account (for Maps API)
- Git

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/your-org/looklike-nearby.git
cd looklike-nearby

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```bash
# Database (use Railway, Supabase, or local PostgreSQL)
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/looklike_nearby

# Google Maps API (get from Google Cloud Console)
GOOGLE_API_KEY=your-google-maps-api-key

# Authentication (change from default)
APP_PASSWORD=your-secure-password

# Optional: Salesforce integration
SF_USERNAME=your-salesforce-username
SF_PASSWORD=your-salesforce-password
SF_SECURITY_TOKEN=your-salesforce-token
```

### 3. Database Setup

**Option A: Railway (Recommended)**
1. Create account at [railway.app](https://railway.app)
2. Create new PostgreSQL database
3. Copy connection string to `DATABASE_URL` in `.env`

**Option B: Local PostgreSQL**
```bash
# Install PostgreSQL and create database
createdb looklike_nearby

# Update DATABASE_URL in .env
DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/looklike_nearby
```

### 4. Google Maps API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project or select existing
3. Enable APIs:
   - Places API
   - Geocoding API
   - Maps JavaScript API (for future map features)
4. Create API key and add to `.env`
5. Restrict API key to your domains for security

### 5. Run the Application

```bash
# Start development server
python run.py

# Or use uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

**Default Login**: Password is `airfare` (configurable via `APP_PASSWORD`)

## 🛠️ Development

### Project Structure

The application follows FastAPI best practices with clear separation of concerns:

- **Models** (`backend/models/`): Database schema definitions
- **API Routes** (`backend/api/`): HTTP endpoint handlers
- **Services** (`backend/services/`): Business logic layer
- **Core Logic** (`leadgen/`): Reusable business logic (Google Places, matching)

### Adding New Features

1. **Database Changes**: Add/modify models in `backend/models/`
2. **API Endpoints**: Create route handlers in `backend/api/`
3. **Frontend**: Update templates and JavaScript in `frontend/`
4. **Business Logic**: Add reusable functions to `leadgen/`

### Code Quality

All modules follow documentation standards with:
- **WHAT**: Purpose and functionality
- **WHY**: Business logic and reasoning  
- **HOW**: Implementation approach
- **DEPENDENCIES**: External dependencies

## 🚀 Deployment

### Railway (Recommended)

1. Connect GitHub repository to Railway
2. Add environment variables in Railway dashboard
3. Deploy automatically on git push

### Docker

```bash
# Build image
docker build -t looklike-nearby .

# Run container
docker run -p 8000:8000 --env-file .env looklike-nearby
```

### Traditional Hosting

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="your-database-url"
export GOOGLE_API_KEY="your-api-key"
export APP_PASSWORD="your-password"

# Run with gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 📊 Features Roadmap

### ✅ Phase 1: MVP (Current)
- [x] Password-only authentication
- [x] Reference client management
- [x] Google Places API integration
- [x] Basic search functionality
- [x] Campaign organization structure
- [x] Responsive web interface

### 🔄 Phase 2: Enhanced Search (Next)
- [ ] Advanced similarity scoring
- [ ] Map visualization with markers
- [ ] Batch territory analysis
- [ ] CSV/PDF export functionality
- [ ] Email and phone enrichment

### 🔮 Phase 3: Intelligence Layer
- [ ] Machine learning similarity scoring
- [ ] Predictive lead scoring
- [ ] Competitive intelligence
- [ ] Social media presence analysis
- [ ] Purchase pattern analysis

### 🎯 Phase 4: Sales Enablement
- [ ] Full CRM integration
- [ ] Referral tracking system
- [ ] Email templates
- [ ] Mobile app
- [ ] Territory optimization

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/description`
3. **Follow code standards**: Use the documentation format in `.cursor/claude_rules.md`
4. **Test thoroughly**: Ensure all functionality works
5. **Submit pull request**: Include description of changes

## 📞 Support

- **Documentation**: Check the `/docs` endpoint when running
- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub discussions for questions

## 📄 License

Copyright (c) 2024 LookLike Nearby. All rights reserved.

---

**Built with ❤️ for B2B sales teams everywhere**
