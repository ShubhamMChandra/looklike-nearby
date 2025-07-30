#!/usr/bin/env python3
"""
Development startup script for LookLike Nearby Lead Generation Platform.

WHAT: Simple development server startup script that runs the FastAPI application
      with hot reload and proper error handling.

WHY: Provides an easy way for developers to start the application without
     remembering uvicorn command-line options and configurations.

HOW: Uses uvicorn to serve the FastAPI application with development settings,
     handles environment variables, and provides helpful startup messages.

DEPENDENCIES:
- uvicorn: ASGI server for FastAPI
- backend.main: Main FastAPI application
- os: Environment variable access
"""

import os
import sys

try:
    import uvicorn
except ImportError:
    print("Error: uvicorn not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Start the development server."""
    
    # Get configuration from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "true").lower() == "true"
    
    print("🚀 Starting LookLike Nearby Lead Generation Platform...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔍 Health Check: http://{host}:{port}/health")
    print()
    
    if debug:
        print("⚠️  Running in DEBUG mode with hot reload")
    
    print("💡 Default password: 'airfare' (configurable via APP_PASSWORD env var)")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 60)
    
    try:
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            reload=debug,
            log_level="info" if debug else "warning",
            access_log=debug
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 