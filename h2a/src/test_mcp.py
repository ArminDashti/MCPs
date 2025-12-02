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
    print("=" * 50)
    print("Testing list_tools()...")
    print("=" * 50)
    
    try:
        tools = list_tools()
        print(f"Found {len(tools)} tool(s):")
        for tool in tools:
            print(f"\nTool Name: {tool.name}")
            print(f"Description: {tool.description}")
            print(f"Input Schema: {json.dumps(tool.inputSchema, indent=2)}")
        return True
    except Exception as e:
        print(f"Error listing tools: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_call_tool(name: str, arguments: dict[str, Any]):
    """Test calling a specific tool."""
    print("\n" + "=" * 50)
    print(f"Testing call_tool('{name}', {json.dumps(arguments, indent=2)})...")
    print("=" * 50)
    
    try:
        result = await call_tool(name, arguments)
        print(f"\nResult ({len(result)} content item(s)):")
        for content in result:
            print(f"Type: {content.type}")
            print(f"Text:\n{content.text}")
        return True
    except Exception as e:
        print(f"Error calling tool: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_direct_execute(arguments: dict[str, Any]):
    """Test executing the tool function directly."""
    print("\n" + "=" * 50)
    print(f"Testing direct execute({json.dumps(arguments, indent=2)})...")
    print("=" * 50)
    
    try:
        result = await execute(arguments)
        print(f"\nResult ({len(result)} content item(s)):")
        for content in result:
            print(f"Type: {content.type}")
            print(f"Text:\n{content.text}")
        return True
    except Exception as e:
        print(f"Error executing tool: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_get_tool():
    """Test getting tool definition."""
    print("\n" + "=" * 50)
    print("Testing get_tool()...")
    print("=" * 50)
    
    try:
        tool = get_tool()
        print(f"Tool Name: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Input Schema: {json.dumps(tool.inputSchema, indent=2)}")
        return True
    except Exception as e:
        print(f"Error getting tool: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 50)
    print("MCP Tool Testing (Without Server)")
    print("=" * 50)
    
    results = []
    
    # Test 1: Get tool definition
    results.append(await test_get_tool())
    
    # Test 2: List tools
    results.append(await test_list_tools())
    
    # Test 3: Direct execute with a sample prompt
    test_prompt = "Write a dropdown for menu in the page"
    results.append(await test_direct_execute({"human_prompt": test_prompt}))
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Total tests: {len(results)}")
    print(f"Passed: {sum(results)}")
    print(f"Failed: {len(results) - sum(results)}")
    
    return all(results)


if __name__ == "__main__":
    # Run tests
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)

