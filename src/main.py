"""
Command-line interface utilities for the shipment tracking application.
"""

import sys
import asyncio

from agent import ShipmentTrackingAgent
from utils import Spinner, setup_logging, check_verbose_mode


def print_help():
    """Print help information for the application."""
    print("🚚 Shipment Tracking Agent Demo")
    print("Usage: python main.py [options]")
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
    print("")
    print("Features:")
    print("  💬 Real-time streaming responses for better user experience")
    print("  🚀 Optimized for interactive conversations")


def print_welcome(verbose_mode: bool):
    """Print welcome message and instructions."""
    mode_str = " (VERBOSE MODE)" if verbose_mode else ""
    
    print(f"🚚 Shipment Tracking Agent Demo{mode_str}")
    print("=" * 50)
    
    if verbose_mode:
        print("📋 Verbose logging is enabled!")
        print("📝 Check 'semantic_kernel_debug.log' for detailed logs")
        print("🔍 Function calls and parameters will be logged to console and file")
        print("")
    else:
        print("💡 Use --verbose or -v flag to enable detailed logging")
    
    print("🚀 Streaming responses enabled - responses appear in real-time!")
    print("")
    
    print("Ask me about tracking packages! Try these examples:")
    print("- 'Track package PKG123456789'")
    print("- 'What's the status of my shipment PKG987654321?'")
    print("- 'Can you help me track my package?'")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("=" * 50)


async def run_interactive_session():
    """Run the interactive chat session."""
    # Check for help flag
    if '--help' in sys.argv or '-h' in sys.argv:
        print_help()
        return
    
    # Check for verbose mode
    verbose_mode = check_verbose_mode()
    
    # Setup logging
    logger = setup_logging(verbose_mode)
    
    # Print welcome message
    print_welcome(verbose_mode)
    
    # Initialize the agent
    try:
        if verbose_mode:
            logger.info("🚀 Starting Shipment Tracking Agent Demo with ChatCompletionAgent")
        agent = ShipmentTrackingAgent(verbose_mode=verbose_mode)
        if verbose_mode:
            logger.info("✅ Agent initialized and ready")
    except Exception as e:
        print(f"❌ Failed to initialize agent: {str(e)}")
        print("Please check your configuration and try again.")
        return
    
    # Main chat loop
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
            
            # Get response from the agent with streaming
            try:
                await agent.chat(user_input)
            except Exception as e:
                print(f"\nError: {str(e)}")
                print("Please try again.")
                continue
            
        except KeyboardInterrupt:
            print("\n\nAgent: Goodbye! 👋")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again.")

def main():
    """Main entry point that can be called from the root main.py."""
    asyncio.run(run_interactive_session())

if __name__ == "__main__":
    """Main entry point for the application."""
    main()
