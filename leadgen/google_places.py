"""
Google Maps / Places API integration for business discovery.

WHAT: Provides wrappers around Google Maps Platform APIs (Geocoding, Places Nearby Search,
      and Text Search) to find businesses within specified geographic areas.

WHY: Sales teams need to discover potential prospects in specific locations around
     existing clients. Google Places API provides comprehensive business data including
     contact information, ratings, and business categories.

HOW: Implements rate-limited API calls with proper pagination handling, combines
     multiple search strategies (keyword-based and text-based), and deduplicates
     results to provide comprehensive business discovery.

DEPENDENCIES:
- requests: HTTP client for API calls
- time: Rate limiting and pagination delays
- typing: Type hints for better code documentation
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

import requests

# API endpoint constants for Google Maps Platform
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
TEXTSEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"


class GooglePlacesError(RuntimeError):
    """Raised when a Google API call returns a non-OK status."""


# ----------------------------------------------------------------------------
# Low-level helpers
# ----------------------------------------------------------------------------

def get_coordinates(api_key: str, address: str) -> Tuple[float, float]:
    """
    Convert address to geographic coordinates using Google Geocoding API.
    
    Args:
        api_key: Google Maps Platform API key
        address: Human-readable address string
        
    Returns:
        Tuple of (latitude, longitude) coordinates
        
    Raises:
        GooglePlacesError: If geocoding fails or returns no results
    """
    resp = requests.get(GEOCODE_URL, params={"address": address, "key": api_key}, timeout=10)
    data: Dict[str, Any] = resp.json()
    if data.get("status") == "OK":
        loc = data["results"][0]["geometry"]["location"]
        return loc["lat"], loc["lng"]
    raise GooglePlacesError(f"Geocode failed: {data.get('status')} – {data.get('error_message')}")


def _paged_request(url: str, params: Dict[str, Any], page_limit: int = 3) -> List[Dict[str, Any]]:
    """
    Handle Google API pagination with next_page_token semantics.
    
    Google Places API uses a next_page_token that requires a short delay
    before it becomes active. This function handles the pagination logic
    and rate limiting automatically.
    
    Args:
        url: API endpoint URL
        params: Query parameters (excluding pagetoken)
        page_limit: Maximum number of pages to fetch
        
    Returns:
        List of all results across all pages
    """
    all_results: List[Dict[str, Any]] = []
    page = 0
    next_token: str | None = None
    while page < page_limit:
        if next_token:
            params["pagetoken"] = next_token
            # Google requires a short delay before using next_page_token
            time.sleep(2)
        resp = requests.get(url, params=params, timeout=10)
        data: Dict[str, Any] = resp.json()
        if data.get("status") != "OK":
            break
        all_results.extend(data["results"])
        next_token = data.get("next_page_token")
        if not next_token:
            break
        page += 1
    return all_results


# ----------------------------------------------------------------------------
# Public search helpers
# ----------------------------------------------------------------------------

def search_nearby(api_key: str, lat: float, lng: float, keyword: str, radius_meters: int = 1609) -> List[Dict[str, Any]]:
    """
    Search for businesses near coordinates using Google Places Nearby Search.
    
    This endpoint is optimized for finding businesses by keyword within a
    specific radius. It's more precise than text search but may miss some
    relevant results.
    
    Args:
        api_key: Google Maps Platform API key
        lat: Latitude coordinate
        lng: Longitude coordinate  
        keyword: Search term (e.g., "restaurant", "grocery store")
        radius_meters: Search radius in meters (default: ~1 mile)
        
    Returns:
        List of business results with place details
    """
    params = {
        "location": f"{lat},{lng}",
        "radius": radius_meters,
        "keyword": keyword,
        "key": api_key,
    }
    return _paged_request(NEARBY_URL, params)


def search_text(api_key: str, lat: float, lng: float, query: str, radius_meters: int = 1609) -> List[Dict[str, Any]]:
    """
    Search for businesses using Google Places Text Search API.
    
    Text search is more flexible than nearby search and can find businesses
    that don't exactly match the keyword. It's useful for broader discovery
    but may return less relevant results.
    
    Args:
        api_key: Google Maps Platform API key
        lat: Latitude coordinate
        lng: Longitude coordinate
        query: Natural language search query
        radius_meters: Search radius in meters (default: ~1 mile)
        
    Returns:
        List of business results with place details
    """
    params = {
        "query": f"{query} near {lat},{lng}",
        "location": f"{lat},{lng}",
        "radius": radius_meters,
        "key": api_key,
    }
    return _paged_request(TEXTSEARCH_URL, params, page_limit=1)


def find_similar_businesses(
    api_key: str,
    address: str,
    search_terms: List[str],
    radius_meters: int = 1609,
) -> List[Dict[str, Any]]:
    """
    High-level function to find similar businesses near an address.
    
    This function combines geocoding with multiple search strategies to
    provide comprehensive business discovery. It deduplicates results
    based on place_id to avoid returning the same business multiple times.
    
    Args:
        api_key: Google Maps Platform API key
        address: Human-readable address to search around
        search_terms: List of keywords to search for (e.g., ["restaurant", "cafe"])
        radius_meters: Search radius in meters (default: ~1 mile)
        
    Returns:
        List of unique business results with full place details
        
    Raises:
        GooglePlacesError: If geocoding fails or API calls fail
    """
    # Convert address to coordinates for radius-based search
    lat, lng = get_coordinates(api_key, address)

    # Track seen place_ids to avoid duplicates
    seen: set[str] = set()
    combined: List[Dict[str, Any]] = []
    
    # Search using each term with both nearby and text search
    for term in search_terms:
        combined.extend(search_nearby(api_key, lat, lng, term, radius_meters))
        combined.extend(search_text(api_key, lat, lng, term, radius_meters))

    # Deduplicate results based on place_id
    unique_results: List[Dict[str, Any]] = []
    for res in combined:
        pid = res.get("place_id")
        if pid and pid not in seen:
            seen.add(pid)
            unique_results.append(res)
    return unique_results 