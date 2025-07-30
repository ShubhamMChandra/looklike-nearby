"""
Salesforce integration utilities for account data retrieval.

WHAT: Provides authentication and data access functions for Salesforce API
      to retrieve account information needed for lead generation.

WHY: Sales teams need to access client account data (addresses, industries,
     business segments) from Salesforce to identify similar prospects
     in the same geographic areas.

HOW: Uses simple-salesforce library for API authentication and querying,
     implements error handling for authentication failures, and provides
     clean interfaces for account data retrieval.

DEPENDENCIES:
- simple_salesforce: Salesforce REST API client
- os: Environment variable access for credentials
- typing: Type hints for better code documentation
"""

from __future__ import annotations

import os
from typing import Any, Dict

try:
    from simple_salesforce import Salesforce, SalesforceAuthenticationFailed  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – only hits in linting env
    # Allow the file to be imported even if simple_salesforce is not installed yet.
    class Salesforce:  # type: ignore
        pass

    class SalesforceAuthenticationFailed(Exception):
        ...


def _auth() -> Salesforce:
    """
    Create authenticated Salesforce client using environment variables.
    
    Retrieves credentials from environment variables and attempts to
    authenticate with Salesforce. Provides clear error messages if
    authentication fails.
    
    Returns:
        Authenticated Salesforce client instance
        
    Raises:
        RuntimeError: If authentication fails due to missing or invalid credentials
        
    Environment Variables:
        SF_USERNAME: Salesforce username/email
        SF_PASSWORD: Salesforce password  
        SF_SECURITY_TOKEN: Salesforce security token
    """
    try:
        return Salesforce(
            username=os.getenv("SF_USERNAME"),
            password=os.getenv("SF_PASSWORD"),
            security_token=os.getenv("SF_SECURITY_TOKEN"),
        )
    except SalesforceAuthenticationFailed as exc:  # pragma: no cover – runtime check
        raise RuntimeError("Failed to authenticate to Salesforce – check your env vars.") from exc


def get_account_details(account_id: str) -> Dict[str, Any]:
    """
    Retrieve account details from Salesforce by Account ID.
    
    Fetches essential account information including billing address,
    business segment, and industry data needed for lead generation
    and similarity matching.
    
    Args:
        account_id: Salesforce Account ID (18-character string)
        
    Returns:
        Dictionary containing account details with fields:
        - Id: Account ID
        - Name: Account name
        - BillingStreet: Street address
        - BillingCity: City
        - BillingCountry: Country
        - Business_Segment__c: Custom business segment field
        - Industry: Standard industry field
        
    Raises:
        ValueError: If account_id is not found in Salesforce
        RuntimeError: If Salesforce authentication or query fails
        
    Example:
        >>> get_account_details("001TQ000001u3M6YAI")
        {
            "Id": "001TQ000001u3M6YAI",
            "Name": "LIFE UNIVERSITY (Parent)",
            "BillingStreet": "1269 BARCLAY CIRCLE",
            "BillingCity": "Atlanta",
            "BillingCountry": "United States",
            "Business_Segment__c": "Dining Facilities",
            "Industry": "Education"
        }
    """
    sf = _auth()
    query = (
        "SELECT Id, Name, BillingStreet, BillingCity, BillingCountry, "
        "Business_Segment__c, Industry "
        f"FROM Account WHERE Id = '{account_id}'"
    )
    res = sf.query(query)
    if not res["records"]:
        raise ValueError(f"Account {account_id} not found.")
    return res["records"][0] 