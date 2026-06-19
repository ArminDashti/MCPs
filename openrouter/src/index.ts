#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { OpenRouterClient } from "./client.js";
import { loadConfig } from "./config.js";
import { registerChatCompletionTool } from "./tools/chat-completion.js";

async function main(): Promise<void> {
  const config = loadConfig();
  const client = new OpenRouterClient(config);

  const server = new McpServer({
    name: "openrouter",
    version: "1.0.0",
  });

  registerChatCompletionTool(server, client, config);

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Fatal error in openrouter-mcp: ${message}`);
  process.exit(1);
});
