# MCP Planner

An MCP (Model Context Protocol) server that provides AI-powered planning capabilities using external LLM services.

## Features

- AI-powered task planning and breakdown
- Configurable LLM provider (OpenRouter)
- Comprehensive logging and error handling
- Easy MCP server integration

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd planing
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Configuration

Create a `.env` file with the following variables:

```env
# OpenRouter API configuration
openrouter_planing_key=your_openrouter_api_key_here
mcp_planner_model=anthropic/claude-3.5-sonnet

# Optional: Custom logging directory
MCP_PLANNER_LOG_DIR=~/.mcp_planner
```

## MCP Server Configuration

Add this to your MCP client configuration (e.g., Claude Desktop):

```json
{
  "mcpServers": {
    "planner": {
      "command": "python",
      "args": ["-m", "src.server"],
      "env": {
        "openrouter_planing_key": "your_api_key_here",
        "mcp_planner_model": "anthropic/claude-3.5-sonnet"
      }
    }
  }
}
```

## Usage

Once configured, the planner tool will be available in your MCP client. Use it to:

- Break down complex tasks into actionable steps
- Generate project plans and timelines
- Create structured approaches to problems
- Get AI assistance with task organization

## Development

Install development dependencies:
```bash
pip install -e ".[dev]"
```

Run tests:
```bash
python -m pytest tests/
```

Format code:
```bash
black src/
ruff check src/
```

## License

MIT License
