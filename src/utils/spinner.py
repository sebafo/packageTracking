"""
Utility classes and functions for the shipment tracking application.
"""

import threading
import time


class Spinner:
    """A simple spinner animation for console output."""
    
    def __init__(self, message: str = "Processing"):
        """
        Initialize the spinner with a custom message.
        
        Args:
            message: The message to display alongside the spinner
        """
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
