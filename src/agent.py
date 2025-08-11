"""
Core agent functionality for the shipment tracking application.
"""

import logging
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.filters.filter_types import FilterTypes

from config import Config
from filters import VerboseFunctionFilter
from plugins import ShipmentTrackingPlugin

logger = logging.getLogger(__name__)


class ShipmentTrackingAgent:
    """
    A conversational agent that can answer shipment tracking questions.
    """
    
    def __init__(self, verbose_mode: bool = False):
        """
        Initialize the shipment tracking agent.
        
        Args:
            verbose_mode: Whether to enable verbose logging and function filtering
        """
        self.verbose_mode = verbose_mode
        self.kernel = Kernel()
        self.chat_history = ChatHistory()
        self.setup_kernel()
    
    def setup_kernel(self):
        """Initialize the kernel with AI services and plugins."""
        
        if self.verbose_mode:
            logger.info("🏗️  Setting up Semantic Kernel...")
        
        # Validate configuration
        if not Config.validate_required_config():
            missing = Config.get_missing_config()
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        # Add Azure OpenAI chat completion service with environment variables
        chat_completion = AzureChatCompletion(
            deployment_name=Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION
        )
        self.kernel.add_service(chat_completion)
        self.chat_completion = chat_completion
        
        # Add verbose function filter for detailed logging (only in verbose mode)
        if self.verbose_mode:
            verbose_filter = VerboseFunctionFilter()
            self.kernel.add_filter(FilterTypes.FUNCTION_INVOCATION, verbose_filter.on_function_invocation)
            logger.info("🔍 Added verbose function invocation filter")
        
        # Add the shipment tracking plugin with configuration
        tracking_plugin = ShipmentTrackingPlugin(
            base_url=Config.SHIPMENT_API_BASE_URL,
            api_key=Config.SHIPMENT_API_KEY,
            use_simulation=Config.USE_SIMULATED_API
        )
        self.kernel.add_plugin(
            plugin=tracking_plugin,
            plugin_name="ShipmentTracking"
        )
        if self.verbose_mode:
            logger.info("📦 Added ShipmentTracking plugin")
        
        # Configure execution settings for function calling
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()
        if self.verbose_mode:
            logger.info("⚙️  Configured execution settings with auto function calling")
        
        # Add system message to set the agent's personality and role
        system_message = """
        You are a helpful shipment tracking assistant. You can help users track their packages 
        and provide detailed information about shipment status, locations, and delivery updates.

        Make sure to use the current date and time (get_current_date_and_time).
        If the user didn't provide any time information, use the most recent date within the last four weeks.

        When users ask about tracking packages, use the track_package function to get the most 
        up-to-date information. Always provide clear, friendly responses and explain the status 
        in an easy-to-understand way.
        Don't say, that there is no update unless you have checked all possible sources.

        If a package cannot be found, suggest that the user double-check the tracking number 
        and contact customer service if the issue persists.
        """
        
        self.chat_history.add_system_message(system_message)
        if self.verbose_mode:
            logger.info("💬 Added system message to chat history")
            logger.info("✅ Kernel setup completed")
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            user_message: The user's input message
            
        Returns:
            The agent's response as a string
        """
        
        if self.verbose_mode:
            logger.info(f"👤 User message: {user_message}")
        
        # Add user message to chat history
        self.chat_history.add_user_message(user_message)
        
        try:
            if self.verbose_mode:
                logger.info("🤖 Sending request to LLM...")
            
            # Get response from the AI with function calling enabled
            result = await self.chat_completion.get_chat_message_content(
                chat_history=self.chat_history,
                settings=self.execution_settings,
                kernel=self.kernel,
            )
            
            if self.verbose_mode:
                logger.info(f"💬 LLM Response: {result}")
                
                # Log function calls if any were made
                if hasattr(result, 'function_call') and result.function_call:
                    logger.info(f"🔧 Function call detected: {result.function_call}")
            
            # Add the assistant's response to chat history
            self.chat_history.add_message(result)
            
            return str(result)
            
        except Exception as e:
            error_message = f"I'm sorry, I encountered an error while processing your request: {str(e)}"
            if self.verbose_mode:
                logger.error(f"❌ Chat error: {str(e)}")
            self.chat_history.add_assistant_message(error_message)
            return error_message
    
    def reset_conversation(self):
        """Reset the chat history while keeping the system message."""
        system_message = self.chat_history.messages[0]  # Keep the system message
        self.chat_history = ChatHistory()
        self.chat_history.add_message(system_message)
