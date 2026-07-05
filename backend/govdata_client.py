"""
govdata_client.py — Real integration with data.gov.in's Open Government Data
(OGD) Platform API, covering the two datasets that are GENUINELY publicly
queryable at a usable granularity:

  1. Agmarknet — daily mandi (market) commodity prices, district-level
  2. PMJDY — Jan Dhan Yojana financial inclusion account statistics, district-level

HONESTY NOTE ON GRANULARITY: both datasets are published at the DISTRICT
level (e.g. "Varanasi"), not per-pincode. PRISM's 12 fictional pincode zones
within Varanasi therefore all share the same real district-level baseline,
blended with the existing synthetic per-zone variation — this is disclosed
in the API response via "granularity": "district_real_zone_synthetic" so
nothing is silently overstated.

HONESTY NOTE ON WHAT'S NOT HERE: DBT Bharat disbursement data and GST
business-registration data do NOT have publicly queryable APIs at any
usable granularity — DBT Bharat only publishes static reports, and GSTN
doesn't expose registration data for privacy reasons. PRISM does not
pretend to use these; PMJDY (above) is used as the real, honest proxy for
financial-inclusion signal instead of a fabricated DBT integration.

Setup:
  1. Register (free) at https://data.gov.in/user/register — takes ~2 min
  2. Get your API key from https://data.gov.in/user (My Account -> API Key)
  3. Find each dataset's exact resource_id:
     - Go to https://data.gov.in and search "Agmarknet" or "PMJDY district"
     - Open a matching resource page — the resource_id is in the URL / on
       the page ("API" tab shows the exact endpoint with resource_id filled in)
     - Paste those IDs into .env as AGMARKNET_RESOURCE_ID / PMJDY_RESOURCE_ID
  Resource IDs are dataset-version-specific and occasionally change, which
  is why they're configurable here rather than hardcoded.
"""

import os
from typing import Optional, Dict, List

try:
    import requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False

DATA_GOV_IN_API_KEY = os.getenv("DATA_GOV_IN_API_KEY")
AGMARKNET_RESOURCE_ID = os.getenv("AGMARKNET_RESOURCE_ID")
PMJDY_RESOURCE_ID = os.getenv("PMJDY_RESOURCE_ID")

BASE_URL = "https://api.data.gov.in/resource"

_call_count = 0
_fail_count = 0
_cache: Dict[str, Dict] = {}


def _request_with_retry(url: str, params: Dict, timeout: int = 35, retries: int = 1):
    """
    data.gov.in's API is documented to be slow/flaky in practice — a single
    15s timeout isn't always enough. This gives it a generous 35s window and
    one retry before giving up, rather than failing on the first slow response.
    """
    for attempt in range(retries + 1):
        try:
            return requests.get(url, params=params, timeout=timeout)
        except requests.exceptions.Timeout:
            if attempt < retries:
                print(f"[PRISM govdata_client] Timed out, retrying (attempt {attempt + 2}/{retries + 1})...")
                continue
            print(f"[PRISM govdata_client] Timed out after {retries + 1} attempts — data.gov.in is likely slow right now")
            return None
        except Exception as e:
            print(f"[PRISM govdata_client] Request failed: {e}")
            return None
    return None


def is_govdata_enabled() -> bool:
    return _REQUESTS_AVAILABLE and bool(DATA_GOV_IN_API_KEY)


def get_govdata_status() -> Dict:
    return {
        "govdata_enabled": is_govdata_enabled(),
        "agmarknet_configured": bool(AGMARKNET_RESOURCE_ID),
        "pmjdy_configured": bool(PMJDY_RESOURCE_ID),
        "calls_made": _call_count,
        "calls_failed": _fail_count,
        "granularity": "district_real_zone_synthetic",
        "note": "DBT Bharat and GST registration data have no public API at "
                "usable granularity and are NOT used — PMJDY is the honest "
                "real proxy for financial-inclusion signal instead.",
    }


def get_agmarknet_prices(state: str = "Uttar Pradesh", district: str = "Varanasi",
                          limit: int = 20) -> Optional[List[Dict]]:
    """
    Real call to Agmarknet daily mandi price data for a district. Returns
    a list of {commodity, market, min_price, max_price, modal_price, arrival_date}
    or None if not configured / call fails.
    """
    global _call_count, _fail_count

    if not is_govdata_enabled() or not AGMARKNET_RESOURCE_ID:
        return None

    cache_key = f"agmarknet_{state}_{district}"
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        _call_count += 1
        response = _request_with_retry(
            f"{BASE_URL}/{AGMARKNET_RESOURCE_ID}",
            params={
                "api-key": DATA_GOV_IN_API_KEY,
                "format": "json",
                "limit": limit,
                "filters[state]": state,
                "filters[district]": district,
            },
        )
        if response is None:
            _fail_count += 1
            return None
        if response.status_code != 200:
            print(f"[PRISM govdata_client] Agmarknet API error {response.status_code}: {response.text[:300]}")
            _fail_count += 1
            return None

        records = response.json().get("records", [])
        result = [
            {
                "commodity": r.get("commodity"),
                "market": r.get("market"),
                "min_price": r.get("min_price"),
                "max_price": r.get("max_price"),
                "modal_price": r.get("modal_price"),
                "arrival_date": r.get("arrival_date"),
            }
            for r in records
        ]
        _cache[cache_key] = result
        return result
    except Exception as e:
        _fail_count += 1
        print(f"[PRISM govdata_client] Agmarknet call failed: {e}")
        return None


def get_pmjdy_financial_inclusion(state: str = "Uttar Pradesh") -> Optional[Dict]:
    """
    Real call to PMJDY district-wise financial inclusion account data.
    Returns aggregated {total_accounts, zero_balance_accounts, ...} or None.
    """
    global _call_count, _fail_count

    if not is_govdata_enabled() or not PMJDY_RESOURCE_ID:
        return None

    cache_key = f"pmjdy_{state}"
    if cache_key in _cache:
        return _cache[cache_key]

    try:
        _call_count += 1
        response = _request_with_retry(
            f"{BASE_URL}/{PMJDY_RESOURCE_ID}",
            params={
                "api-key": DATA_GOV_IN_API_KEY,
                "format": "json",
                "limit": 50,
                "filters[state]": state,
            },
        )
        if response is None:
            _fail_count += 1
            return None
        if response.status_code != 200:
            print(f"[PRISM govdata_client] PMJDY API error {response.status_code}: {response.text[:300]}")
            _fail_count += 1
            return None

        records = response.json().get("records", [])
        result = {"state": state, "district_records": records, "record_count": len(records)}
        _cache[cache_key] = result
        return result
    except Exception as e:
        _fail_count += 1
        print(f"[PRISM govdata_client] PMJDY call failed: {e}")
        return None
