import type { OpenRouterConfig } from "./config.js";

export interface ChatMessage {
  role: "system" | "user" | "assistant" | "tool";
  content: string | unknown;
  name?: string;
  tool_call_id?: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  max_tokens?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
  stop?: string | string[];
  response_format?: { type: "text" | "json_object" };
  models?: string[];
  provider?: Record<string, unknown>;
}

export interface ChatCompletionResponse {
  id: string;
  model: string;
  choices: Array<{
    index: number;
    message: {
      role: string;
      content: string | null;
      tool_calls?: unknown[];
    };
    finish_reason: string | null;
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

export class OpenRouterClient {
  constructor(private readonly config: OpenRouterConfig) {}

  private headers(): Record<string, string> {
    const headers: Record<string, string> = {
      Authorization: `Bearer ${this.config.apiKey}`,
      "Content-Type": "application/json",
    };

    if (this.config.httpReferer) {
      headers["HTTP-Referer"] = this.config.httpReferer;
    }

    if (this.config.appTitle) {
      headers["X-OpenRouter-Title"] = this.config.appTitle;
    }

    return headers;
  }

  private async request<T>(
    path: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.config.baseUrl}${path}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.headers(),
        ...(options.headers as Record<string, string> | undefined),
      },
    });

    if (!response.ok) {
      const body = await response.text();
      let message = `OpenRouter API error (${response.status})`;
      try {
        const parsed = JSON.parse(body) as { error?: { message?: string } };
        if (parsed.error?.message) {
          message = parsed.error.message;
        }
      } catch {
        if (body) {
          message = body;
        }
      }
      throw new Error(message);
    }

    return (await response.json()) as T;
  }

  async chatCompletion(
    request: ChatCompletionRequest
  ): Promise<ChatCompletionResponse> {
    return this.request<ChatCompletionResponse>("/chat/completions", {
      method: "POST",
      body: JSON.stringify(request),
    });
  }
}
