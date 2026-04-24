"""
Flight search tool using Amadeus API.
"""

import os
import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime

from core import settings
from .base import ToolError, async_retry


def _get_amadeus_client() -> httpx.AsyncClient:
    """Get Amadeus API client."""
    return httpx.AsyncClient(
        base_url="https://api.amadeus.com" if settings.AMADEUS_ENVIRONMENT == "production" else "https://api.amadeus.com",
        timeout=30.0
    )


async def _get_access_token() -> str:
    """Get Amadeus API access token."""
    if not settings.AMADEUS_CLIENT_ID or not settings.AMADEUS_CLIENT_SECRET:
        raise ToolError("Amadeus API credentials not configured")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.amadeus.com/v1/security/oauth2/token",
            data={
                "grant_type": "client_credentials",
                "client_id": settings.AMADEUS_CLIENT_ID,
                "client_secret": settings.AMADEUS_CLIENT_SECRET
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["access_token"]


@async_retry(max_retries=2)
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    cabin_class: str = "ECONOMY",
    max_results: int = 5,
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Search for flights using Amadeus API.

    Args:
        origin: Origin airport code (e.g., JFK, LHR)
        destination: Destination airport code or city name
        departure_date: Departure date (YYYY-MM-DD)
        return_date: Return date (YYYY-MM-DD), omit for one-way
        adults: Number of adult passengers
        cabin_class: Cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
        max_results: Maximum results to return

    Returns:
        List of flight offers

    Raises:
        ToolError: If search fails
    """

    # Validate inputs
    if not origin or len(origin) < 2:
        raise ToolError("Origin must be a valid airport/city code")
    if not destination or len(destination) < 2:
        raise ToolError("Destination must be a valid airport/city code")

    try:
        # Validate dates
        datetime.strptime(departure_date, "%Y-%m-%d")
        if return_date:
            datetime.strptime(return_date, "%Y-%m-%d")
    except ValueError:
        raise ToolError("Dates must be in YYYY-MM-DD format")

    # If Amadeus not configured, return mock data for development
    if not settings.AMADEUS_CLIENT_ID:
        return _get_mock_flights(origin, destination, departure_date, return_date, adults, cabin_class)

    try:
        token = await _get_access_token()

        async with _get_amadeus_client() as client:
            params = {
                "originLocationCode": origin.upper(),
                "destinationLocationCode": destination.upper(),
                "departureDate": departure_date,
                "adults": adults,
                "travelClass": cabin_class,
                "max": max_results,
                "currencyCode": settings.getattr("currency", "EUR")
            }

            if return_date:
                params["returnDate"] = return_date

            response = await client.get(
                "/v2/shopping/flight-offers",
                headers={"Authorization": f"Bearer {token}"},
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Format results
            offers = data.get("data", [])
            formatted_offers = []

            for offer in offers:
                formatted_offer = _format_flight_offer(offer)
                if formatted_offer:
                    formatted_offers.append(formatted_offer)

            return formatted_offers

    except httpx.HTTPStatusError as e:
        raise ToolError(f"Flight search API error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        raise ToolError(f"Flight search failed: {str(e)}")


def _format_flight_offer(offer: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Format Amadeus offer into simplified structure."""
    try:
        price = offer.get("price", {})
        itineraries = offer.get("itineraries", [])

        formatted = {
            "id": offer.get("id"),
            "price": {
                "total": price.get("total"),
                "currency": price.get("currency"),
                "base": price.get("base"),
                "fees": price.get("fees", [])
            },
            "segments": []
        }

        for itinerary in itineraries:
            for segment in itinerary.get("segments", []):
                formatted["segments"].append({
                    "departure": {
                        "airport": segment.get("departure", {}).get("iataCode"),
                        "terminal": segment.get("departure", {}).get("terminal"),
                        "time": segment.get("departure", {}).get("at")
                    },
                    "arrival": {
                        "airport": segment.get("arrival", {}).get("iataCode"),
                        "terminal": segment.get("arrival", {}).get("terminal"),
                        "time": segment.get("arrival", {}).get("at")
                    },
                    "carrier": segment.get("carrierCode"),
                    "flight_number": segment.get("number"),
                    "aircraft": segment.get("aircraft", {}).get("code"),
                    "duration": segment.get("duration"),
                    "stops": len(segment.get("stops", []))
                })

        return formatted

    except Exception as e:
        return None


def _get_mock_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str],
    adults: int,
    cabin_class: str
) -> List[Dict[str, Any]]:
    """Return mock flight data for development when Amadeus not configured."""

    price_multiplier = {
        "ECONOMY": 1,
        "PREMIUM_ECONOMY": 1.5,
        "BUSINESS": 3,
        "FIRST": 6
    }.get(cabin_class, 1)

    base_price = 450 * price_multiplier * adults

    mock_flights = [
        {
            "id": "mock-1",
            "price": {
                "total": str(int(base_price)),
                "currency": "EUR",
                "base": str(int(base_price * 0.8)),
                "fees": [{"type": "SUPPLIER", "amount": str(int(base_price * 0.2))}]
            },
            "segments": [
                {
                    "departure": {
                        "airport": origin.upper(),
                        "terminal": "1",
                        "time": f"{departure_date}T09:00:00"
                    },
                    "arrival": {
                        "airport": destination.upper(),
                        "terminal": "2",
                        "time": f"{departure_date}T12:30:00"
                    },
                    "carrier": "LH",
                    "flight_number": "LH1234",
                    "aircraft": "A320",
                    "duration": "PT3H30M",
                    "stops": 0
                }
            ],
            "is_mock": True
        }
    ]

    if return_date:
        mock_flights[0]["segments"].append({
            "departure": {
                "airport": destination.upper(),
                "terminal": "2",
                "time": f"{return_date}T14:00:00"
            },
            "arrival": {
                "airport": origin.upper(),
                "terminal": "1",
                "time": f"{return_date}T17:30:00"
            },
            "carrier": "LH",
            "flight_number": "LH1235",
            "aircraft": "A320",
            "duration": "PT3H30M",
            "stops": 0
        })

    return mock_flights
