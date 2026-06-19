import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

export interface OpenRouterConfig {
  apiKey: string;
  baseUrl: string;
  httpReferer?: string;
  appTitle?: string;
  models: Record<string, string>;
  defaultModel: string;
  logsDir?: string;
}

interface ConfigFile {
  modelsFile?: string;
  defaultModel?: string;
  logsDir?: string;
}

function loadModelsFile(modelsPath: string): Record<string, string> {
  let raw: string;
  try {
    raw = readFileSync(modelsPath, "utf-8");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    throw new Error(`Failed to load models from ${modelsPath}: ${message}`);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new Error(`Models file at ${modelsPath} must be valid JSON.`);
  }

  if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
    throw new Error(
      `Models file at ${modelsPath} must be a JSON object mapping model names to OpenRouter IDs.`
    );
  }

  const models: Record<string, string> = {};
  for (const [name, id] of Object.entries(parsed)) {
    if (typeof name !== "string" || name.trim() === "") {
      throw new Error(`Invalid model name in ${modelsPath}.`);
    }
    if (typeof id !== "string" || id.trim() === "") {
      throw new Error(
        `Model "${name}" in ${modelsPath} must map to a non-empty OpenRouter model ID.`
      );
    }
    models[name.trim()] = id.trim();
  }

  if (Object.keys(models).length === 0) {
    throw new Error(`Models file at ${modelsPath} must define at least one model.`);
  }

  return models;
}

export function getModelNames(config: OpenRouterConfig): string[] {
  return Object.keys(config.models);
}

export function resolveModelId(
  config: OpenRouterConfig,
  modelName: string
): string | undefined {
  return config.models[modelName];
}

export function loadConfig(): OpenRouterConfig {
  const apiKey = process.env.OPENROUTER_API_KEY;
  if (!apiKey) {
    throw new Error(
      "OPENROUTER_API_KEY environment variable is required. Get a key at https://openrouter.ai/settings/keys"
    );
  }

  const configPath =
    process.env.OPENROUTER_CONFIG ?? resolve(process.cwd(), "config.json");

  let fileConfig: ConfigFile = {};
  try {
    const raw = readFileSync(configPath, "utf-8");
    fileConfig = JSON.parse(raw) as ConfigFile;
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    throw new Error(
      `Failed to load config from ${configPath}: ${message}. ` +
        "Set OPENROUTER_CONFIG to your config file path."
    );
  }

  const configDir = dirname(configPath);
  const modelsPath = process.env.OPENROUTER_MODELS
    ? resolve(process.env.OPENROUTER_MODELS)
    : fileConfig.modelsFile
      ? resolve(configDir, fileConfig.modelsFile)
      : resolve(configDir, "models.json");

  const models = loadModelsFile(modelsPath);

  const defaultModel = fileConfig.defaultModel?.trim();
  if (!defaultModel) {
    throw new Error(
      `Config at ${configPath} must define "defaultModel" — the model name to use when the agent omits model.`
    );
  }
  if (!models[defaultModel]) {
    throw new Error(
      `defaultModel "${defaultModel}" in ${configPath} is not defined in ${modelsPath}.`
    );
  }

  return {
    apiKey,
    baseUrl: process.env.OPENROUTER_BASE_URL ?? "https://openrouter.ai/api/v1",
    httpReferer: process.env.OPENROUTER_HTTP_REFERER,
    appTitle: process.env.OPENROUTER_APP_TITLE ?? "openrouter-mcp",
    models,
    defaultModel,
    logsDir: fileConfig.logsDir?.trim() || undefined,
  };
}
