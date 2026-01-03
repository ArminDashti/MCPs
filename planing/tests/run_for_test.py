#!/usr/bin/env python3
"""
Test runner for MCP Planner.

This script provides a simple way to test the planner functionality
without requiring a full MCP server setup.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the parent directory to the path so we can import src
parent_path = Path(__file__).parent.parent
sys.path.insert(0, str(parent_path))

from src.tools.planner import planner_sync
from src.config import Config


def test_basic_planning():
    """Test basic planning functionality."""
    print("Testing basic planning functionality...")
    
    # Test prompts
    test_prompts = [
        "Plan a simple web application project",
        "Create a study plan for learning Python",
        "Organize a team meeting agenda",
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}: {prompt} ---")
        try:
            result = planner_sync(prompt)
            print(f"Success! Plan generated ({len(result)} characters)")
            print("First 200 characters:")
            print(result[:200] + "..." if len(result) > 200 else result)
        except Exception as e:
            print(f"Error: {e}")


def test_configuration():
    """Test configuration validation."""
    print("\nTesting configuration...")
    
    try:
        Config.validate()
        print("✓ Configuration is valid")
        print(f"✓ Model: {Config.PLANNER_MODEL}")
        print(f"✓ Log directory: {Config.LOG_DIR}")
    except Exception as e:
        print(f"✗ Configuration error: {e}")


def test_logging():
    """Test logging functionality."""
    print("\nTesting logging...")
    
    from src.utils.logger import get_log_stats
    
    try:
        stats = get_log_stats()
        print(f"✓ Prompt logs: {stats['prompt_logs']}")
        print(f"✓ Exception logs: {stats['exception_logs']}")
    except Exception as e:
        print(f"✗ Logging error: {e}")


def main():
    """Run all tests."""
    print("MCP Planner Test Suite")
    print("=" * 50)
    
    # Check if API key is configured
    if not Config.OPENROUTER_API_KEY or Config.OPENROUTER_API_KEY == "your_openrouter_api_key_here":
        print("⚠️  Warning: OpenRouter API key not configured")
        print("   Set 'openrouter_planing_key' in your .env file to test actual API calls")
        print("   Running configuration tests only...\n")
        
        test_configuration()
        test_logging()
        return
    
    # Run all tests
    test_configuration()
    test_logging()
    test_basic_planning()
    
    print("\n" + "=" * 50)
    print("Test suite completed!")


if __name__ == "__main__":
    main()
