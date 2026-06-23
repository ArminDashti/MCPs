import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { resolve } from "node:path";

export interface SqlServerConfig {
  server: string;
  port: number;
  database: string;
  username: string;
  password: string;
  trustServerCertificate: boolean;
  encrypt: boolean;
  logsDir: string;
  csvDir: string;
}

interface ConfigFile {
  server?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  trustServerCertificate?: boolean;
  encrypt?: boolean;
  logsDir?: string;
  csvDir?: string;
}

function expandHomePath(path: string): string {
  if (path.startsWith("~/")) {
    return resolve(homedir(), path.slice(2));
  }
  if (path === "~") {
    return homedir();
  }
  return resolve(path);
}

function requireNonEmpty(value: string | undefined, label: string): string {
  const trimmed = value?.trim();
  if (!trimmed) {
    throw new Error(`${label} is required.`);
  }
  return trimmed;
}

function loadConfigFile(): ConfigFile {
  const configPath =
    process.env.SQL_SERVER_CONFIG ?? resolve(process.cwd(), "config.json");

  try {
    const raw = readFileSync(configPath, "utf-8");
    return JSON.parse(raw) as ConfigFile;
  } catch (error) {
    const hasEnvCredentials =
      process.env.SQL_SERVER &&
      process.env.SQL_DATABASE &&
      process.env.SQL_USERNAME &&
      process.env.SQL_PASSWORD;

    if (hasEnvCredentials) {
      return {};
    }

    const message = error instanceof Error ? error.message : "Unknown error";
    throw new Error(
      `Failed to load config from ${configPath}: ${message}. ` +
        "Set SQL_SERVER_CONFIG to your config file path, or provide SQL_SERVER, SQL_DATABASE, SQL_USERNAME, and SQL_PASSWORD environment variables."
    );
  }
}

export function loadConfig(): SqlServerConfig {
  const fileConfig = loadConfigFile();

  const server = requireNonEmpty(
    process.env.SQL_SERVER ?? fileConfig.server,
    "server (SQL_SERVER)"
  );
  const database = requireNonEmpty(
    process.env.SQL_DATABASE ?? fileConfig.database,
    "database (SQL_DATABASE)"
  );
  const username = requireNonEmpty(
    process.env.SQL_USERNAME ?? fileConfig.username,
    "username (SQL_USERNAME)"
  );
  const password = requireNonEmpty(
    process.env.SQL_PASSWORD ?? fileConfig.password,
    "password (SQL_PASSWORD)"
  );

  const port = Number(process.env.SQL_PORT ?? fileConfig.port ?? 1433);
  if (!Number.isInteger(port) || port <= 0) {
    throw new Error("port (SQL_PORT) must be a positive integer.");
  }

  const trustServerCertificate =
    process.env.SQL_TRUST_SERVER_CERTIFICATE !== undefined
      ? process.env.SQL_TRUST_SERVER_CERTIFICATE === "true"
      : (fileConfig.trustServerCertificate ?? true);

  const encrypt =
    process.env.SQL_ENCRYPT !== undefined
      ? process.env.SQL_ENCRYPT === "true"
      : (fileConfig.encrypt ?? true);

  const logsDir = expandHomePath(
    process.env.SQL_LOGS_DIR ?? fileConfig.logsDir ?? "~/sql-server-mcp"
  );
  const csvDir = expandHomePath(
    process.env.SQL_CSV_DIR ?? fileConfig.csvDir ?? "~/sql-server-mcp/csv"
  );

  return {
    server,
    port,
    database,
    username,
    password,
    trustServerCertificate,
    encrypt,
    logsDir,
    csvDir,
  };
}
