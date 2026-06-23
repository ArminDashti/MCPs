import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

function formatCsvFileName(date: Date): string {
  const pad = (value: number) => String(value).padStart(2, "0");
  const monthDay = `${pad(date.getMonth() + 1)}${pad(date.getDate())}`;
  const time = `${pad(date.getHours())}${pad(date.getMinutes())}${pad(date.getSeconds())}`;
  return `${monthDay}-${time}.csv`;
}

function escapeCsvValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "";
  }

  let text: string;
  if (value instanceof Date) {
    text = value.toISOString();
  } else if (typeof value === "object") {
    text = JSON.stringify(value);
  } else {
    text = String(value);
  }

  if (/[",\n\r]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

export async function writeRowsToCsv(
  csvDir: string,
  rows: Record<string, unknown>[],
  explicitPath?: string
): Promise<string> {
  await mkdir(csvDir, { recursive: true });

  const filePath =
    explicitPath?.trim() || join(csvDir, formatCsvFileName(new Date()));

  if (rows.length === 0) {
    await writeFile(filePath, "", "utf-8");
    return filePath;
  }

  const headers = Object.keys(rows[0]!);
  const lines = [
    headers.map(escapeCsvValue).join(","),
    ...rows.map((row) =>
      headers.map((header) => escapeCsvValue(row[header])).join(",")
    ),
  ];

  await writeFile(filePath, `${lines.join("\n")}\n`, "utf-8");
  return filePath;
}
