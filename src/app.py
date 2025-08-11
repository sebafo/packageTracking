"""
Sample Shipment Tracking Agent using Semantic Kernel
This application demonstrates how to create a single agent that can answer
tracking questions using function calls to the Demo Shipment Tracker API.
"""

import asyncio
import os
import logging
import sys
import threading
import time
from typing import Annotated, Dict, Any
from datetime import datetime
import json
import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check for verbose mode flag
VERBOSE_MODE = '--verbose' in sys.argv or '-v' in sys.argv

# Configure logging based on verbose mode
if VERBOSE_MODE:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('semantic_kernel_debug.log')
        ]
    )
    
    # Set specific loggers for detailed function call tracking
    logging.getLogger('semantic_kernel').setLevel(logging.DEBUG)
    logging.getLogger('semantic_kernel.functions').setLevel(logging.DEBUG)
    logging.getLogger('semantic_kernel.connectors.ai').setLevel(logging.DEBUG)
    logging.getLogger('openai').setLevel(logging.DEBUG)
else:
    # Minimal logging for normal mode
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Create a custom logger for our application
logger = logging.getLogger(__name__)

# Environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
A2A_SERVER_URL = os.getenv("A2A_SERVER_URL")

# Shipment API configuration
SHIPMENT_API_BASE_URL = os.getenv("SHIPMENT_API_BASE_URL", "https://your-demo-domain.com")
SHIPMENT_API_KEY = os.getenv("SHIPMENT_API_KEY")  # Optional API key for authentication
USE_SIMULATED_API = os.getenv("USE_SIMULATED_API", "true").lower() == "true"

from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.filters.functions.function_invocation_context import FunctionInvocationContext
from semantic_kernel.filters.filter_types import FilterTypes


class Spinner:
    """A simple spinner animation for console output."""
    
    def __init__(self, message="Processing"):
        self.message = message
        self.spinner_chars = ['-', '\\', '|', '/']
        self.running = False
        self.thread = None
    
    def _spin(self):
        """Internal method to handle the spinning animation."""
        i = 0
        while self.running:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            print(f"\r{self.message}... {char}", end="", flush=True)
            time.sleep(0.1)
            i += 1
    
    def start(self):
        """Start the spinner animation."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop the spinner animation and clear the line."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=0.2)
            # Clear the spinner line more thoroughly
            print(f"\r{' ' * 80}\r", end="", flush=True)


class VerboseFunctionFilter:
    """Custom filter to log detailed function call information."""
    
    async def on_function_invocation(self, context: FunctionInvocationContext, next):
        """Log function invocation details before and after execution."""
        
        function_name = context.function.name
        plugin_name = context.function.plugin_name
        arguments = context.arguments
        
        logger.info("=" * 60)
        logger.info(f"🚀 FUNCTION INVOCATION STARTED")
        logger.info(f"📍 Plugin: {plugin_name}")
        logger.info(f"🔧 Function: {function_name}")
        logger.info(f"📝 Arguments: {dict(arguments) if arguments else 'None'}")
        logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 60)
        
        try:
            # Execute the function
            await next(context)
            
            logger.info("=" * 60)
            logger.info(f"✅ FUNCTION INVOCATION COMPLETED")
            logger.info(f"🔧 Function: {plugin_name}.{function_name}")
            logger.info(f"📤 Result: {context.result}")
            logger.info(f"⏰ Completed at: {datetime.now().isoformat()}")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error("=" * 60)
            logger.error(f"❌ FUNCTION INVOCATION FAILED")
            logger.error(f"🔧 Function: {plugin_name}.{function_name}")
            logger.error(f"💥 Error: {str(e)}")
            logger.error(f"⏰ Failed at: {datetime.now().isoformat()}")
            logger.error("=" * 60)
            raise


class ShipmentTrackingPlugin:
    """
    Plugin for tracking shipments using the Demo Shipment Tracker API.
    Can be configured to use either a real API or simulated responses.
    """
    
    def __init__(self, base_url: str = None, api_key: str = None, use_simulation: bool = True):
        self.base_url = base_url or SHIPMENT_API_BASE_URL
        self.api_key = api_key or SHIPMENT_API_KEY
        self.use_simulation = use_simulation
        self.api_endpoint = f"{self.base_url}/api/v2/package/lookup"
        
        print(f"ShipmentTrackingPlugin initialized:")
        print(f"  Base URL: {self.base_url}")
        print(f"  Using simulation: {self.use_simulation}")
        print(f"  API Key configured: {'Yes' if self.api_key else 'No'}")

    @kernel_function
    async def get_current_date_and_time(self) -> Dict[str, Any]:
        """
        Get the current date and time.
        """
        if VERBOSE_MODE:
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
        Track a package using its tracking ID and optionally filter by date range. Make sure to use the right format of the date.
        Returns detailed package information including status updates and item details.
        """
        
        # Log function call with parameters (only in verbose mode)
        if VERBOSE_MODE:
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
                if VERBOSE_MODE:
                    logger.info("🎭 Using simulated API response")
                result = self._simulate_api_response(tracking_id, from_date, to_date)
            else:
                # Make actual API call
                if VERBOSE_MODE:
                    logger.info("🌐 Making real API call")
                result = await self._call_real_api(params)
            
            if VERBOSE_MODE:
                logger.info(f"✅ Function result: {json.dumps(result, indent=2)}")
            return result
            
        except Exception as e:
            error_result = {
                "error": f"Failed to track package: {str(e)}",
                "tracking_id": tracking_id
            }
            if VERBOSE_MODE:
                logger.error(f"❌ Function error: {json.dumps(error_result, indent=2)}")
            return error_result
    
    async def _call_real_api(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make an actual HTTP request to the shipment tracking API.
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
                timestamp = datetime.now().isoformat()
                if VERBOSE_MODE:
                    logger.info(f"Making API request to: {self.api_endpoint}")
                    logger.info(f"Parameters: {params}")
                
                async with session.get(
                    self.api_endpoint,
                    params=params,
                    headers=headers
                ) as response:
                    response_timestamp = datetime.now().isoformat()
                    if VERBOSE_MODE:
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


class ShipmentTrackingAgent:
    """
    A conversational agent that can answer shipment tracking questions.
    """
    
    def __init__(self):
        self.kernel = Kernel()
        self.chat_history = ChatHistory()
        self.setup_kernel()
    
    def setup_kernel(self):
        """Initialize the kernel with AI services and plugins."""
        
        if VERBOSE_MODE:
            logger.info("🏗️  Setting up Semantic Kernel...")
        
        # Add Azure OpenAI chat completion service with environment variables
        chat_completion = AzureChatCompletion(
            deployment_name=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION
        )
        self.kernel.add_service(chat_completion)
        self.chat_completion = chat_completion
        
        # Add verbose function filter for detailed logging (only in verbose mode)
        if VERBOSE_MODE:
            verbose_filter = VerboseFunctionFilter()
            self.kernel.add_filter(FilterTypes.FUNCTION_INVOCATION, verbose_filter.on_function_invocation)
            logger.info("🔍 Added verbose function invocation filter")
        
        # Add the shipment tracking plugin with configuration
        tracking_plugin = ShipmentTrackingPlugin(
            base_url=SHIPMENT_API_BASE_URL,
            api_key=SHIPMENT_API_KEY,
            use_simulation=USE_SIMULATED_API
        )
        self.kernel.add_plugin(
            plugin=tracking_plugin,
            plugin_name="ShipmentTracking"
        )
        if VERBOSE_MODE:
            logger.info("📦 Added ShipmentTracking plugin")
        
        # Configure execution settings for function calling
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        if VERBOSE_MODE:
            logger.info("⚙️  Configured execution settings with auto function calling")
        
        # Add system message to set the agent's personality and role
        system_message = """
        You are a helpful shipment tracking assistant. You can help users track their packages 
        and provide detailed information about shipment status, locations, and delivery updates.
        
        When users ask about tracking packages, use the track_package function to get the most 
        up-to-date information. Always provide clear, friendly responses and explain the status 
        in an easy-to-understand way.

        If no date was added by the user, use the most recent last 4 weeks.
        
        If a package cannot be found, suggest that the user double-check the tracking number 
        and contact customer service if the issue persists.
        """
        
        self.chat_history.add_system_message(system_message)
        if VERBOSE_MODE:
            logger.info("💬 Added system message to chat history")
            logger.info("✅ Kernel setup completed")
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        """
        
        if VERBOSE_MODE:
            logger.info(f"👤 User message: {user_message}")
        
        # Add user message to chat history
        self.chat_history.add_user_message(user_message)
        
        try:
            if VERBOSE_MODE:
                logger.info("🤖 Sending request to LLM...")
            
            # Get response from the AI with function calling enabled
            result = await self.chat_completion.get_chat_message_content(
                chat_history=self.chat_history,
                settings=self.execution_settings,
                kernel=self.kernel,
            )
            
            if VERBOSE_MODE:
                logger.info(f"💬 LLM Response: {result}")
                
                # Log function calls if any were made
                if hasattr(result, 'function_call') and result.function_call:
                    logger.info(f"🔧 Function call detected: {result.function_call}")
            
            # Add the assistant's response to chat history
            self.chat_history.add_message(result)
            
            return str(result)
            
        except Exception as e:
            error_message = f"I'm sorry, I encountered an error while processing your request: {str(e)}"
            if VERBOSE_MODE:
                logger.error(f"❌ Chat error: {str(e)}")
            self.chat_history.add_assistant_message(error_message)
            return error_message
    
    def reset_conversation(self):
        """Reset the chat history while keeping the system message."""
        system_message = self.chat_history.messages[0]  # Keep the system message
        self.chat_history = ChatHistory()
        self.chat_history.add_message(system_message)


async def main():
    """
    Main function to run the shipment tracking agent demo.
    """
    
    if VERBOSE_MODE:
        print("🚚 Shipment Tracking Agent Demo (VERBOSE MODE)")
        print("=" * 50)
        print("📋 Verbose logging is enabled!")
        print("📝 Check 'semantic_kernel_debug.log' for detailed logs")
        print("🔍 Function calls and parameters will be logged to console and file")
        print("")
    else:
        print("🚚 Shipment Tracking Agent Demo")
        print("=" * 50)
        print("💡 Use --verbose or -v flag to enable detailed logging")
        print("")
    
    print("Ask me about tracking packages! Try these examples:")
    print("- 'Track package PKG123456789'")
    print("- 'What's the status of my shipment PKG987654321?'")
    print("- 'Can you help me track my package?'")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("=" * 50)
    
    # Initialize the agent
    if VERBOSE_MODE:
        logger.info("🚀 Starting Shipment Tracking Agent Demo")
    agent = ShipmentTrackingAgent()
    if VERBOSE_MODE:
        logger.info("✅ Agent initialized and ready")
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                print("\nAgent: Thank you for using the Shipment Tracking service. Have a great day! 👋")
                break
            
            if not user_input:
                continue
            
            # Get response from the agent with spinner animation
            spinner = Spinner()
            spinner.start()
            
            try:
                response = await agent.chat(user_input)
                spinner.stop()
                print("Agent:\n", end="")
                print(response)
            except Exception as e:
                spinner.stop()
                print(f"\nError: {str(e)}")
                print("Please try again.")
                continue
            
        except KeyboardInterrupt:
            print("\n\nAgent: Goodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")


if __name__ == "__main__":
    # Print usage information
    if '--help' in sys.argv or '-h' in sys.argv:
        print("🚚 Shipment Tracking Agent Demo")
        print("Usage: python app.py [options]")
        print("")
        print("Options:")
        print("  --verbose, -v    Enable verbose logging with detailed function call information")
        print("  --help, -h       Show this help message")
        print("")
        print("In verbose mode, you'll see:")
        print("  📦 Function calls with parameters")
        print("  🔧 LLM requests and responses")
        print("  📝 Detailed execution logs")
        print("  💾 Logs saved to 'semantic_kernel_debug.log'")
        exit(0)
    
    # Run the async main function
    asyncio.run(main())