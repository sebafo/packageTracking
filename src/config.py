"""
Configuration management for the shipment tracking application.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class to manage environment variables."""
    
    # Azure OpenAI configuration
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
    
    # Server configuration
    A2A_SERVER_URL = os.getenv("A2A_SERVER_URL")
    
    # Shipment API configuration
    SHIPMENT_API_BASE_URL = os.getenv("SHIPMENT_API_BASE_URL", "https://your-demo-domain.com")
    SHIPMENT_API_KEY = os.getenv("SHIPMENT_API_KEY")  # Optional API key for authentication
    USE_SIMULATED_API = os.getenv("USE_SIMULATED_API", "true").lower() == "true"
    
    @classmethod
    def validate_required_config(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            True if all required config is present, False otherwise
        """
        required_vars = [
            cls.AZURE_OPENAI_ENDPOINT,
            cls.AZURE_OPENAI_API_KEY,
            cls.AZURE_OPENAI_API_VERSION,
            cls.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
        ]
        
        return all(var is not None for var in required_vars)
    
    @classmethod
    def get_missing_config(cls) -> list[str]:
        """
        Get a list of missing required configuration variables.
        
        Returns:
            List of missing environment variable names
        """
        missing = []
        
        if not cls.AZURE_OPENAI_ENDPOINT:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not cls.AZURE_OPENAI_API_KEY:
            missing.append("AZURE_OPENAI_API_KEY")
        if not cls.AZURE_OPENAI_API_VERSION:
            missing.append("AZURE_OPENAI_API_VERSION")
        if not cls.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME:
            missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
            
        return missing
