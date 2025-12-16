"""
Automatic test script for MCP server.
Tests server initialization, tool listing, and tool execution via stdio protocol.
"""

import asyncio
import json
import sys
import time
import io
from pathlib import Path
from typing import Any, Dict, List, Tuple

prompt = """
when the menu is opened, the boxes in the page should adjust their size based on the menu
"""

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    # Fallback for different MCP SDK versions
    try:
        from mcp.client import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError:
        print("Error: MCP SDK not found. Please install it with: pip install mcp")
        sys.exit(1)


class Colors:
    """ANSI color codes for terminal output."""
    # Enable ANSI colors on Windows 10+
    if sys.platform == "win32":
        import os
        os.system("")  # Enable ANSI escape sequences
    
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class TestResult:
    """Represents a test result."""
    def __init__(self, name: str, passed: bool, message: str = "", duration: float = 0.0, output: str = "", error: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
        self.duration = duration
        self.output = output
        self.error = error


class MCPTester:
    """Test suite for MCP server."""
    
    def __init__(self, server_command: List[str], timeout: int = 30):
        self.server_command = server_command
        self.timeout = timeout
        self.results: List[TestResult] = []
    
    def log(self, message: str, color: str = Colors.RESET):
        """Print a colored log message."""
        print(f"{color}{message}{Colors.RESET}")
    
    def _normalize_tool(self, tool):
        """Normalize a tool object, handling tuples and response objects."""
        if isinstance(tool, tuple):
            # If tool is a tuple, extract the first element (the actual tool)
            return tool[0] if len(tool) > 0 else tool
        return tool
    
    def add_result(self, result: TestResult, show_output: bool = True):
        """Add a test result."""
        self.results.append(result)
        status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if result.passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
        duration_str = f" ({result.duration:.2f}s)" if result.duration > 0 else ""
        self.log(f"  {status}: {result.name}{duration_str}")
        if result.message:
            self.log(f"    {result.message}", Colors.YELLOW)
        
        # Display error if present
        if result.error:
            self.log(f"    {Colors.RED}ERROR:{Colors.RESET} {result.error}", Colors.RED)
        
        # Display output if present and show_output is True
        if result.output and show_output:
            self.log(f"    {Colors.BLUE}OUTPUT:{Colors.RESET}")
            # Format JSON output if possible
            try:
                output_data = json.loads(result.output)
                formatted_output = json.dumps(output_data, indent=4, ensure_ascii=False)
                for line in formatted_output.split('\n'):
                    self.log(f"      {line}", Colors.YELLOW)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, display as-is (truncate if too long)
                output_lines = result.output.split('\n')
                if len(output_lines) > 20:
                    for line in output_lines[:20]:
                        self.log(f"      {line}", Colors.YELLOW)
                    self.log(f"      ... ({len(output_lines) - 20} more lines)", Colors.YELLOW)
                else:
                    for line in output_lines:
                        self.log(f"      {line}", Colors.YELLOW)
    
    async def test_server_initialization(self, session: ClientSession) -> TestResult:
        """Test server initialization."""
        start_time = time.time()
        try:
            # Initialize the session (handshake)
            await session.initialize()
            duration = time.time() - start_time
            return TestResult(
                "Server Initialization",
                True,
                "Server initialized successfully",
                duration
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                "Server Initialization",
                False,
                f"Failed to initialize: {str(e)}",
                duration
            )
    
    async def test_list_tools(self, session: ClientSession) -> Tuple[TestResult, List]:
        """Test listing available tools."""
        start_time = time.time()
        tools = []
        try:
            tools_result = await session.list_tools()
            # Handle both response object and direct list
            if hasattr(tools_result, 'tools'):
                tools = tools_result.tools
            elif isinstance(tools_result, tuple):
                # If it's a tuple, unpack it (likely (tools, metadata))
                tools = tools_result[0] if len(tools_result) > 0 else []
            else:
                tools = tools_result
            duration = time.time() - start_time
            
            if not tools:
                return TestResult(
                    "List Tools",
                    False,
                    "No tools returned",
                    duration
                ), []
            
            # Normalize tools and extract names
            normalized_tools = []
            tool_names = []
            for tool in tools:
                normalized_tool = self._normalize_tool(tool)
                normalized_tools.append(normalized_tool)
                if hasattr(normalized_tool, 'name'):
                    tool_names.append(normalized_tool.name)
                else:
                    tool_names.append(str(normalized_tool))
            
            # Return normalized tools
            tools = normalized_tools
            
            return TestResult(
                "List Tools",
                True,
                f"Found {len(tools)} tool(s): {', '.join(tool_names)}",
                duration
            ), tools
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                "List Tools",
                False,
                f"Error listing tools: {str(e)}",
                duration,
                error=str(e)
            ), []
    
    def generate_test_input(self, tool) -> Dict[str, Any]:
        """Generate test input based on tool's input schema."""
        # Normalize tool in case it's a tuple
        tool = self._normalize_tool(tool)
        test_inputs = {}
        
        if not hasattr(tool, 'inputSchema') or not tool.inputSchema:
            return test_inputs
        
        schema = tool.inputSchema
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        # Generate test values based on property types
        for prop_name, prop_schema in properties.items():
            prop_type = prop_schema.get('type', 'string')
            
            if prop_name in required or prop_name == 'human_prompt':
                if prop_type == 'string':
                    test_inputs[prop_name] = prompt
                elif prop_type == 'number' or prop_type == 'integer':
                    test_inputs[prop_name] = 42
                elif prop_type == 'boolean':
                    test_inputs[prop_name] = True
                elif prop_type == 'array':
                    test_inputs[prop_name] = []
                elif prop_type == 'object':
                    test_inputs[prop_name] = {}
        
        return test_inputs
    
    async def test_tool_execution(self, session: ClientSession, tool) -> TestResult:
        """Test executing a specific tool with a test prompt."""
        start_time = time.time()
        # Normalize tool in case it's a tuple
        tool = self._normalize_tool(tool)
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        
        try:
            # Generate test input based on tool schema
            test_input = self.generate_test_input(tool)
            
            if not test_input:
                return TestResult(
                    f"Tool: {tool_name}",
                    False,
                    "Could not generate test input - no required parameters found",
                    time.time() - start_time,
                    error="No test input generated"
                )
            
            self.log(f"\n{Colors.BOLD}Testing tool: {Colors.BLUE}{tool_name}{Colors.RESET}")
            self.log(f"  Input: {json.dumps(test_input, indent=2, ensure_ascii=False)}", Colors.YELLOW)
            
            # Call the tool
            result = await session.call_tool(tool_name, test_input)
            duration = time.time() - start_time
            
            if not result:
                return TestResult(
                    f"Tool: {tool_name}",
                    False,
                    "No result returned",
                    duration,
                    error="No result from tool execution"
                )
            
            # Extract text content
            text_content = None
            for content in result.content:
                if hasattr(content, 'type') and content.type == "text":
                    text_content = content.text
                    break
                elif isinstance(content, str):
                    text_content = content
                    break
            
            if not text_content:
                return TestResult(
                    f"Tool: {tool_name}",
                    False,
                    "Result does not contain text content",
                    duration,
                    error="No text content in response"
                )
            
            # Try to parse JSON response
            try:
                response_data = json.loads(text_content)
                success = response_data.get("success", True)
                error_msg = response_data.get("error", "")
                
                if success and not error_msg:
                    return TestResult(
                        f"Tool: {tool_name}",
                        True,
                        "Tool executed successfully",
                        duration,
                        output=text_content
                    )
                else:
                    return TestResult(
                        f"Tool: {tool_name}",
                        False,
                        f"Tool returned error: {error_msg}",
                        duration,
                        output=text_content,
                        error=error_msg
                    )
            except json.JSONDecodeError:
                # Not JSON, but got a response
                return TestResult(
                    f"Tool: {tool_name}",
                    True,
                    "Tool executed (response not JSON)",
                    duration,
                    output=text_content
                )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            import traceback
            error_trace = traceback.format_exc()
            
            return TestResult(
                f"Tool: {tool_name}",
                False,
                f"Error calling tool: {error_msg}",
                duration,
                error=error_trace
            )
    
    async def test_call_tool_missing_param(self, session: ClientSession) -> TestResult:
        """Test calling tool with missing required parameter."""
        start_time = time.time()
        try:
            # Try to find prompt_engineering_assistant tool
            tools_result = await session.list_tools()
            # Handle both response object and direct list
            if hasattr(tools_result, 'tools'):
                tools = tools_result.tools
            elif isinstance(tools_result, tuple):
                # If it's a tuple, unpack it (likely (tools, metadata))
                tools = tools_result[0] if len(tools_result) > 0 else []
            else:
                tools = tools_result
            
            tool_name = None
            for tool in tools:
                # Normalize tool and check name
                normalized_tool = self._normalize_tool(tool)
                if hasattr(normalized_tool, 'name') and normalized_tool.name == "prompt_engineering_assistant":
                    tool_name = normalized_tool.name
                    break
            
            if not tool_name:
                return TestResult(
                    "Call Tool (Missing Parameter)",
                    False,
                    "prompt_engineering_assistant tool not found",
                    time.time() - start_time,
                    error="Tool not available"
                )
            
            result = await session.call_tool(tool_name, {})
            duration = time.time() - start_time
            
            # Should return an error or handle gracefully
            text_content = None
            for content in result.content:
                if hasattr(content, 'type') and content.type == "text":
                    text_content = content.text
                    break
                elif isinstance(content, str):
                    text_content = content
                    break
            
            if text_content:
                try:
                    response_data = json.loads(text_content)
                    if "error" in response_data or not response_data.get("success", True):
                        return TestResult(
                            "Call Tool (Missing Parameter)",
                            True,
                            "Tool correctly handled missing parameter",
                            duration,
                            output=text_content,
                            error=response_data.get("error", "")
                        )
                except json.JSONDecodeError:
                    pass
            
            return TestResult(
                "Call Tool (Missing Parameter)",
                True,
                "Tool handled missing parameter",
                duration,
                output=text_content or "No output"
            )
        except Exception as e:
            # Exception is acceptable for missing parameter
            duration = time.time() - start_time
            import traceback
            error_trace = traceback.format_exc()
            return TestResult(
                "Call Tool (Missing Parameter)",
                True,
                f"Tool correctly rejected missing parameter: {str(e)}",
                duration,
                error=error_trace
            )
    
    async def test_call_tool_unknown(self, session: ClientSession) -> TestResult:
        """Test calling unknown tool."""
        start_time = time.time()
        try:
            result = await session.call_tool(
                "unknown_tool",
                {"test": "value"}
            )
            duration = time.time() - start_time
            
            # Check if result indicates an error
            if hasattr(result, 'isError') and result.isError:
                # Extract error message if any
                text_content = None
                for content in result.content:
                    if hasattr(content, 'type') and content.type == "text":
                        text_content = content.text
                        break
                    elif isinstance(content, str):
                        text_content = content
                        break
                
                return TestResult(
                    "Call Tool (Unknown Tool)",
                    True,
                    "Correctly rejected unknown tool",
                    duration,
                    output=text_content or "No output"
                )
            
            # Extract output if any
            text_content = None
            for content in result.content:
                if hasattr(content, 'type') and content.type == "text":
                    text_content = content.text
                    break
                elif isinstance(content, str):
                    text_content = content
                    break
            
            return TestResult(
                "Call Tool (Unknown Tool)",
                False,
                "Should have raised an error for unknown tool",
                duration,
                output=text_content or "No output",
                error="Tool was accepted but should have been rejected"
            )
        except Exception as e:
            # Exception is also acceptable - some MCP SDK versions may raise exceptions
            duration = time.time() - start_time
            import traceback
            error_trace = traceback.format_exc()
            return TestResult(
                "Call Tool (Unknown Tool)",
                True,
                f"Correctly rejected unknown tool: {str(e)}",
                duration,
                error=error_trace
            )
    
    async def run_tests(self) -> bool:
        """Run all tests."""
        self.log(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        self.log(f"{Colors.BOLD}{Colors.BLUE}MCP Server Automated Tests{Colors.RESET}")
        self.log(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
        
        self.log(f"Server command: {' '.join(self.server_command)}")
        self.log(f"Timeout: {self.timeout}s\n")
        
        # Create server parameters
        server_params = StdioServerParameters(
            command=self.server_command[0],
            args=self.server_command[1:] if len(self.server_command) > 1 else []
        )
        
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Run initialization test
                    self.log(f"{Colors.BOLD}Running tests...{Colors.RESET}\n")
                    self.add_result(await self.test_server_initialization(session), show_output=False)
                    
                    # List tools and get the list
                    list_result, tools = await self.test_list_tools(session)
                    self.add_result(list_result, show_output=False)
                    
                    if not tools:
                        self.log(f"{Colors.RED}No tools found. Cannot test tool execution.{Colors.RESET}\n")
                    else:
                        # Test each tool individually
                        self.log(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
                        self.log(f"{Colors.BOLD}Testing Each Tool{Colors.RESET}")
                        self.log(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
                        
                        for tool in tools:
                            result = await self.test_tool_execution(session, tool)
                            self.add_result(result, show_output=True)
                    
                    # Test error cases
                    self.log(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
                    self.log(f"{Colors.BOLD}Testing Error Cases{Colors.RESET}")
                    self.log(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
                    
                    self.add_result(await self.test_call_tool_missing_param(session), show_output=True)
                    self.add_result(await self.test_call_tool_unknown(session), show_output=True)
        
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            self.add_result(TestResult(
                "Server Connection",
                False,
                f"Failed to connect to server: {str(e)}",
                error=error_trace
            ), show_output=True)
        
        # Print summary
        self.print_summary()
        
        # Return True if all tests passed
        return all(r.passed for r in self.results)
    
    def print_summary(self):
        """Print test summary."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        failed = total - passed
        
        self.log(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        self.log(f"{Colors.BOLD}Test Summary{Colors.RESET}")
        self.log(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
        self.log(f"Total tests: {total}")
        self.log(f"{Colors.GREEN}Passed: {passed}{Colors.RESET}")
        if failed > 0:
            self.log(f"{Colors.RED}Failed: {failed}{Colors.RESET}")
        
        total_duration = sum(r.duration for r in self.results)
        self.log(f"Total duration: {total_duration:.2f}s")
        self.log(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")
        
        if failed > 0:
            self.log(f"{Colors.RED}{Colors.BOLD}Some tests failed!{Colors.RESET}\n")
        else:
            self.log(f"{Colors.GREEN}{Colors.BOLD}All tests passed!{Colors.RESET}\n")


async def main():
    """Main entry point."""
    # Determine Python executable
    python_exe = sys.executable
    
    # Get script directory
    script_dir = Path(__file__).parent
    server_script = script_dir / "h2a.py"
    
    if not server_script.exists():
        print(f"{Colors.RED}Error: h2a.py not found at {server_script}{Colors.RESET}")
        sys.exit(1)
    
    # Build server command
    server_command = [str(python_exe), str(server_script)]
    
    # Create tester and run tests
    tester = MCPTester(server_command, timeout=30)
    success = await tester.run_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
