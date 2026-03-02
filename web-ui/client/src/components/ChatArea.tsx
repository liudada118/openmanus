import { Task, Message } from "@/lib/types";
import { ArrowUp, Square, Loader2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { Streamdown } from "streamdown";

interface ChatAreaProps {
  task: Task | null;
  isStreaming: boolean;
  onSendMessage: (content: string) => void;
  onStopStreaming: () => void;
}

const EMPTY_STATE_IMAGE =
  "https://d2xsxph8kpxj0f.cloudfront.net/310519663332343321/fkHWeZyyAtSTiXfYpB2rRt/empty-state-4hr7JQd3xbAX5Wb6xXDa4n.webp";

const SUGGESTIONS = [
  "帮我写一个 Python 爬虫脚本",
  "分析这份数据并生成报告",
  "帮我搜索最新的 AI 技术趋势",
  "写一个自动化脚本处理文件",
];

export default function ChatArea({
  task,
  isStreaming,
  onSendMessage,
  onStopStreaming,
}: ChatAreaProps) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [task?.messages]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  function handleSubmit() {
    const trimmed = input.trim();
    if (!trimmed || isStreaming) return;
    onSendMessage(trimmed);
    setInput("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  // Empty state - no active task
  if (!task) {
    return (
      <div className="flex-1 flex flex-col">
        <div className="flex-1 flex flex-col items-center justify-center px-6">
          <img
            src={EMPTY_STATE_IMAGE}
            alt="OpenManus"
            className="w-16 h-16 mb-6 opacity-60"
          />
          <h2 className="text-xl font-semibold text-foreground mb-2">
            有什么我可以帮您的？
          </h2>
          <p className="text-sm text-muted-foreground mb-8 max-w-md text-center">
            我是您的 AI Agent 助手，可以帮您上网搜索、编写代码、处理数据、生成报告等
          </p>
          <div className="flex flex-wrap gap-2 justify-center max-w-lg">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => onSendMessage(s)}
                className="px-4 py-2 text-sm border border-border rounded-full hover:bg-accent transition-colors text-muted-foreground hover:text-foreground"
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        {/* Input area */}
        <div className="px-4 pb-6 pt-2">
          <div className="max-w-3xl mx-auto">
            <div className="relative flex items-end bg-muted/50 border border-border rounded-2xl px-4 py-3 focus-within:border-primary/30 focus-within:shadow-sm transition-all">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="描述您想要完成的任务..."
                rows={1}
                className="flex-1 bg-transparent resize-none text-sm leading-relaxed outline-none placeholder:text-muted-foreground/60 max-h-[200px]"
              />
              <button
                onClick={handleSubmit}
                disabled={!input.trim()}
                className="ml-2 w-8 h-8 flex items-center justify-center rounded-full bg-foreground text-background disabled:opacity-30 disabled:cursor-not-allowed hover:opacity-80 transition-opacity shrink-0"
              >
                <ArrowUp size={16} strokeWidth={2.5} />
              </button>
            </div>
            <p className="text-[11px] text-muted-foreground/60 text-center mt-2">
              OpenManus Agent · 按 Enter 发送，Shift+Enter 换行
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Active task with messages
  return (
    <div className="flex-1 flex flex-col">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
          {task.messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="px-4 pb-6 pt-2">
        <div className="max-w-3xl mx-auto">
          <div className="relative flex items-end bg-muted/50 border border-border rounded-2xl px-4 py-3 focus-within:border-primary/30 focus-within:shadow-sm transition-all">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isStreaming ? "Agent 正在工作中..." : "继续对话..."}
              rows={1}
              disabled={isStreaming}
              className="flex-1 bg-transparent resize-none text-sm leading-relaxed outline-none placeholder:text-muted-foreground/60 max-h-[200px] disabled:opacity-50"
            />
            {isStreaming ? (
              <button
                onClick={onStopStreaming}
                className="ml-2 w-8 h-8 flex items-center justify-center rounded-full bg-destructive text-destructive-foreground hover:opacity-80 transition-opacity shrink-0"
              >
                <Square size={14} fill="currentColor" />
              </button>
            ) : (
              <button
                onClick={handleSubmit}
                disabled={!input.trim()}
                className="ml-2 w-8 h-8 flex items-center justify-center rounded-full bg-foreground text-background disabled:opacity-30 disabled:cursor-not-allowed hover:opacity-80 transition-opacity shrink-0"
              >
                <ArrowUp size={16} strokeWidth={2.5} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[85%] bg-primary text-primary-foreground px-4 py-2.5 rounded-2xl rounded-br-md">
          <p className="text-sm leading-relaxed whitespace-pre-wrap">
            {message.content}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex gap-3">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center shrink-0 mt-0.5">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <path
            d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
            fill="oklch(0.546 0.215 262)"
          />
        </svg>
      </div>
      <div className="flex-1 min-w-0">
        {message.status === "streaming" || message.status === "pending" ? (
          <div>
            {message.content ? (
              <div className="text-sm leading-relaxed markdown-content">
                <Streamdown>{message.content}</Streamdown>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 size={14} className="animate-spin" />
                <span>思考中...</span>
              </div>
            )}
          </div>
        ) : message.status === "error" ? (
          <div className="text-sm text-destructive bg-destructive/5 px-3 py-2 rounded-lg">
            {message.content || "请求失败，请检查 API 服务是否正常运行"}
          </div>
        ) : (
          <div className="text-sm leading-relaxed markdown-content">
            <Streamdown>{message.content}</Streamdown>
          </div>
        )}
      </div>
    </div>
  );
}
