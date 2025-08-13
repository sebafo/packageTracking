"""
Core agent functionality for the shipment tracking application.
"""

import logging
from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent, ChatHistoryAgentThread
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent, FunctionCallContent, FunctionResultContent
from semantic_kernel.filters.filter_types import FilterTypes

from config import Config
from filters import VerboseFunctionFilter
from plugins import ShipmentTrackingPlugin

logger = logging.getLogger(__name__)


class ShipmentTrackingAgent:
    """
    A conversational agent that can answer shipment tracking questions using ChatCompletionAgent framework.
    """
    
    def __init__(self, verbose_mode: bool = False):
        """
        Initialize the shipment tracking agent.
        
        Args:
            verbose_mode: Whether to enable verbose logging and function filtering
        """
        self.verbose_mode = verbose_mode
        self.agent: Optional[ChatCompletionAgent] = None
        self.thread: Optional[ChatHistoryAgentThread] = None
        self.setup_agent()
    
    def setup_agent(self):
        """Initialize the agent using the ChatCompletionAgent framework."""
        
        if self.verbose_mode:
            logger.info("🏗️  Setting up Semantic Kernel ChatCompletionAgent...")
        
        # Validate configuration
        if not Config.validate_required_config():
            missing = Config.get_missing_config()
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        # Create kernel and add services
        kernel = Kernel()
        
        # Add Azure OpenAI chat completion service
        chat_completion = AzureChatCompletion(
            deployment_name=Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION
        )
        kernel.add_service(chat_completion)
        
        # Add verbose function filter for detailed logging (only in verbose mode)
        if self.verbose_mode:
            verbose_filter = VerboseFunctionFilter()
            kernel.add_filter(FilterTypes.FUNCTION_INVOCATION, verbose_filter.on_function_invocation)
            logger.info("🔍 Added verbose function invocation filter")
        
        # Add the shipment tracking plugin
        tracking_plugin = ShipmentTrackingPlugin(
            base_url=Config.SHIPMENT_API_BASE_URL,
            api_key=Config.SHIPMENT_API_KEY,
            use_simulation=Config.USE_SIMULATED_API
        )
        kernel.add_plugin(
            plugin=tracking_plugin,
            plugin_name="ShipmentTracking"
        )
        if self.verbose_mode:
            logger.info("📦 Added ShipmentTracking plugin")
        
        # Create the agent using the ChatCompletionAgent framework
        self.agent = ChatCompletionAgent(
            kernel=kernel,
            name="ShipmentTrackingAgent",
            instructions="""
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
        )
        
        if self.verbose_mode:
            logger.info("✅ ChatCompletionAgent setup completed")
    
    async def chat(self, user_message: str) -> str:
        """
        Process a user message with streaming response for better user experience.
        
        Args:
            user_message: The user's input message
            
        Returns:
            The complete agent's response as a string
        """
        
        if self.verbose_mode:
            logger.info(f"👤 User message: {user_message}")
        
        try:
            response_parts = []
            print("Agent: ", end="", flush=True)
            
            # Use streaming invoke
            async for response in self.agent.invoke_stream(
                messages=user_message,
                thread=self.thread
            ):
                if hasattr(response, 'content') and response.content:
                    # Convert content to string if it's not already
                    content_str = str(response.content)
                    print(content_str, end="", flush=True)
                    response_parts.append(content_str)
                    
                # Update thread from the last response
                if hasattr(response, 'thread') and response.thread:
                    self.thread = response.thread
            
            print()  # New line after streaming
            
            complete_response = "".join(response_parts)
            if self.verbose_mode:
                logger.info(f"💬 Complete streaming response: {complete_response}")
            
            return complete_response
                
        except Exception as e:
            error_message = f"I'm sorry, I encountered an error while processing your request: {str(e)}"
            if self.verbose_mode:
                logger.error(f"❌ Chat error: {str(e)}")
            print(f"\n{error_message}")
            return error_message
    
    def reset_conversation(self):
        """Reset the conversation thread."""
        self.thread = None
        if self.verbose_mode:
            logger.info("🔄 Conversation thread reset")
