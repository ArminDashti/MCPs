"""
Test file for MCP tools without needing to run the server.
This allows direct testing of tool functionality.
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools import list_tools, call_tool
from src.human2agent import get_tool, execute


async def test_list_tools():
    """Test listing available tools."""
    
    try:
        tools = list_tools()
        for tool in tools:
            pass
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False


async def test_call_tool(name: str, arguments: dict[str, Any]):
    """Test calling a specific tool."""
    
    try:
        result = await call_tool(name, arguments)
        for content in result:
            pass
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False


async def test_direct_execute(arguments: dict[str, Any]):
    """Test executing the tool function directly."""
    
    try:
        result = await execute(arguments)
        for content in result:
            pass
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False


async def test_get_tool():
    """Test getting tool definition."""
    
    try:
        tool = get_tool()
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests."""
    
    # Test 3: Direct execute with a sample prompt
    test_prompt = "Write a dropdown for menu in the page"
    results = await test_direct_execute({"human_prompt": test_prompt})
    
    return results


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

