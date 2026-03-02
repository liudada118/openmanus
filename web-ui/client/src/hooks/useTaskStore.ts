import { useState, useCallback, useEffect } from "react";
import { Task, Message, DEFAULT_MODEL } from "@/lib/types";
import { nanoid } from "nanoid";

const STORAGE_KEY = "openmanus_tasks";
const MODEL_KEY = "openmanus_model";

function loadTasks(): Task[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveTasks(tasks: Task[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

export function useTaskStore() {
  const [tasks, setTasks] = useState<Task[]>(loadTasks);
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [currentModel, setCurrentModel] = useState<string>(
    () => localStorage.getItem(MODEL_KEY) || DEFAULT_MODEL
  );

  useEffect(() => {
    saveTasks(tasks);
  }, [tasks]);

  useEffect(() => {
    localStorage.setItem(MODEL_KEY, currentModel);
  }, [currentModel]);

  const activeTask = tasks.find((t) => t.id === activeTaskId) || null;

  const createTask = useCallback(
    (firstMessage?: string) => {
      const id = nanoid();
      const title = firstMessage
        ? firstMessage.slice(0, 40) + (firstMessage.length > 40 ? "..." : "")
        : "新任务";
      const now = Date.now();
      const messages: Message[] = firstMessage
        ? [
            {
              id: nanoid(),
              role: "user",
              content: firstMessage,
              timestamp: now,
              status: "done",
            },
          ]
        : [];
      const task: Task = {
        id,
        title,
        messages,
        createdAt: now,
        updatedAt: now,
        model: currentModel,
      };
      setTasks((prev) => [task, ...prev]);
      setActiveTaskId(id);
      return task;
    },
    [currentModel]
  );

  const addMessage = useCallback(
    (taskId: string, message: Omit<Message, "id" | "timestamp">) => {
      const msg: Message = {
        ...message,
        id: nanoid(),
        timestamp: Date.now(),
      };
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId
            ? { ...t, messages: [...t.messages, msg], updatedAt: Date.now() }
            : t
        )
      );
      return msg;
    },
    []
  );

  const updateMessage = useCallback(
    (taskId: string, messageId: string, updates: Partial<Message>) => {
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId
            ? {
                ...t,
                messages: t.messages.map((m) =>
                  m.id === messageId ? { ...m, ...updates } : m
                ),
                updatedAt: Date.now(),
              }
            : t
        )
      );
    },
    []
  );

  const deleteTask = useCallback(
    (taskId: string) => {
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
      if (activeTaskId === taskId) {
        setActiveTaskId(null);
      }
    },
    [activeTaskId]
  );

  const renameTask = useCallback((taskId: string, newTitle: string) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, title: newTitle } : t))
    );
  }, []);

  return {
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
    renameTask,
  };
}
