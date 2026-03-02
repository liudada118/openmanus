// OpenManus-GUI api_server.py 兼容的 OpenAI 格式 API 客户端
// 后端只提供 POST /v1/chat/completions 一个端点
// 健康检查使用 /openapi.json（FastAPI 自动生成）
// 模型列表为前端静态配置

const SETTINGS_KEY = "openmanus_settings";

interface Settings {
  backendHost: string;
  backendPort: number;
}

const DEFAULT_SETTINGS: Settings = {
  backendHost: "localhost",
  backendPort: 8000,
};

export function getSettings(): Settings {
  try {
    const raw = localStorage.getItem(SETTINGS_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return { ...DEFAULT_SETTINGS, ...parsed };
    }
  } catch {
    // ignore
  }
  return DEFAULT_SETTINGS;
}

export function saveSettings(settings: Settings) {
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}

function getApiBase(): string {
  const settings = getSettings();
  // 开发环境通过 Vite 代理，避免 CORS
  if (import.meta.env.DEV) {
    return "/api";
  }
  // 生产环境直连后端
  return `http://${settings.backendHost}:${settings.backendPort}`;
}

interface ChatCompletionRequest {
  model: string;
  messages: { role: string; content: string }[];
  stream?: boolean;
}

export async function sendChatMessage(
  request: ChatCompletionRequest,
  onChunk?: (text: string) => void,
  signal?: AbortSignal
): Promise<string> {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/v1/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...request, stream: true }),
    signal,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API 请求失败 (${response.status}): ${errorText}`);
  }

  if (!response.body) {
    throw new Error("响应体为空");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let fullText = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    const lines = chunk.split("\n").filter((line) => line.trim());

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") continue;

        try {
          const parsed = JSON.parse(data);
          const content = parsed.choices?.[0]?.delta?.content;
          if (content) {
            fullText += content;
            onChunk?.(fullText);
          }
        } catch {
          // skip non-JSON lines
        }
      }
    }
  }

  return fullText;
}

// 非流式请求（备用）
export async function sendChatMessageSync(
  request: ChatCompletionRequest
): Promise<string> {
  const apiBase = getApiBase();
  const response = await fetch(`${apiBase}/v1/chat/completions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...request, stream: false }),
  });

  if (!response.ok) {
    throw new Error(`API 请求失败 (${response.status})`);
  }

  const data = await response.json();
  return data.choices?.[0]?.message?.content || "";
}

// 健康检查 - 使用 /openapi.json（FastAPI 自动提供）
export async function checkApiHealth(): Promise<boolean> {
  try {
    const apiBase = getApiBase();
    const response = await fetch(`${apiBase}/openapi.json`, {
      method: "GET",
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
}
