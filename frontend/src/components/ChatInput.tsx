"use client";

import React, { useState, useRef, useEffect } from "react";
import { ArrowUp, Sparkles, Loader2 } from "lucide-react";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const SUGGESTIONS = [
  "Create a binary search function with pytest tests",
  "Build a password strength validator with unit tests",
  "Create a roman numeral converter with tests",
];

export default function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-4 bg-gradient-to-t from-zinc-950 via-zinc-950/95 to-transparent">
      {/* Suggestions */}
      <div className="flex flex-wrap gap-2 mb-2 px-1">
        {SUGGESTIONS.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSendMessage(suggestion)}
            disabled={isLoading}
            className="text-xs px-2.5 py-1 rounded-full bg-zinc-900 hover:bg-zinc-800 text-zinc-400 hover:text-zinc-200 border border-zinc-800 transition disabled:opacity-40"
          >
            {suggestion}
          </button>
        ))}
      </div>

      {/* Input container */}
      <form
        onSubmit={handleSubmit}
        className="relative flex items-end rounded-2xl bg-zinc-900 border border-zinc-800 focus-within:border-blue-500/80 shadow-lg px-4 py-3 transition"
      >
        <Sparkles className="w-4 h-4 text-blue-400 mr-2.5 mb-2 flex-shrink-0" />

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Ola to build or modify Python code..."
          rows={1}
          disabled={isLoading}
          className="flex-1 bg-transparent text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none resize-none max-h-40 leading-relaxed font-sans"
        />

        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="ml-2 w-8 h-8 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-800 text-white disabled:text-zinc-600 flex items-center justify-center transition flex-shrink-0"
        >
          {isLoading ? (
            <Loader2 className="w-4 h-4 animate-spin text-cyan-300" />
          ) : (
            <ArrowUp className="w-4 h-4" />
          )}
        </button>
      </form>
    </div>
  );
}
