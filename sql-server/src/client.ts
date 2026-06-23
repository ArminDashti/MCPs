import sql from "mssql";
import type { SqlServerConfig } from "./config.js";

export class SqlServerClient {
  private pool: sql.ConnectionPool | null = null;
  private readonly config: SqlServerConfig;

  constructor(config: SqlServerConfig) {
    this.config = config;
  }

  private getConnectionConfig(): sql.config {
    return {
      server: this.config.server,
      port: this.config.port,
      database: this.config.database,
      user: this.config.username,
      password: this.config.password,
      options: {
        encrypt: this.config.encrypt,
        trustServerCertificate: this.config.trustServerCertificate,
      },
    };
  }

  async connect(): Promise<void> {
    if (this.pool?.connected) {
      return;
    }

    this.pool = await new sql.ConnectionPool(this.getConnectionConfig()).connect();
  }

  async query<T extends Record<string, unknown> = Record<string, unknown>>(
    queryText: string,
    parameters?: Record<string, unknown>
  ): Promise<T[]> {
    await this.connect();
    const request = this.pool!.request();

    if (parameters) {
      for (const [name, value] of Object.entries(parameters)) {
        request.input(name, value);
      }
    }

    const result = await request.query<T>(queryText);
    return result.recordset ?? [];
  }

  async close(): Promise<void> {
    if (this.pool) {
      await this.pool.close();
      this.pool = null;
    }
  }
}
