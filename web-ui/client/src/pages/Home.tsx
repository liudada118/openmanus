/*
 * Design: Manus 极简白 (Swiss Design / Minimalist White)
 * - 纯白背景 + 极浅灰侧边栏
 * - 三栏布局：左侧任务列表 + 中间对话区
 * - 极简导航栏：logo + 模型选择器 + 状态指示
 * - 底部居中圆角输入框 + 圆形发送按钮
 */

import { useState, useCallback, useRef } from "react";
import Sidebar from "@/components/Sidebar";
import ChatArea from "@/components/ChatArea";
import ModelSelector from "@/components/ModelSelector";
import StatusIndicator from "@/components/StatusIndicator";
import { useTaskStore } from "@/hooks/useTaskStore";
import { sendChatMessage } from "@/lib/api";

export default function Home() {
  const {
    tasks,
    activeTask,
    activeTaskId,
    currentModel,
    setCurrentModel,
    setActiveTaskId,
    createTask,
    addMessage,
    updateMessage,
    deleteTask,
  } = useTaskStore();

  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const handleSendMessage = useCallback(
    async (content: string) => {
      let taskId = activeTaskId;
      let task = activeTask;

      // Create new task if none active
      if (!taskId) {
        task = createTask(content);
        taskId = task.id;
      } else {
        addMessage(taskId, { role: "user", content, status: "done" });
      }

      // Add assistant placeholder
      const assistantMsg = addMessage(taskId, {
        role: "assistant",
        content: "",
        status: "pending",
      });

      setIsStreaming(true);
      const controller = new AbortController();
      abortRef.current = controller;

      try {
        // Build message history
        const currentTask = task || activeTask;
        const history = (currentTask?.messages || [])
          .filter((m) => m.status === "done")
          .map((m) => ({ role: m.role, content: m.content }));

        // Add the new user message if task was existing
        if (activeTaskId) {
          history.push({ role: "user", content });
        }

        const fullText = await sendChatMessage(
          {
            model: currentModel,
            messages: history,
            stream: true,
          },
          (text) => {
            updateMessage(taskId!, assistantMsg.id, {
              content: text,
              status: "streaming",
            });
          },
          controller.signal
        );

        updateMessage(taskId!, assistantMsg.id, {
          content: fullText,
          status: "done",
        });
      } catch (err: any) {
        if (err.name === "AbortError") {
          updateMessage(taskId!, assistantMsg.id, {
            status: "done",
          });
        } else {
          updateMessage(taskId!, assistantMsg.id, {
            content: `错误：${err.message || "请求失败"}。请确保 OpenManus-GUI 的 API 服务 (api_server.py) 已启动。`,
            status: "error",
          });
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [
      activeTaskId,
      activeTask,
      currentModel,
      createTask,
      addMessage,
      updateMessage,
    ]
  );

  const handleStopStreaming = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  const handleCreateTask = useCallback(() => {
    setActiveTaskId(null);
  }, [setActiveTaskId]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Top Navigation Bar */}
      <header className="h-14 border-b border-border flex items-center justify-between px-4 bg-background shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-primary/70 flex items-center justify-center">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"
                  fill="white"
                />
              </svg>
            </div>
            <span className="font-semibold text-base tracking-tight">
              OpenManus
            </span>
          </div>
          <div className="w-px h-5 bg-border" />
          <ModelSelector
            currentModel={currentModel}
            onModelChange={setCurrentModel}
          />
        </div>

        <div className="flex items-center gap-4">
          <StatusIndicator />
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          tasks={tasks}
          activeTaskId={activeTaskId}
          onSelectTask={setActiveTaskId}
          onCreateTask={handleCreateTask}
          onDeleteTask={deleteTask}
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        <main className="flex-1 flex flex-col overflow-hidden">
          <ChatArea
            task={activeTask}
            isStreaming={isStreaming}
            onSendMessage={handleSendMessage}
            onStopStreaming={handleStopStreaming}
          />
        </main>
      </div>
    </div>
  );
}
