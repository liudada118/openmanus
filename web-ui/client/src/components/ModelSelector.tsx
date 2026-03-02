import { MODELS, ModelConfig } from "@/lib/types";
import { ChevronDown, Cloud, Monitor, Check } from "lucide-react";
import { useState, useRef, useEffect } from "react";

interface ModelSelectorProps {
  currentModel: string;
  onModelChange: (modelId: string) => void;
}

export default function ModelSelector({
  currentModel,
  onModelChange,
}: ModelSelectorProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const selected = MODELS.find((m) => m.id === currentModel) || MODELS[0];
  const cloudModels = MODELS.filter((m) => m.provider === "openai");
  const localModels = MODELS.filter((m) => m.provider === "ollama");

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-accent transition-colors text-sm font-medium"
      >
        {selected.provider === "ollama" ? (
          <Monitor size={14} className="text-emerald-600" />
        ) : (
          <Cloud size={14} className="text-primary" />
        )}
        <span>{selected.name}</span>
        <ChevronDown
          size={14}
          className={`text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`}
        />
      </button>

      {open && (
        <div className="absolute top-full left-0 mt-1 z-50 bg-popover border border-border rounded-xl shadow-xl py-2 min-w-[280px] animate-in fade-in-0 zoom-in-95 duration-150">
          {/* Cloud Models */}
          <div className="px-3 py-1.5">
            <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
              <Cloud size={12} />
              云端模型
            </p>
          </div>
          {cloudModels.map((model) => (
            <ModelItem
              key={model.id}
              model={model}
              isSelected={currentModel === model.id}
              onSelect={() => {
                onModelChange(model.id);
                setOpen(false);
              }}
            />
          ))}

          <div className="my-1.5 mx-3 border-t border-border" />

          {/* Local Models */}
          <div className="px-3 py-1.5">
            <p className="text-[11px] font-medium text-muted-foreground uppercase tracking-wider flex items-center gap-1.5">
              <Monitor size={12} />
              本地模型 (Ollama)
            </p>
          </div>
          {localModels.map((model) => (
            <ModelItem
              key={model.id}
              model={model}
              isSelected={currentModel === model.id}
              onSelect={() => {
                onModelChange(model.id);
                setOpen(false);
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function ModelItem({
  model,
  isSelected,
  onSelect,
}: {
  model: ModelConfig;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <button
      onClick={onSelect}
      className={`w-full flex items-center gap-3 px-3 py-2 text-left transition-colors ${
        isSelected ? "bg-accent" : "hover:bg-accent/50"
      }`}
    >
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium">{model.name}</span>
          {model.costPerTask && (
            <span
              className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium ${
                model.provider === "ollama"
                  ? "bg-emerald-50 text-emerald-700"
                  : "bg-blue-50 text-blue-700"
              }`}
            >
              {model.costPerTask}
            </span>
          )}
        </div>
        <p className="text-xs text-muted-foreground mt-0.5">
          {model.description}
        </p>
      </div>
      {isSelected && <Check size={16} className="text-primary shrink-0" />}
    </button>
  );
}
