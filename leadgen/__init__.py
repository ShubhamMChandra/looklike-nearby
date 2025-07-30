"""
Lead generation helper package for B2B referral lead generation.

WHAT: This package provides reusable business logic for finding similar businesses
      near existing clients to enable warm referral opportunities.

WHY: Sales teams need to identify high-potential prospects by leveraging existing
     client relationships and geographic proximity to maximize conversion rates.

HOW: Combines Salesforce account data with Google Places API to find nearby
     businesses, applies similarity scoring algorithms, and returns prioritized
     lead recommendations.

DEPENDENCIES:
- simple_salesforce: Salesforce API integration
- requests: HTTP client for Google APIs
- pandas: Data manipulation and analysis
- fuzzywuzzy: String matching for business name similarity
- geopy: Geocoding and distance calculations
"""

__all__ = [
    "google_places",
    "matching", 
    "salesforce_utils",
]

__version__ = "0.1.0"

# Lazy-import sub-modules so that tools like linters see the symbols
# without triggering heavy third-party imports at package import time.
from importlib import import_module as _imp
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import types as _types
    google_places: _types.ModuleType
    matching: _types.ModuleType
    salesforce_utils: _types.ModuleType

for _name in __all__:
    globals()[_name] = _imp(f"leadgen.{_name}")

del _imp, _name 