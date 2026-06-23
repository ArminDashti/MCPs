import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { SqlServerClient } from "../client.js";
import type { SqlServerConfig } from "../config.js";
import { writeQueryLog } from "../logger.js";
import { writeRowsToCsv } from "../sql/csv.js";

const rawQueryInputSchema = z.object({
  sql: z.string().min(1).describe("Raw SQL to execute"),
  parameters: z
    .record(z.unknown())
    .optional()
    .describe(
      "Optional named parameters for the query (use @name in SQL, e.g. WHERE id = @id)"
    ),
  store_on_disk_as_csv: z
    .boolean()
    .optional()
    .describe("When true, writes the result set to a CSV file on disk"),
  csv_path: z
    .string()
    .optional()
    .describe(
      "Optional absolute path for the CSV file. Defaults to csvDir with a timestamped name."
    ),
});

function toolError(message: string) {
  return {
    content: [{ type: "text" as const, text: message }],
    isError: true,
  };
}

export function registerRawQueryTool(
  server: McpServer,
  client: SqlServerClient,
  config: SqlServerConfig
): void {
  server.registerTool(
    "raw_query",
    {
      title: "SQL Server Raw Query",
      description:
        "Execute any SQL statement the agent needs against SQL Server, with optional named parameters and CSV export.",
      inputSchema: rawQueryInputSchema,
    },
    async (input) => {
      const sql = input.sql.trim();
      if (!sql) {
        const logFile = await writeQueryLog(config.logsDir, {
          tool: "raw_query",
          input,
          sql: "",
          error: "SQL must not be empty.",
        });
        return toolError(
          JSON.stringify(
            { error: "SQL must not be empty.", log_file: logFile },
            null,
            2
          )
        );
      }

      try {
        const rows = await client.query(sql, input.parameters);
        let csvPath: string | undefined;

        if (input.store_on_disk_as_csv) {
          csvPath = await writeRowsToCsv(config.csvDir, rows, input.csv_path);
        }

        const logFile = await writeQueryLog(config.logsDir, {
          tool: "raw_query",
          input,
          sql,
          rowCount: rows.length,
          csvPath,
        });

        const result: Record<string, unknown> = {
          sql,
          row_count: rows.length,
          rows,
          log_file: logFile,
        };

        if (csvPath) {
          result.csv_path = csvPath;
        }

        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        const logFile = await writeQueryLog(config.logsDir, {
          tool: "raw_query",
          input,
          sql,
          error: message,
        });

        return toolError(
          JSON.stringify(
            {
              error: message,
              sql,
              log_file: logFile,
            },
            null,
            2
          )
        );
      }
    }
  );
}
