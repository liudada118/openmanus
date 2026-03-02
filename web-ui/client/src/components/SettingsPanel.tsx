import { useState, useEffect } from "react";
import { Settings, X } from "lucide-react";
import { getSettings, saveSettings } from "@/lib/api";

interface SettingsPanelProps {
  open: boolean;
  onClose: () => void;
}

export default function SettingsPanel({ open, onClose }: SettingsPanelProps) {
  const [host, setHost] = useState("localhost");
  const [port, setPort] = useState("8000");
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (open) {
      const s = getSettings();
      setHost(s.backendHost);
      setPort(String(s.backendPort));
      setSaved(false);
    }
  }, [open]);

  function handleSave() {
    const portNum = parseInt(port, 10);
    if (isNaN(portNum) || portNum < 1 || portNum > 65535) {
      return;
    }
    saveSettings({ backendHost: host, backendPort: portNum });
    setSaved(true);
    setTimeout(() => {
      onClose();
      window.location.reload();
    }, 800);
  }

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-background border border-border rounded-2xl shadow-2xl w-full max-w-md mx-4 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-border">
          <div className="flex items-center gap-2">
            <Settings size={18} className="text-muted-foreground" />
            <h2 className="font-semibold text-base">连接设置</h2>
          </div>
          <button
            onClick={onClose}
            className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-accent transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div className="px-6 py-5 space-y-5">
          <p className="text-sm text-muted-foreground leading-relaxed">
            配置 OpenManus-GUI 后端 API 服务的连接地址。修改后需要重启前端页面生效。
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">
                后端地址
              </label>
              <input
                type="text"
                value={host}
                onChange={(e) => setHost(e.target.value)}
                placeholder="localhost"
                className="w-full px-3 py-2 text-sm border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-ring/20 focus:border-primary/50 transition-all"
              />
              <p className="text-xs text-muted-foreground mt-1">
                通常为 localhost，如果后端在其他机器上则填写 IP 地址
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">
                后端端口
              </label>
              <input
                type="number"
                value={port}
                onChange={(e) => setPort(e.target.value)}
                placeholder="8000"
                min={1}
                max={65535}
                className="w-full px-3 py-2 text-sm border border-input rounded-lg bg-background focus:outline-none focus:ring-2 focus:ring-ring/20 focus:border-primary/50 transition-all"
              />
              <p className="text-xs text-muted-foreground mt-1">
                OpenManus-GUI 的 api_server.py 默认端口为 8000
              </p>
            </div>
          </div>

          <div className="bg-muted/50 rounded-lg px-4 py-3">
            <p className="text-xs text-muted-foreground leading-relaxed">
              <span className="font-medium text-foreground">提示：</span>
              确保后端已启动：
              <code className="bg-muted px-1.5 py-0.5 rounded text-[11px] font-mono mx-1">
                cd OpenManus-GUI && python api_server.py
              </code>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border bg-muted/30">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm rounded-lg hover:bg-accent transition-colors"
          >
            取消
          </button>
          <button
            onClick={handleSave}
            disabled={saved}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition-opacity disabled:opacity-60"
          >
            {saved ? "已保存 ✓" : "保存并重连"}
          </button>
        </div>
      </div>
    </div>
  );
}
