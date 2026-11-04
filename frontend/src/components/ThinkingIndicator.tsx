"use client";

import React from "react";

interface ThinkingIndicatorProps {
  label?: string;
  variant?: "full" | "compact";
}

export default function ThinkingIndicator({
  label = "Ola is reasoning...",
  variant = "full",
}: ThinkingIndicatorProps) {
  if (variant === "compact") {
    return (
      <div className="flex items-center justify-between py-0.5 text-xs font-medium">
        <div className="flex items-center gap-1 text-primary">
          <span className="material-symbols-outlined text-[14px] animate-spin" style={{ animationDuration: "3s" }}>
            psychology
          </span>
          <span className="text-primary font-semibold text-[11px]">{label}</span>
          <div className="flex items-center gap-0.5 ml-1">
            <span className="w-1 h-1 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]" />
            <span className="w-1 h-1 rounded-full bg-secondary animate-bounce [animation-delay:-0.15s]" />
            <span className="w-1 h-1 rounded-full bg-tertiary animate-bounce" />
          </div>
        </div>
        <span className="font-label-code text-[9px] text-on-surface-variant font-mono animate-pulse">
          Streaming State...
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2 py-1 text-on-surface">
      <div className="relative flex items-center justify-center w-6 h-6 flex-shrink-0">
        <div className="absolute inset-0 rounded-full bg-primary/20 animate-ping" />
        <div className="relative w-6 h-6 rounded-full bg-primary text-on-primary flex items-center justify-center shadow-xs">
          <span className="material-symbols-outlined text-[14px] animate-spin" style={{ animationDuration: "4s" }}>
            psychology
          </span>
        </div>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="text-xs font-semibold text-primary">
          {label}
        </span>
        <div className="flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]" />
          <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-bounce [animation-delay:-0.15s]" />
          <span className="w-1.5 h-1.5 rounded-full bg-tertiary animate-bounce" />
        </div>
      </div>
    </div>
  );
}
