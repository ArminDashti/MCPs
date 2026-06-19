import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

function formatTimestamp(date: Date): string {
  const pad = (value: number) => String(value).padStart(2, "0");
  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
    pad(date.getHours()),
    pad(date.getMinutes()),
    pad(date.getSeconds()),
  ].join("-");
}

function extractUserPrompt(
  messages: Array<{ role: string; content: string }>
): string {
  return messages
    .filter((message) => message.role === "user")
    .map((message) => message.content)
    .join("\n\n");
}

export async function writeRequestLog(
  logsDir: string,
  model: string,
  messages: Array<{ role: string; content: string }>,
  response: string
): Promise<string> {
  await mkdir(logsDir, { recursive: true });

  const timestamp = formatTimestamp(new Date());
  const fileName = `${timestamp}.log`;
  const filePath = join(logsDir, fileName);

  const userPrompt = extractUserPrompt(messages);
  const content = [
    model,
    "",
    "--------------------------------------------------------------------",
    userPrompt,
    "",
    "--------------------------------------------------------------------",
    response,
    "",
  ].join("\n");

  await writeFile(filePath, content, "utf-8");
  return filePath;
}
