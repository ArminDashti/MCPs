#!/usr/bin/env python3
"""
Run script for the MCP Planner server.

This script properly sets up the Python path and runs the MCP server.
"""

import sys
import os

# Add the current directory to Python path so src module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the server
from src.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())