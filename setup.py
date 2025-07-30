#!/usr/bin/env python3
"""
Setup script for LookLike Nearby Lead Generation Platform.

WHAT: Installation and setup script that validates dependencies,
      creates necessary directories, and prepares the application
      for first run.

WHY: Provides automated setup process to ensure all requirements
     are met and the application is properly configured before
     first use.

HOW: Checks Python version, installs dependencies, validates
     environment configuration, and provides helpful setup
     guidance for new users.

DEPENDENCIES:
- Python 3.9+
- pip package manager
- Virtual environment support
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Colors for output
class Colors:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def log_info(message):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")

def log_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def log_warning(message):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def log_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def check_python_version():
    """Check if Python version is 3.9 or higher."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        log_error(f"Python 3.9+ required. Current version: {version.major}.{version.minor}")
        return False
    log_success(f"Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def check_virtual_environment():
    """Check if running in virtual environment."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        log_success("Running in virtual environment")
        return True
    else:
        log_warning("Not running in virtual environment")
        log_info("Recommended: python -m venv venv && source venv/bin/activate")
        return False

def install_dependencies():
    """Install Python dependencies."""
    log_info("Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        log_success("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment configuration."""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if not env_file.exists():
        if env_example.exists():
            shutil.copy(env_example, env_file)
            log_success("Created .env file from template")
        else:
            # Create basic .env file
            with open(env_file, 'w') as f:
                f.write("""# Database Configuration
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/looklike_nearby

# Authentication
APP_PASSWORD=airfare

# Google APIs
GOOGLE_API_KEY=your-google-maps-api-key

# Application Settings
HOST=0.0.0.0
PORT=8000
DEBUG=true
""")
            log_success("Created basic .env file")
        
        log_warning("Please edit .env file with your configuration:")
        log_info("  - Set GOOGLE_API_KEY (required)")
        log_info("  - Set DATABASE_URL (PostgreSQL connection)")
        log_info("  - Change APP_PASSWORD from default")
        return False
    else:
        log_success(".env file already exists")
        return True

def check_required_tools():
    """Check for required external tools."""
    tools = {
        'git': 'Git version control',
        'docker': 'Docker containerization (optional)',
        'psql': 'PostgreSQL client (optional)'
    }
    
    available = {}
    for tool, description in tools.items():
        if shutil.which(tool):
            log_success(f"{description}: Available")
            available[tool] = True
        else:
            log_warning(f"{description}: Not found")
            available[tool] = False
    
    return available

def create_directories():
    """Create necessary directories."""
    directories = [
        "logs",
        "temp",
        "exports"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    log_success("Created necessary directories")

def main():
    """Main setup function."""
    print(f"{Colors.BOLD}🚀 LookLike Nearby Setup{Colors.END}")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check virtual environment
    in_venv = check_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Setup environment
    env_configured = setup_environment()
    
    # Check tools
    tools = check_required_tools()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    log_success("Setup completed!")
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.END}")
    
    if not env_configured:
        print("1. Edit .env file with your configuration")
    
    if not in_venv:
        print("2. Consider using a virtual environment:")
        print("   python -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    
    print("3. Start the application:")
    print("   python run.py")
    
    print("\n4. Access the application:")
    print("   Web Interface: http://localhost:8000/app")
    print("   API Docs: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    
    if not tools.get('docker', False):
        print("\n5. Optional: Install Docker for easy deployment")
    
    print(f"\n{Colors.BOLD}Documentation:{Colors.END}")
    print("   README.md - Complete setup guide")
    print("   /docs endpoint - API documentation")
    print("   .cursor/claude_rules.md - Development guidelines")

if __name__ == "__main__":
    main()