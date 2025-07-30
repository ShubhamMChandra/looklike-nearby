"""
Authentication API routes for password-only access.

WHAT: Provides FastAPI routes for login, logout, and session management
      with simple password-only authentication system.

WHY: The application needs secure but simple access control without
     complex user management, suitable for single-tenant team usage.

HOW: Uses FastAPI routers with password validation, session token generation,
     and proper HTTP status codes for authentication flows.

DEPENDENCIES:
- fastapi: Router and HTTP handling
- pydantic: Request/response validation
- backend.auth.password_auth: Authentication logic
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.auth.password_auth import authenticate_password, get_current_session, logout_session

router = APIRouter()


class LoginRequest(BaseModel):
    """Request model for login endpoint."""
    password: str


class LoginResponse(BaseModel):
    """Response model for successful login."""
    session_token: str
    message: str


class LogoutResponse(BaseModel):
    """Response model for logout endpoint."""
    message: str


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest) -> LoginResponse:
    """
    Authenticate user with password and return session token.
    
    Args:
        request: Login request with password
        
    Returns:
        Session token and success message
        
    Raises:
        HTTPException: If password is incorrect (401)
    """
    try:
        # Create mock credentials object for the dependency
        from fastapi.security import HTTPBasicCredentials
        credentials = HTTPBasicCredentials(username="", password=request.password)
        
        # Authenticate and get session token
        session_token = authenticate_password(credentials)
        
        return LoginResponse(
            session_token=session_token,
            message="Authentication successful"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


@router.post("/logout", response_model=LogoutResponse)
async def logout(session_token: str = Depends(get_current_session)) -> LogoutResponse:
    """
    Logout user and invalidate session token.
    
    Args:
        session_token: Current session token from dependency
        
    Returns:
        Success message
    """
    logout_session(session_token)
    
    return LogoutResponse(message="Logout successful")


@router.get("/validate")
async def validate_session(session_token: str = Depends(get_current_session)) -> dict:
    """
    Validate current session token.
    
    Args:
        session_token: Current session token from dependency
        
    Returns:
        Session validation response
    """
    return {"valid": True, "session_token": session_token} 