"""
Simple password-only authentication for single-tenant access.

WHAT: Provides password-only authentication without user accounts,
      suitable for single-tenant applications where everyone shares
      the same access credentials.

WHY: The application needs simple access control without the complexity
     of user management, registration, or individual accounts. A single
     shared password provides adequate security for internal team use.

HOW: Uses session-based authentication with configurable password,
     creates secure session tokens, and provides FastAPI dependencies
     for route protection.

DEPENDENCIES:
- fastapi: HTTP exception handling and dependency injection
- os: Environment variable access for password configuration
- secrets: Secure token generation
- typing: Type hints for better code documentation
"""

import os
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

# Simple HTTP Basic auth for password-only access
security = HTTPBasic()

# Default password (configurable via environment variable)
DEFAULT_PASSWORD = os.getenv("APP_PASSWORD", "airfare")

# In-memory session storage (for production, use Redis or database)
active_sessions: set[str] = set()


def generate_session_token() -> str:
    """
    Generate a secure session token.
    
    Returns:
        Cryptographically secure random token string
    """
    return secrets.token_urlsafe(32)


def authenticate_password(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    """
    Authenticate user with password-only access.
    
    Validates the provided password against the configured password
    and creates a session token for subsequent requests.
    
    Args:
        credentials: HTTP Basic auth credentials from request
        
    Returns:
        Session token for authenticated user
        
    Raises:
        HTTPException: If password is incorrect (401 Unauthorized)
    """
    if credentials.password != DEFAULT_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Generate and store session token
    session_token = generate_session_token()
    active_sessions.add(session_token)
    
    return session_token


def get_current_session(request: Request) -> str:
    """
    Validate current session from request headers.
    
    Checks for valid session token in Authorization header
    or falls back to password authentication.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Valid session token
        
    Raises:
        HTTPException: If session is invalid (401 Unauthorized)
    """
    # Check for session token in Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        if token in active_sessions:
            return token
    
    # Check for session token in cookies
    session_token = request.cookies.get("session_token")
    if session_token and session_token in active_sessions:
        return session_token
    
    # No valid session found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired session",
        headers={"WWW-Authenticate": "Bearer"},
    )


def logout_session(session_token: str) -> None:
    """
    Remove session token from active sessions.
    
    Args:
        session_token: Session token to invalidate
    """
    active_sessions.discard(session_token)


# FastAPI dependency for protected routes
RequireAuth = Depends(get_current_session) 