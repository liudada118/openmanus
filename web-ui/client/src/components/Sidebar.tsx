import { Task } from "@/lib/types";
import { Plus, MessageSquare, Trash2, MoreHorizontal } from "lucide-react";
import { useState, useRef, useEffect } from "react";

interface SidebarProps {
  tasks: Task[];
  activeTaskId: string | null;
  onSelectTask: (id: string) => void;
  onCreateTask: () => void;
  onDeleteTask: (id: string) => void;
  collapsed: boolean;
  onToggle: () => void;
}

function formatTime(ts: number): string {
  const now = Date.now();
  const diff = now - ts;
  if (diff < 60000) return "刚刚";
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
  const d = new Date(ts);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

export default function Sidebar({
  tasks,
  activeTaskId,
  onSelectTask,
  onCreateTask,
  onDeleteTask,
  collapsed,
  onToggle,
}: SidebarProps) {
  const [menuOpen, setMenuOpen] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(null);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  if (collapsed) {
    return (
      <div className="w-[52px] border-r border-border bg-sidebar flex flex-col items-center py-3 gap-2 shrink-0">
        <button
          onClick={onToggle}
          className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-sidebar-accent transition-colors"
          title="展开侧边栏"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="3" y1="12" x2="21" y2="12" />
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <button
          onClick={onCreateTask}
          className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-sidebar-accent transition-colors text-muted-foreground"
          title="新建任务"
        >
          <Plus size={18} />
        </button>
      </div>
    );
  }

  return (
    <div className="w-[260px] border-r border-border bg-sidebar flex flex-col shrink-0">
      {/* Header */}
      <div className="h-14 flex items-center justify-between px-4 border-b border-border">
        <div className="flex items-center gap-2">
          <button
            onClick={onToggle}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-sidebar-accent transition-colors"
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          <span className="font-semibold text-sm tracking-tight">任务列表</span>
        </div>
        <button
          onClick={onCreateTask}
          className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-sidebar-accent transition-colors text-muted-foreground"
          title="新建任务"
        >
          <Plus size={18} />
        </button>
      </div>

      {/* Task List */}
      <div className="flex-1 overflow-y-auto py-2 px-2">
        {tasks.length === 0 ? (
          <div className="text-center text-muted-foreground text-xs mt-8 px-4">
            <p>暂无任务</p>
            <p className="mt-1">点击上方 + 创建新任务</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {tasks.map((task) => (
              <div
                key={task.id}
                onClick={() => onSelectTask(task.id)}
                className={`group relative flex items-center gap-2.5 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                  activeTaskId === task.id
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "hover:bg-sidebar-accent/50 text-sidebar-foreground"
                }`}
              >
                <MessageSquare size={15} className="shrink-0 text-muted-foreground" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm truncate leading-snug">{task.title}</p>
                  <p className="text-[11px] text-muted-foreground mt-0.5">
                    {formatTime(task.updatedAt)}
                  </p>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setMenuOpen(menuOpen === task.id ? null : task.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 w-6 h-6 flex items-center justify-center rounded hover:bg-background/50 transition-all shrink-0"
                >
                  <MoreHorizontal size={14} />
                </button>

                {menuOpen === task.id && (
                  <div
                    ref={menuRef}
                    className="absolute right-2 top-full z-50 bg-popover border border-border rounded-lg shadow-lg py-1 min-w-[120px]"
                  >
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onDeleteTask(task.id);
                        setMenuOpen(null);
                      }}
                      className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-destructive hover:bg-accent transition-colors"
                    >
                      <Trash2 size={14} />
                      删除任务
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
