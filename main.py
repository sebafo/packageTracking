#!/usr/bin/env python3
"""
Main entry point for the shipment tracking application.
Run this from the project root directory.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main import main

if __name__ == "__main__":
    main()
