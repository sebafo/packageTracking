"""
Custom filters for Semantic Kernel function invocation logging.
"""

import logging
from datetime import datetime
from semantic_kernel.filters.functions.function_invocation_context import FunctionInvocationContext

logger = logging.getLogger(__name__)


class VerboseFunctionFilter:
    """Custom filter to log detailed function call information."""
    
    async def on_function_invocation(self, context: FunctionInvocationContext, next):
        """
        Log function invocation details before and after execution.
        
        Args:
            context: The function invocation context
            next: The next filter or function in the chain
        """
        
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
