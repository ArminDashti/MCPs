# PowerShell MCP Server

A Model Context Protocol (MCP) server for executing PowerShell commands on Windows systems.

## Features

- Execute any PowerShell command or script
- Support for custom working directories
- Asynchronous command execution
- Detailed output formatting with return codes and execution times
- Error handling and reporting

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the MCP Server

```bash
python powershell.py
```

### Available Tools

#### `execute_powershell`

Executes a PowerShell command on the Windows system.

**Parameters:**
- `command` (required): The PowerShell command to execute
- `working_directory` (optional): The working directory where the command should be executed

**Returns:**
- Formatted output containing:
  - Command executed
  - Working directory
  - Return code
  - Execution time
  - Success status
  - STDOUT output
  - STDERR output

## Example Usage

```python
# Execute a simple command
result = await execute_powershell_command("Get-Date")

# Execute command in specific directory
result = await execute_powershell_command("Get-ChildItem", "C:\\Users")
```

## Testing

Run the test script to verify functionality:

```bash
python test_powershell_mcp.py
```

## Security Considerations

This MCP server allows execution of arbitrary PowerShell commands, which means:

- Only use this in trusted environments
- Be aware of the security implications of allowing command execution
- Consider implementing additional security measures if needed

## Configuration

The server can be configured by modifying the MCP client configuration to include this server. The server name is "powershell".

## Dependencies

- `mcp>=0.9.0` - Model Context Protocol library
- Python 3.10+ - Required for async/await support

## License

This project follows the same license as the MCP framework.
