const IDENTIFIER_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;

export interface OrderByClause {
  column: string;
  direction?: "ASC" | "DESC";
}

export interface BuildQueryParams {
  table: string;
  select?: string[];
  where?: string;
  rowLimit?: number;
  groupBy?: string[];
  orderBy?: OrderByClause[];
  count?: boolean;
}

function assertIdentifier(name: string, label: string): void {
  if (!IDENTIFIER_PATTERN.test(name)) {
    throw new Error(
      `Invalid ${label} "${name}". Only letters, numbers, and underscores are allowed.`
    );
  }
}

function quoteIdentifier(name: string): string {
  assertIdentifier(name, "identifier");
  return `[${name.replace(/]/g, "]]")}]`;
}

export function formatTableName(table: string): string {
  const parts = table.split(".");
  if (parts.length === 0 || parts.length > 2) {
    throw new Error(
      `Invalid table "${table}". Use "table" or "schema.table".`
    );
  }
  return parts.map((part) => quoteIdentifier(part)).join(".");
}

export function buildSelectQuery(params: BuildQueryParams): string {
  const table = formatTableName(params.table);

  if (params.select) {
    for (const column of params.select) {
      if (column !== "*") {
        assertIdentifier(column, "select column");
      }
    }
  }

  if (params.groupBy) {
    for (const column of params.groupBy) {
      assertIdentifier(column, "group by column");
    }
  }

  if (params.orderBy) {
    for (const clause of params.orderBy) {
      assertIdentifier(clause.column, "order by column");
      if (clause.direction && !["ASC", "DESC"].includes(clause.direction)) {
        throw new Error(
          `Invalid order direction "${clause.direction}" for column "${clause.column}".`
        );
      }
    }
  }

  if (params.rowLimit !== undefined) {
    if (!Number.isInteger(params.rowLimit) || params.rowLimit <= 0) {
      throw new Error("row_limit must be a positive integer.");
    }
  }

  const hasGroupBy = Boolean(params.groupBy?.length);

  if (params.count && !hasGroupBy) {
    let sql = `SELECT COUNT(*) AS [count] FROM ${table}`;
    if (params.where?.trim()) {
      sql += ` WHERE ${params.where.trim()}`;
    }
    return sql;
  }

  let columns: string;
  if (params.count && hasGroupBy) {
    columns = `${params.groupBy!.map(quoteIdentifier).join(", ")}, COUNT(*) AS [count]`;
  } else if (params.select?.length) {
    columns = params.select
      .map((column) => (column === "*" ? "*" : quoteIdentifier(column)))
      .join(", ");
  } else {
    columns = "*";
  }

  const topClause =
    params.rowLimit !== undefined ? `TOP (${params.rowLimit}) ` : "";
  let sql = `SELECT ${topClause}${columns} FROM ${table}`;

  if (params.where?.trim()) {
    sql += ` WHERE ${params.where.trim()}`;
  }

  if (hasGroupBy) {
    sql += ` GROUP BY ${params.groupBy!.map(quoteIdentifier).join(", ")}`;
  }

  if (params.orderBy?.length) {
    const orderClause = params.orderBy
      .map(
        (clause) =>
          `${quoteIdentifier(clause.column)} ${clause.direction ?? "ASC"}`
      )
      .join(", ");
    sql += ` ORDER BY ${orderClause}`;
  }

  return sql;
}
