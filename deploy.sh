#!/bin/bash

# LookLike Nearby Deployment Script
# 
# WHAT: Automated deployment script for the lead generation platform
# 
# WHY: Provides easy deployment to various platforms (Docker, Railway, etc.)
#      with proper environment setup and database initialization.
# 
# HOW: Detects deployment target, sets up environment variables,
#      builds containers, and starts the application with health checks.

set -e  # Exit on any error

echo "🚀 LookLike Nearby Deployment Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if .env file exists
if [ ! -f .env ]; then
    log_warning ".env file not found. Creating from template..."
    cp env.example .env
    log_info "Please edit .env file with your configuration before continuing."
    echo "Required variables:"
    echo "  - DATABASE_URL (PostgreSQL connection string)"
    echo "  - GOOGLE_API_KEY (Google Maps Platform API key)"
    echo "  - APP_PASSWORD (change from default 'airfare')"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Load environment variables
source .env

# Check required environment variables
if [ -z "$GOOGLE_API_KEY" ] || [ "$GOOGLE_API_KEY" = "your-google-maps-api-key" ]; then
    log_error "GOOGLE_API_KEY not set in .env file"
    exit 1
fi

# Deployment options
echo "Select deployment option:"
echo "1) Local development (Docker Compose)"
echo "2) Production build (Docker only)"
echo "3) Railway deployment"
echo "4) Manual setup"
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        log_info "Starting local development environment..."
        
        # Check if Docker is running
        if ! docker info >/dev/null 2>&1; then
            log_error "Docker is not running. Please start Docker and try again."
            exit 1
        fi
        
        # Build and start services
        docker-compose up --build -d
        
        log_success "Services started!"
        log_info "Application: http://localhost:8000"
        log_info "API Docs: http://localhost:8000/docs"
        log_info "Database: localhost:5432"
        
        # Wait for services to be ready
        log_info "Waiting for services to be ready..."
        sleep 10
        
        # Check health
        if curl -f http://localhost:8000/health >/dev/null 2>&1; then
            log_success "Application is healthy!"
        else
            log_warning "Application may still be starting up..."
        fi
        
        echo ""
        log_info "To view logs: docker-compose logs -f"
        log_info "To stop: docker-compose down"
        ;;
        
    2)
        log_info "Building production Docker image..."
        
        # Build Docker image
        docker build -t looklike-nearby:latest .
        
        log_success "Docker image built successfully!"
        log_info "To run: docker run -p 8000:8000 --env-file .env looklike-nearby:latest"
        ;;
        
    3)
        log_info "Preparing for Railway deployment..."
        
        # Check if railway CLI is installed
        if ! command -v railway &> /dev/null; then
            log_warning "Railway CLI not found. Installing..."
            npm install -g @railway/cli
        fi
        
        log_info "Please ensure you have:"
        log_info "1. Created a Railway project"
        log_info "2. Added a PostgreSQL database"
        log_info "3. Set environment variables in Railway dashboard"
        
        echo ""
        log_info "Run these commands to deploy:"
        echo "  railway login"
        echo "  railway link"
        echo "  railway up"
        ;;
        
    4)
        log_info "Manual setup instructions:"
        echo ""
        echo "1. Install Python 3.11+"
        echo "2. Create virtual environment: python -m venv venv"
        echo "3. Activate: source venv/bin/activate"
        echo "4. Install dependencies: pip install -r requirements.txt"
        echo "5. Set up PostgreSQL database"
        echo "6. Configure .env file"
        echo "7. Run: python run.py"
        ;;
        
    *)
        log_error "Invalid choice"
        exit 1
        ;;
esac

log_success "Deployment script completed!"