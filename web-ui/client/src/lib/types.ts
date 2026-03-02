export interface Message {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: number;
  status?: "pending" | "streaming" | "done" | "error";
}

export interface Task {
  id: string;
  title: string;
  messages: Message[];
  createdAt: number;
  updatedAt: number;
  model: string;
}

export interface ModelConfig {
  id: string;
  name: string;
  provider: "openai" | "ollama" | "custom";
  description: string;
  costPerTask?: string;
}

export const MODELS: ModelConfig[] = [
  {
    id: "gpt-4.1-mini",
    name: "GPT-4.1 Mini",
    provider: "openai",
    description: "日常任务，性价比最高",
    costPerTask: "¥0.14/次",
  },
  {
    id: "gpt-4.1",
    name: "GPT-4.1",
    provider: "openai",
    description: "强大的通用模型",
    costPerTask: "¥0.42/次",
  },
  {
    id: "gpt-5-mini",
    name: "GPT-5 Mini",
    provider: "openai",
    description: "更强推理能力",
    costPerTask: "¥0.25/次",
  },
  {
    id: "gpt-5.2",
    name: "GPT-5.2",
    provider: "openai",
    description: "最强 Agent 模型",
    costPerTask: "¥0.86/次",
  },
  {
    id: "qwen3:14b",
    name: "Qwen3 14B",
    provider: "ollama",
    description: "本地免费，需 12GB 显存",
    costPerTask: "免费",
  },
  {
    id: "qwen3:8b",
    name: "Qwen3 8B",
    provider: "ollama",
    description: "本地免费，轻量快速",
    costPerTask: "免费",
  },
  {
    id: "deepseek-r1:14b",
    name: "DeepSeek R1 14B",
    provider: "ollama",
    description: "本地免费，深度推理",
    costPerTask: "免费",
  },
];

export const DEFAULT_MODEL = "gpt-4.1-mini";
