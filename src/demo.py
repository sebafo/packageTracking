"""
Quick demo script for the Shipment Tracking Agent.
This script demonstrates the agent's capabilities with pre-defined test cases.
"""

import asyncio
import sys
import os

# Add the current directory to the Python path so we can import from agent.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import ShipmentTrackingAgent


async def demo():
    """Run a quick demonstration of the shipment tracking agent."""
    
    print("🚚 Shipment Tracking Agent Demo")
    print("=" * 60)
    
    # Initialize the agent
    agent = ShipmentTrackingAgent()
    
    # Test cases
    test_queries = [
        "Track package PKG123456789",
        "What's the status of my shipment PKG987654321?",
        "Can you tell me where package PKG123456789 is right now?",
        "I need help tracking my package ABC123 - can you help?",
        "What information do you have about tracking ID PKG999999999?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📦 Test Case {i}")
        print(f"User: {query}")
        print("Agent: ", end="")
        
        try:
            response = await agent.chat(query)
            print(response)
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 60)
    
    print("\n✅ Demo completed!")
    print("To run the interactive version, use: python main.py")


if __name__ == "__main__":
    asyncio.run(demo())
