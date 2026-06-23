import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { SqlServerClient } from "../client.js";
import type { SqlServerConfig } from "../config.js";
import { writeQueryLog } from "../logger.js";
import { buildSelectQuery } from "../sql/builder.js";
import { writeRowsToCsv } from "../sql/csv.js";

const orderBySchema = z.object({
  column: z.string().describe("Column name to sort by"),
  direction: z
    .enum(["ASC", "DESC"])
    .optional()
    .describe("Sort direction (default ASC)"),
});

const queryInputSchema = z.object({
  table: z.string().describe("Table name (schema.table or table)"),
  select: z
    .array(z.string())
    .optional()
    .describe('Columns to return (default ["*"]). Use "*" for all columns.'),
  where: z
    .string()
    .optional()
    .describe("WHERE clause body without the WHERE keyword"),
  row_limit: z
    .number()
    .int()
    .positive()
    .optional()
    .describe("Maximum number of rows to return (SQL Server TOP)"),
  group_by: z
    .array(z.string())
    .optional()
    .describe("Columns to group by"),
  order_by: z
    .array(orderBySchema)
    .optional()
    .describe("Sort order for results"),
  count: z
    .boolean()
    .optional()
    .describe(
      "When true, returns COUNT(*) instead of row data. With group_by, returns counts per group."
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

type QueryInput = z.infer<typeof queryInputSchema>;

function toolError(message: string) {
  return {
    content: [{ type: "text" as const, text: message }],
    isError: true,
  };
}

async function executeAndRespond(
  client: SqlServerClient,
  config: SqlServerConfig,
  tool: string,
  input: QueryInput | Record<string, unknown>,
  sql: string,
  storeOnDiskAsCsv?: boolean,
  csvPath?: string
) {
  try {
    const rows = await client.query(sql);
    let writtenCsvPath: string | undefined;

    if (storeOnDiskAsCsv) {
      writtenCsvPath = await writeRowsToCsv(config.csvDir, rows, csvPath);
    }

    const logFile = await writeQueryLog(config.logsDir, {
      tool,
      input: input as Record<string, unknown>,
      sql,
      rowCount: rows.length,
      csvPath: writtenCsvPath,
    });

    const result: Record<string, unknown> = {
      sql,
      row_count: rows.length,
      rows,
      log_file: logFile,
    };

    if (writtenCsvPath) {
      result.csv_path = writtenCsvPath;
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
      tool,
      input: input as Record<string, unknown>,
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

export function registerQueryTool(
  server: McpServer,
  client: SqlServerClient,
  config: SqlServerConfig
): void {
  server.registerTool(
    "query",
    {
      title: "SQL Server Structured Query",
      description:
        "Run a SELECT against SQL Server using structured parameters: select, where, row_limit, group_by, order_by, count, and optional CSV export.",
      inputSchema: queryInputSchema,
    },
    async (input) => {
      let sql: string;
      try {
        sql = buildSelectQuery({
          table: input.table,
          select: input.select,
          where: input.where,
          rowLimit: input.row_limit,
          groupBy: input.group_by,
          orderBy: input.order_by,
          count: input.count,
        });
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        const logFile = await writeQueryLog(config.logsDir, {
          tool: "query",
          input,
          sql: "",
          error: message,
        });
        return toolError(
          JSON.stringify({ error: message, log_file: logFile }, null, 2)
        );
      }

      return executeAndRespond(
        client,
        config,
        "query",
        input,
        sql,
        input.store_on_disk_as_csv,
        input.csv_path
      );
    }
  );
}
