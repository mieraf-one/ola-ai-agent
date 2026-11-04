"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export default function MarkdownRenderer({ content, className = "" }: MarkdownRendererProps) {
  // Strip math delimiters ($...$ or $$...$$) to plain text
  const cleanedContent = content.replace(/\$([^\$]+)\$/g, "$1");

  return (
    <div className={`prose max-w-none text-xs sm:text-[13px] text-on-surface leading-relaxed ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ node, ...props }) => (
            <h1 className="text-sm sm:text-base text-on-surface font-bold mt-2 mb-1.5 pb-0.5 border-b border-outline-variant/40" {...props} />
          ),
          h2: ({ node, ...props }) => (
            <h2 className="text-xs sm:text-sm text-on-surface font-semibold mt-2 mb-1" {...props} />
          ),
          h3: ({ node, ...props }) => (
            <h3 className="text-[11px] text-primary font-bold uppercase tracking-wider mt-1.5 mb-0.5" {...props} />
          ),
          p: ({ node, ...props }) => (
            <p className="mb-1.5 last:mb-0 text-on-surface leading-relaxed text-xs sm:text-[13px]" {...props} />
          ),
          ul: ({ node, ...props }) => (
            <ul className="list-disc list-outside pl-4 space-y-0.5 mb-1.5 text-on-surface-variant text-xs sm:text-[13px]" {...props} />
          ),
          ol: ({ node, ...props }) => (
            <ol className="list-decimal list-outside pl-4 space-y-0.5 mb-1.5 text-on-surface-variant text-xs sm:text-[13px]" {...props} />
          ),
          li: ({ node, ...props }) => (
            <li className="leading-relaxed" {...props} />
          ),
          strong: ({ node, ...props }) => (
            <strong className="font-semibold text-on-surface" {...props} />
          ),
          em: ({ node, ...props }) => (
            <em className="text-secondary italic" {...props} />
          ),
          code: ({ node, inline, ...props }: any) => {
            if (inline) {
              return (
                <code
                  className="px-1 py-0.5 rounded bg-surface-container-highest text-primary font-mono text-[11px] border border-outline-variant/60 font-medium"
                  {...props}
                />
              );
            }
            return (
              <pre className="p-2 my-1.5 rounded bg-inverse-surface text-inverse-on-surface font-mono text-[11px] overflow-x-auto leading-relaxed shadow-2xs">
                <code {...props} />
              </pre>
            );
          },
          blockquote: ({ node, ...props }) => (
            <blockquote className="border-l-2 border-primary pl-2.5 my-1 text-on-surface-variant italic bg-surface-container-low/40 py-0.5 rounded-r text-xs" {...props} />
          ),
        }}
      >
        {cleanedContent}
      </ReactMarkdown>
    </div>
  );
}
