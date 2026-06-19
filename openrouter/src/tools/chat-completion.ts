import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import type { OpenRouterClient } from "../client.js";
import {
  getModelNames,
  resolveModelId,
  type OpenRouterConfig,
} from "../config.js";
import { writeRequestLog } from "../logger.js";

const messageSchema = z.object({
  role: z
    .enum(["system", "user", "assistant", "tool"])
    .describe("Message role"),
  content: z
    .string()
    .describe("Message content (plain text or JSON string for multimodal)"),
  name: z.string().optional().describe("Optional name for the message author"),
  tool_call_id: z
    .string()
    .optional()
    .describe("Required when role is tool — ID of the tool call being answered"),
});

function createChatCompletionSchema(modelNames: string[], defaultModel: string) {
  return z.object({
    model: z
      .enum(modelNames as [string, ...string[]])
      .optional()
      .describe(
        `Model name from the allowed models file. Defaults to "${defaultModel}" when omitted. Allowed: ${modelNames.join(", ")}`
      ),
    messages: z
      .array(messageSchema)
      .min(1)
      .describe("Conversation messages in OpenAI chat format"),
    temperature: z
      .number()
      .min(0)
      .max(2)
      .optional()
      .describe("Sampling temperature (0-2, default model-specific)"),
    max_tokens: z
      .number()
      .int()
      .positive()
      .optional()
      .describe("Maximum tokens to generate"),
    top_p: z
      .number()
      .min(0)
      .max(1)
      .optional()
      .describe("Nucleus sampling parameter"),
    frequency_penalty: z
      .number()
      .min(-2)
      .max(2)
      .optional()
      .describe("Frequency penalty (-2 to 2)"),
    presence_penalty: z
      .number()
      .min(-2)
      .max(2)
      .optional()
      .describe("Presence penalty (-2 to 2)"),
    stop: z
      .union([z.string(), z.array(z.string())])
      .optional()
      .describe("Stop sequences"),
    json_mode: z
      .boolean()
      .optional()
      .describe("Request JSON object response format when supported"),
    fallback_models: z
      .array(z.string())
      .optional()
      .describe(
        "Fallback model names if the primary model is unavailable (OpenRouter routing)"
      ),
  });
}

export function registerChatCompletionTool(
  server: McpServer,
  client: OpenRouterClient,
  config: OpenRouterConfig
): void {
  const modelNames = getModelNames(config);
  const chatCompletionSchema = createChatCompletionSchema(
    modelNames,
    config.defaultModel
  );

  server.registerTool(
    "chat_completion",
    {
      title: "OpenRouter Chat Completion",
      description: `Send a chat completion request to an OpenRouter model. Default model: ${config.defaultModel}. Allowed: ${modelNames.join(", ")}`,
      inputSchema: chatCompletionSchema,
    },
    async ({
      model,
      messages,
      temperature,
      max_tokens,
      top_p,
      frequency_penalty,
      presence_penalty,
      stop,
      json_mode,
      fallback_models,
    }) => {
      const modelName = model ?? config.defaultModel;
      const modelId = resolveModelId(config, modelName);
      if (!modelId) {
        return {
          content: [
            {
              type: "text" as const,
              text: `Unknown model name "${modelName}". Allowed: ${modelNames.join(", ")}`,
            },
          ],
          isError: true,
        };
      }

      let fallbackIds: string[] | undefined;
      if (fallback_models) {
        fallbackIds = [];
        for (const name of fallback_models) {
          const id = resolveModelId(config, name);
          if (!id) {
            return {
              content: [
                {
                  type: "text" as const,
                  text: `Unknown fallback model name "${name}". Allowed: ${modelNames.join(", ")}`,
                },
              ],
              isError: true,
            };
          }
          fallbackIds.push(id);
        }
      }

      const response = await client.chatCompletion({
        model: modelId,
        messages,
        temperature,
        max_tokens,
        top_p,
        frequency_penalty,
        presence_penalty,
        stop,
        models: fallbackIds,
        response_format: json_mode ? { type: "json_object" } : undefined,
      });

      const choice = response.choices[0];
      const content = choice?.message?.content ?? "";
      const result: Record<string, unknown> = {
        id: response.id,
        model_name: modelName,
        model: response.model,
        content,
        finish_reason: choice?.finish_reason,
        usage: response.usage,
      };

      if (config.logsDir) {
        result.log_file = await writeRequestLog(
          config.logsDir,
          modelId,
          messages,
          content
        );
      }

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }
  );
}
