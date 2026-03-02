import { useState, useEffect } from "react";
import { checkApiHealth, getSettings } from "@/lib/api";
import { Wifi, WifiOff, Settings } from "lucide-react";
import SettingsPanel from "./SettingsPanel";

export default function StatusIndicator() {
  const [connected, setConnected] = useState<boolean | null>(null);
  const [settingsOpen, setSettingsOpen] = useState(false);

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

  const settings = getSettings();
  const portLabel = `${settings.backendHost}:${settings.backendPort}`;

  return (
    <>
      <div className="flex items-center gap-2">
        {connected === null ? (
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <div className="w-1.5 h-1.5 rounded-full bg-muted-foreground/40 animate-pulse" />
            <span>检测中</span>
          </div>
        ) : connected ? (
          <div className="flex items-center gap-1.5 text-xs text-emerald-600">
            <Wifi size={12} />
            <span>已连接</span>
            <span className="text-muted-foreground">({portLabel})</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-xs text-amber-600">
            <WifiOff size={12} />
            <span>未连接</span>
          </div>
        )}
        <button
          onClick={() => setSettingsOpen(true)}
          className="w-7 h-7 flex items-center justify-center rounded-lg hover:bg-accent transition-colors text-muted-foreground"
          title="连接设置"
        >
          <Settings size={14} />
        </button>
      </div>

      <SettingsPanel
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </>
  );
}
