// OpenManus-GUI api_server.py 兼容的 OpenAI 格式 API 客户端
// 默认连接 http://localhost:8000（OpenManus-GUI 的 api_server.py）

const API_BASE = "http://localhost:8000";

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
  const response = await fetch(`${API_BASE}/v1/chat/completions`, {
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
  const response = await fetch(`${API_BASE}/v1/chat/completions`, {
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

// 健康检查
export async function checkApiHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/v1/models`, {
      method: "GET",
      signal: AbortSignal.timeout(3000),
    });
    return response.ok;
  } catch {
    return false;
  }
}
