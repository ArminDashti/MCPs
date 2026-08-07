# OpenRouter MCP Server

An [MCP](https://modelcontextprotocol.io) server that lets agents call [OpenRouter](https://openrouter.ai) models by name from a user-defined allowed-models file.

## Tools

| Tool | Description |
|------|-------------|
| `chat_completion` | Send a chat completion request using a configured model name |

## Prerequisites

- Node.js 18+
- An [OpenRouter API key](https://openrouter.ai/settings/keys)

## Setup

```bash
cd openrouter
npm install
cp config.example.json config.json
cp models.example.json models.json
# Edit both files
npm run build
```

## Configuration

### `config.json`

Server settings (path via `OPENROUTER_CONFIG`, default `./config.json`):

```json
{
  "modelsFile": "models.json",
  "defaultModel": "gemini-flash",
  "logsDir": "C:/logs/openrouter"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `modelsFile` | No | Path to allowed models file, relative to `config.json` (default: `models.json`) |
| `defaultModel` | Yes | Model name used when the agent omits `model` (must exist in `models.json`) |
| `logsDir` | No | Folder where request logs are written |

### `models.json`

Allowed models the agent can choose from. Keys are names the agent sends; values are OpenRouter model IDs.

Path via `OPENROUTER_MODELS`, or `modelsFile` in `config.json`, or default `models.json` next to `config.json`.

```json
{
  "claude": "anthropic/claude-sonnet-4",
  "gemini-flash": "google/gemini-2.5-flash-preview"
}
```

The agent passes one of these **names** (e.g. `"claude"`), or omits `model` to use `defaultModel` from `config.json`.

### Request logs

When `logsDir` is set, each call writes `<YYYY-MM-DD-HH-mm-ss>.log`:

```
anthropic/claude-sonnet-4

--------------------------------------------------------------------
What is MCP?

--------------------------------------------------------------------
MCP is a protocol that lets applications provide context to LLMs...
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | Yes | Your OpenRouter API key |
| `OPENROUTER_CONFIG` | No | Path to `config.json` (default: `./config.json`) |
| `OPENROUTER_MODELS` | No | Path to allowed models file (overrides `modelsFile`) |
| `OPENROUTER_HTTP_REFERER` | No | Site URL for OpenRouter rankings |
| `OPENROUTER_APP_TITLE` | No | App name shown on OpenRouter (default: `openrouter-mcp`) |
| `OPENROUTER_BASE_URL` | No | API base URL (default: `https://openrouter.ai/api/v1`) |

## Cursor Configuration

```json
{
  "mcpServers": {
    "openrouter": {
      "command": "node",
      "args": ["C:/Users/armin/Documents/GitHub/MCPs/openrouter/dist/index.js"],
      "env": {
        "OPENROUTER_API_KEY": "your-api-key-here",
        "OPENROUTER_CONFIG": "C:/Users/armin/Documents/GitHub/MCPs/openrouter/config.json",
        "OPENROUTER_MODELS": "C:/Users/armin/Documents/GitHub/MCPs/openrouter/models.json"
      }
    }
  }
}
```

## Usage Example

With an explicit model:

```json
{
  "model": "gemini-flash",
  "messages": [
    { "role": "user", "content": "Explain MCP in one sentence." }
  ],
  "temperature": 0.7
}
```

Without `model` — uses `defaultModel` from `config.json`:

```json
{
  "messages": [
    { "role": "user", "content": "Explain MCP in one sentence." }
  ]
}
```

## Development

```bash
npm run dev    # Run with tsx (stdio transport)
npm run build  # Compile to dist/
npm start      # Run compiled server
```

## License

MIT
