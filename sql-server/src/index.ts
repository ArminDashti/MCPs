#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { SqlServerClient } from "./client.js";
import { loadConfig } from "./config.js";
import { registerQueryTool } from "./tools/query.js";
import { registerRawQueryTool } from "./tools/raw-query.js";

async function main(): Promise<void> {
  const config = loadConfig();
  const client = new SqlServerClient(config);

  const server = new McpServer({
    name: "sql-server",
    version: "1.0.0",
  });

  registerQueryTool(server, client, config);
  registerRawQueryTool(server, client, config);

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Fatal error in sql-server-mcp: ${message}`);
  process.exit(1);
});
