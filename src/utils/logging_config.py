"""
Logging configuration and utilities for the shipment tracking application.
"""

import logging
import sys
from datetime import datetime


def setup_logging(verbose_mode: bool = False) -> logging.Logger:
    """
    Configure logging based on verbose mode.
    
    Args:
        verbose_mode: If True, enables detailed debug logging
        
    Returns:
        Logger instance for the application
    """
    if verbose_mode:
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
    return logging.getLogger(__name__)


def check_verbose_mode() -> bool:
    """Check if verbose mode is enabled via command line arguments."""
    return '--verbose' in sys.argv or '-v' in sys.argv
