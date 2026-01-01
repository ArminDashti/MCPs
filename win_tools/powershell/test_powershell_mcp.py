import asyncio
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.powershell import execute_powershell_command


async def test_powershell_execution():
    """Test the PowerShell execution functionality."""
    print("Testing PowerShell MCP...")
    
    # Test 1: Simple command
    print("\n=== Test 1: Simple Get-Date command ===")
    result = await execute_powershell_command("Get-Date")
    print(f"Success: {result['success']}")
    print(f"Return Code: {result['return_code']}")
    print(f"STDOUT: {result['stdout']}")
    print(f"STDERR: {result['stderr']}")
    
    # Test 2: Command with working directory
    print("\n=== Test 2: Get-Location with working directory ===")
    result = await execute_powershell_command("Get-Location", "C:\\")
    print(f"Success: {result['success']}")
    print(f"Return Code: {result['return_code']}")
    print(f"STDOUT: {result['stdout']}")
    print(f"STDERR: {result['stderr']}")
    
    # Test 3: Command that produces error
    print("\n=== Test 3: Invalid command (should produce error) ===")
    result = await execute_powershell_command("Get-InvalidCommand")
    print(f"Success: {result['success']}")
    print(f"Return Code: {result['return_code']}")
    print(f"STDOUT: {result['stdout']}")
    print(f"STDERR: {result['stderr']}")
    
    print("\n=== All tests completed ===")


if __name__ == "__main__":
    asyncio.run(test_powershell_execution())
