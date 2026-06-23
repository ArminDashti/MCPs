import { appendFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

function formatLogFileName(date: Date): string {
  const pad = (value: number) => String(value).padStart(2, "0");
  const monthDay = `${pad(date.getMonth() + 1)}${pad(date.getDate())}`;
  const time = `${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;
  return `${monthDay}-${time}.log`;
}

function formatIsoTimestamp(date: Date): string {
  return date.toISOString();
}

export interface QueryLogEntry {
  tool: string;
  input: Record<string, unknown>;
  sql: string;
  rowCount?: number;
  error?: string;
  csvPath?: string;
}

export async function writeQueryLog(
  logsDir: string,
  entry: QueryLogEntry
): Promise<string> {
  await mkdir(logsDir, { recursive: true });

  const now = new Date();
  const fileName = formatLogFileName(now);
  const filePath = join(logsDir, fileName);

  const lines = [
    `timestamp: ${formatIsoTimestamp(now)}`,
    `tool: ${entry.tool}`,
    "",
    "input:",
    JSON.stringify(entry.input, null, 2),
    "",
    "sql:",
    entry.sql,
    "",
  ];

  if (entry.rowCount !== undefined) {
    lines.push(`row_count: ${entry.rowCount}`, "");
  }
  if (entry.csvPath) {
    lines.push(`csv_path: ${entry.csvPath}`, "");
  }
  if (entry.error) {
    lines.push(`error: ${entry.error}`, "");
  }

  await appendFile(filePath, `${lines.join("\n")}\n`, "utf-8");
  return filePath;
}
