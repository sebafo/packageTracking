"""
Shipment tracking plugin for interacting with the Demo Shipment Tracker API.
"""

import asyncio
import json
import logging
from typing import Annotated, Dict, Any
from datetime import datetime

import aiohttp
from semantic_kernel.functions import kernel_function

logger = logging.getLogger(__name__)


class ShipmentTrackingPlugin:
    """
    Plugin for tracking shipments using the Demo Shipment Tracker API.
    Can be configured to use either a real API or simulated responses.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, use_simulation: bool = True):
        """
        Initialize the shipment tracking plugin.
        
        Args:
            base_url: Base URL for the shipment API
            api_key: Optional API key for authentication
            use_simulation: Whether to use simulated API responses
        """
        self.base_url = base_url
        self.api_key = api_key
        self.use_simulation = use_simulation
        self.api_endpoint = f"{self.base_url}/api/v2/package/lookup" if base_url else None
        
        print(f"ShipmentTrackingPlugin initialized:")
        print(f"  Base URL: {self.base_url}")
        print(f"  Using simulation: {self.use_simulation}")
        print(f"  API Key configured: {'Yes' if self.api_key else 'No'}")

    @kernel_function
    async def get_current_date_and_time(self) -> Dict[str, Any]:
        """
        Get the current date and time.
        
        Returns:
            Dictionary containing the current date and time in ISO format
        """
        logger.info("🔧 FUNCTION CALLED: get_current_date_and_time")
        return {"current_date_and_time": datetime.now().isoformat()}

    @kernel_function
    async def track_package(
        self,
        tracking_id: Annotated[str, "The tracking ID of the package to track"],
        from_date: Annotated[str, "Start date for tracking period in YYYY-MM-DD format"] = None,
        to_date: Annotated[str, "End date for tracking period in YYYY-MM-DD format"] = None
    ) -> Dict[str, Any]:
        """
        Track a package using its tracking ID and optionally filter by date range.
        Make sure to use the right format of the date.
        Returns detailed package information including status updates and item details.
        
        Args:
            tracking_id: The tracking ID of the package to track
            from_date: Start date for tracking period in YYYY-MM-DD format
            to_date: End date for tracking period in YYYY-MM-DD format
            
        Returns:
            Dictionary containing package tracking information
        """
        
        # Log function call with parameters
        logger.info(f"🔧 FUNCTION CALLED: track_package")
        logger.info(f"📦 Parameters: tracking_id='{tracking_id}', from_date='{from_date}', to_date='{to_date}'")
        
        # Build query parameters
        params = {"trackingId": tracking_id}
        if from_date:
            params["fromDate"] = from_date
        if to_date:
            params["toDate"] = to_date
        
        try:
            if self.use_simulation:
                # Use simulated response for demo purposes
                logger.info("🎭 Using simulated API response")
                result = self._simulate_api_response(tracking_id, from_date, to_date)
            else:
                # Make actual API call
                logger.info("🌐 Making real API call")
                result = await self._call_real_api(params)
            
            logger.info(f"✅ Function result: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            error_result = {
                "error": f"Failed to track package: {str(e)}",
                "tracking_id": tracking_id
            }
            logger.error(f"❌ Function error: {json.dumps(error_result, indent=2)}")
            return error_result
    
    async def _call_real_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an actual HTTP request to the shipment tracking API.
        
        Args:
            params: Query parameters for the API request
            
        Returns:
            API response data
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add API key to headers if configured
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            # Alternative header formats you might need:
            # headers["X-API-Key"] = self.api_key
            # headers["Authorization"] = f"ApiKey {self.api_key}"
        
        timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                logger.info(f"Making API request to: {self.api_endpoint}")
                logger.info(f"Parameters: {params}")
                
                async with session.get(
                    self.api_endpoint,
                    params=params,
                    headers=headers
                ) as response:
                    logger.info(f"API response status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        return data
                    elif response.status == 404:
                        return {
                            "error": "Package not found",
                            "tracking_id": params.get("trackingId"),
                            "status_code": 404
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "error": f"API request failed with status {response.status}: {error_text}",
                            "tracking_id": params.get("trackingId"),
                            "status_code": response.status
                        }
                        
            except aiohttp.ClientError as e:
                return {
                    "error": f"Network error: {str(e)}",
                    "tracking_id": params.get("trackingId")
                }
            except asyncio.TimeoutError:
                return {
                    "error": "Request timeout - the API took too long to respond",
                    "tracking_id": params.get("trackingId")
                }
    
    def _simulate_api_response(self, tracking_id: str, from_date: str = None, to_date: str = None) -> Dict[str, Any]:
        """
        Simulate the API response based on the API specification.
        In a real implementation, this would be replaced with actual HTTP calls.
        
        Args:
            tracking_id: The tracking ID to simulate response for
            from_date: Start date filter (unused in simulation)
            to_date: End date filter (unused in simulation)
            
        Returns:
            Simulated API response data
        """
        
        # Simulate different scenarios based on tracking ID
        if tracking_id.upper() == "PKG123456789":
            return {
                "packages": [
                    {
                        "packageKey": 987654321,
                        "trackingId": "PKG123456789",
                        "datePartition": 20250811,
                        "serviceType": "EXPRESS",
                        "customerReference": "REF20250811",
                        "originCountry": "DE",
                        "originCity": "Munich",
                        "originFacility": "MUC1",
                        "destinationCountry": "FR",
                        "destinationCity": "Paris",
                        "destinationFacility": "CDG2",
                        "senderName": "REDACTED",
                        "senderContact": "REDACTED",
                        "recipientName": "REDACTED",
                        "recipientContact": "REDACTED",
                        "dispatchDate": "2025-08-11T09:00:00",
                        "itemCount": 2,
                        "packageContents": "ELECTRONICS",
                        "currency": "EUR",
                        "declaredValue": 199.99,
                        "declaredWeight": 2.5,
                        "actualWeight": 2.8,
                        "items": [
                            {
                                "itemId": "ITM987654321",
                                "itemWeightDeclared": 1.2,
                                "itemWeightActual": 1.3,
                                "itemDescription": "Tablet",
                                "statusUpdates": [
                                    {
                                        "statusCode": "ARR",
                                        "statusTimestamp": "2025-08-11T10:00:00",
                                        "statusLocation": "MUC1",
                                        "statusRemarks": "Arrived at origin facility"
                                    },
                                    {
                                        "statusCode": "DEP",
                                        "statusTimestamp": "2025-08-11T11:00:00",
                                        "statusLocation": "MUC1",
                                        "statusRemarks": "Departed from origin facility"
                                    },
                                    {
                                        "statusCode": "TRN",
                                        "statusTimestamp": "2025-08-11T14:00:00",
                                        "statusLocation": "HUB1",
                                        "statusRemarks": "In transit to destination"
                                    }
                                ]
                            }
                        ],
                        "statusUpdates": [
                            {
                                "statusCode": "DEP",
                                "statusTimestamp": "2025-08-11T11:00:00",
                                "statusLocation": "MUC1",
                                "statusRemarks": "Departed from origin facility"
                            },
                            {
                                "statusCode": "TRN",
                                "statusTimestamp": "2025-08-11T14:00:00",
                                "statusLocation": "HUB1",
                                "statusRemarks": "In transit to destination"
                            }
                        ]
                    }
                ]
            }
        elif tracking_id.upper().startswith("PKG"):
            # Generic package response
            return {
                "packages": [
                    {
                        "packageKey": 123456789,
                        "trackingId": tracking_id,
                        "datePartition": 20250811,
                        "serviceType": "STANDARD",
                        "customerReference": f"REF{tracking_id[-6:]}",
                        "originCountry": "US",
                        "originCity": "New York",
                        "originFacility": "NYC1",
                        "destinationCountry": "US",
                        "destinationCity": "Los Angeles",
                        "destinationFacility": "LAX1",
                        "senderName": "REDACTED",
                        "senderContact": "REDACTED",
                        "recipientName": "REDACTED",
                        "recipientContact": "REDACTED",
                        "dispatchDate": "2025-08-11T08:00:00",
                        "itemCount": 1,
                        "packageContents": "DOCUMENTS",
                        "currency": "USD",
                        "declaredValue": 50.00,
                        "declaredWeight": 0.5,
                        "actualWeight": 0.6,
                        "items": [
                            {
                                "itemId": f"ITM{tracking_id[-6:]}",
                                "itemWeightDeclared": 0.5,
                                "itemWeightActual": 0.6,
                                "itemDescription": "Business Documents",
                                "statusUpdates": [
                                    {
                                        "statusCode": "ARR",
                                        "statusTimestamp": "2025-08-11T09:00:00",
                                        "statusLocation": "NYC1",
                                        "statusRemarks": "Arrived at origin facility"
                                    },
                                    {
                                        "statusCode": "DEL",
                                        "statusTimestamp": "2025-08-11T16:00:00",
                                        "statusLocation": "LAX1",
                                        "statusRemarks": "Delivered successfully"
                                    }
                                ]
                            }
                        ],
                        "statusUpdates": [
                            {
                                "statusCode": "ARR",
                                "statusTimestamp": "2025-08-11T09:00:00",
                                "statusLocation": "NYC1",
                                "statusRemarks": "Arrived at origin facility"
                            },
                            {
                                "statusCode": "DEL",
                                "statusTimestamp": "2025-08-11T16:00:00",
                                "statusLocation": "LAX1",
                                "statusRemarks": "Delivered successfully"
                            }
                        ]
                    }
                ]
            }
        else:
            # Simulate 404 response for unknown tracking IDs
            return {
                "error": "Package not found",
                "tracking_id": tracking_id,
                "status_code": 404
            }
