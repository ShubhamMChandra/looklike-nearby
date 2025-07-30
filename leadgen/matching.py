"""
Utility functions for fuzzy matching and geospatial calculations.

WHAT: Provides helper functions for string matching, address normalization,
      domain extraction, and geographic distance calculations used in
      business similarity scoring.

WHY: Lead generation requires comparing business names, addresses, and
     calculating distances between locations. These utilities enable
     accurate matching and filtering of potential prospects.

HOW: Uses fuzzy string matching algorithms, regex-based address normalization,
     URL parsing for domain extraction, and the Haversine formula for
     accurate geographic distance calculations.

DEPENDENCIES:
- math: Trigonometric functions for distance calculations
- re: Regular expressions for string processing
- urllib.parse: URL parsing for domain extraction
- typing: Type hints for better code documentation
"""

from __future__ import annotations

import re
from math import asin, cos, radians, sin, sqrt
from typing import Optional
from urllib.parse import urlparse

__all__ = [
    "haversine",
    "extract_domain",
    "normalize_address",
]


# ----------------------------------------------------------------------------
# Geo helpers
# ----------------------------------------------------------------------------

def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
    Calculate great-circle distance between two geographic points.
    
    Uses the Haversine formula to compute the shortest distance over
    the Earth's surface between two points given their latitude and
    longitude coordinates.
    
    Args:
        lon1: Longitude of first point in decimal degrees
        lat1: Latitude of first point in decimal degrees
        lon2: Longitude of second point in decimal degrees
        lat2: Latitude of second point in decimal degrees
        
    Returns:
        Distance in meters between the two points
        
    Example:
        >>> haversine(-74.006, 40.7128, -118.2437, 34.0522)
        3935000.0  # Distance from NYC to LA in meters
    """
    # Convert decimal degrees to radians for trigonometric calculations
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Calculate differences in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Haversine formula implementation
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    
    # Earth's radius in meters (mean radius)
    r = 6_371_000
    return c * r


# ----------------------------------------------------------------------------
# String helpers
# ----------------------------------------------------------------------------

def extract_domain(url: str | None) -> Optional[str]:
    """
    Extract domain name from a URL string.
    
    Handles URLs with or without protocol schemes and removes
    common prefixes like 'www.' for consistent domain matching.
    
    Args:
        url: URL string to extract domain from (can be None)
        
    Returns:
        Domain name in lowercase (e.g., "example.com") or None if invalid
        
    Examples:
        >>> extract_domain("https://www.example.com/path")
        "example.com"
        >>> extract_domain("example.com")
        "example.com"
        >>> extract_domain(None)
        None
    """
    if not url:
        return None
    
    # Add protocol if missing to ensure proper URL parsing
    if not url.startswith(("http://", "https://")):
        url = "http://" + url
    
    # Parse URL and extract domain
    domain = urlparse(url).netloc.lower()
    
    # Remove www. prefix if present for consistent matching
    return domain[4:] if domain.startswith("www.") else domain


# Compiled regex for whitespace normalization
_space_re = re.compile(r"\s+")


def normalize_address(address: str | None) -> str:
    """
    Normalize address string for consistent fuzzy matching.
    
    Converts address to lowercase, removes extra whitespace, and
    standardizes formatting to improve similarity matching accuracy.
    
    Args:
        address: Address string to normalize (can be None)
        
    Returns:
        Normalized address string in lowercase with single spaces
        
    Examples:
        >>> normalize_address("123 Main St,  New York,  NY")
        "123 main st, new york, ny"
        >>> normalize_address(None)
        ""
    """
    if not address:
        return ""
    
    # Convert to lowercase and collapse multiple whitespace to single space
    return _space_re.sub(" ", address.lower().strip()) 