import { useState, useEffect } from "react";
import { checkApiHealth } from "@/lib/api";
import { Wifi, WifiOff } from "lucide-react";

export default function StatusIndicator() {
  const [connected, setConnected] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;

    async function check() {
      const ok = await checkApiHealth();
      if (mounted) setConnected(ok);
    }

    check();
    const interval = setInterval(check, 10000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  if (connected === null) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
        <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 animate-pulse" />
        <span>检测中</span>
      </div>
    );
  }

  if (connected) {
    return (
      <div className="flex items-center gap-1.5 text-xs text-emerald-600">
        <Wifi size={12} />
        <span>已连接</span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-1.5 text-xs text-amber-600 group relative">
      <WifiOff size={12} />
      <span>未连接</span>
      <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block bg-popover border border-border rounded-lg shadow-lg p-3 min-w-[240px] z-50">
        <p className="text-xs font-medium text-foreground mb-1">后端未连接</p>
        <p className="text-[11px] text-muted-foreground leading-relaxed">
          请确保 OpenManus-GUI 的 API 服务已启动：
          <br />
          <code className="bg-muted px-1 py-0.5 rounded text-[10px] font-mono">
            python api_server.py
          </code>
        </p>
      </div>
    </div>
  );
}
