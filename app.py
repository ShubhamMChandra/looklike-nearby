"""
Flask API server for B2B lead generation platform.

WHAT: Provides REST API endpoints for finding similar businesses near existing
      clients to enable warm referral opportunities for sales teams.

WHY: Sales teams need a simple, accessible interface to discover potential
     prospects without requiring technical knowledge of APIs or data sources.
     This Flask app provides a clean HTTP interface to the leadgen package.

HOW: Uses Flask for HTTP routing, integrates with leadgen package for business
     logic, handles environment variable configuration, and provides JSON
     responses with proper error handling and status codes.

DEPENDENCIES:
- Flask: Web framework for HTTP routing and JSON responses
- leadgen: Core business logic package
- os: Environment variable access for configuration
- typing: Type hints for better code documentation
"""

from __future__ import annotations

import os
from typing import List

from flask import Flask, jsonify, request

from leadgen import google_places as gp
from leadgen import salesforce_utils as sf_utils

# Conversion factor for miles to meters (1 mile = 1609.34 meters)
MILES_TO_METERS = 1609.34

app = Flask(__name__)


@app.get("/health")
def health() -> dict:  # type: ignore[override]
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        Simple JSON response indicating service is running
    """
    return {"status": "ok"}


def _build_search_terms(account: dict, custom_industry: str) -> List[str]:
    """
    Build search terms for Google Places API based on account data.
    
    Uses custom industry keywords if provided, otherwise falls back to
    account's business segment and industry fields from Salesforce.
    
    Args:
        account: Salesforce account dictionary with business fields
        custom_industry: Comma-separated custom industry keywords
        
    Returns:
        List of search terms for Google Places API
    """
    if custom_industry:
        # Split custom industry string and clean up whitespace
        return [t.strip() for t in custom_industry.split(",") if t.strip()]
    
    # Use account's business segment and industry fields
    return list(
        filter(
            None,
            [
                account.get("Business_Segment__c"),
                account.get("Industry"),
            ],
        )
    )


@app.post("/leads")
def leads():  # type: ignore[override]
    """
    Find similar businesses near a Salesforce account.
    
    Accepts JSON payload with account_id and optional parameters,
    retrieves account details from Salesforce, and searches for
    similar businesses using Google Places API.
    
    Request Body:
        {
            "account_id": "001xxxxxxxxxxxx",  # Required: Salesforce Account ID
            "radius_miles": 10,               # Optional: Search radius (default: 10)
            "custom_address": "123 Main St",  # Optional: Override account address
            "custom_industry": "restaurant"   # Optional: Override industry keywords
        }
        
    Returns:
        JSON response with count and list of similar businesses
        
    Status Codes:
        200: Success with business results
        400: Missing required account_id field
        500: Salesforce or Google API errors
    """
    # Parse and validate request data
    data = request.get_json(force=True, silent=True) or {}
    account_id = data.get("account_id")
    if not account_id:
        return jsonify({"error": "Missing 'account_id' field"}), 400

    # Extract optional parameters with defaults
    custom_address = data.get("custom_address", "")
    custom_industry = data.get("custom_industry", "")
    radius_miles = float(data.get("radius_miles", 10))
    radius_meters = int(radius_miles * MILES_TO_METERS)

    # Validate Google API key is configured
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        return jsonify({"error": "GOOGLE_API_KEY environment variable not set"}), 500

    # ------------------------------------------------------------------
    # Fetch account data from Salesforce
    # ------------------------------------------------------------------
    try:
        account = sf_utils.get_account_details(account_id)
    except Exception as exc:
        return jsonify({"error": f"Failed to fetch Salesforce account: {exc}"}), 500

    # Build address string for geocoding
    address = (
        custom_address
        if custom_address
        else f"{account.get('BillingStreet')}, {account.get('BillingCity')}, {account.get('BillingCountry')}"
    )

    # ------------------------------------------------------------------
    # Search for similar businesses using Google Places API
    # ------------------------------------------------------------------
    try:
        search_terms = _build_search_terms(account, custom_industry)
        results = gp.find_similar_businesses(google_api_key, address, search_terms, radius_meters)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({"count": len(results), "results": results})


if __name__ == "__main__":
    # Get port from environment or default to 5000
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True) 