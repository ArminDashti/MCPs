#!/usr/bin/env python3
"""
Test script to verify that the planing MCP server loads tools properly.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the src directory to the path
parent_path = Path(__file__).parent / "src"
sys.path.insert(0, str(parent_path))

from tool_registry import list_tools, tool_exists, call_tool


async def test_tools_loading():
    """Test that tools are loaded properly."""
    print("Testing tool loading...")

    # Test list_tools
    tools = list_tools()
    print(f"✓ Found {len(tools)} tools")

    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")

    # Test tool_exists
    if tool_exists("planner"):
        print("✓ 'planner' tool exists")
    else:
        print("✗ 'planner' tool not found")
        return False

    if not tool_exists("nonexistent_tool"):
        print("✓ Non-existent tool correctly returns False")
    else:
        print("✗ tool_exists returned True for non-existent tool")
        return False

    # Test call_tool (without actually making API calls)
    try:
        # This should work but will fail due to missing API key
        result = await call_tool("planner", {"prompt": "test"})
        print("✓ call_tool executed (may have failed due to config, but that's expected)")
    except Exception as e:
        if "OPENROUTER_API_KEY" in str(e):
            print("✓ call_tool failed as expected due to missing API key")
        else:
            print(f"✗ call_tool failed unexpectedly: {e}")
            return False

    return True


async def main():
    """Run the tests."""
    print("Planing MCP Server Tool Loading Test")
    print("=" * 40)

    success = await test_tools_loading()

    print("=" * 40)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")

    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)