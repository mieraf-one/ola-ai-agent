"use client";

import React, { useState } from "react";
import { StepInfo } from "../types";

interface StepperProps {
  steps: StepInfo[];
  onFileClick?: (filename: string) => void;
}

export default function Stepper({ steps, onFileClick }: StepperProps) {
  const [expandedNodes, setExpandedNodes] = useState<Record<string, boolean>>({
    planning: true,
    research: true,
    critique: true,
  });

  const toggleExpand = (node: string) => {
    setExpandedNodes((prev) => ({ ...prev, [node]: !prev[node] }));
  };

  const getNodeIcon = (node: string, status: StepInfo["status"]) => {
    if (status === "running") {
      return (
        <span className="material-symbols-outlined text-[18px] text-primary animate-spin">
          progress_activity
        </span>
      );
    }
    if (status === "failed") {
      return (
        <span className="material-symbols-outlined text-[18px] text-error">
          error
        </span>
      );
    }

    switch (node) {
      case "planning":
        return <span className="material-symbols-outlined text-[18px] text-secondary">format_list_numbered</span>;
      case "research":
        return <span className="material-symbols-outlined text-[18px] text-primary">search</span>;
      case "code_generation":
      case "save_code":
        return <span className="material-symbols-outlined text-[18px] text-primary">code_blocks</span>;
      case "execute_code":
      case "testing_code":
        return <span className="material-symbols-outlined text-[18px] text-secondary">terminal</span>;
      case "critique":
        return <span className="material-symbols-outlined text-[18px] text-secondary-container">shield</span>;
      case "retry":
      case "fix_code":
        return <span className="material-symbols-outlined text-[18px] text-primary">build</span>;
      default:
        return <span className="material-symbols-outlined text-[18px] text-primary">check_circle</span>;
    }
  };

  const codeSteps = (steps || []).filter(
    (s) => s.node !== "router" && s.node !== "chat" && s.node !== "conclusion"
  );
  if (codeSteps.length === 0) return null;

  return (
    <div className="space-y-1.5 my-2 bg-surface-container-low border border-outline-variant/50 rounded-lg p-2.5 text-xs shadow-2xs">
      <div className="font-label-badge text-[10px] sm:text-[11px] text-on-surface-variant uppercase tracking-wider font-semibold px-1 mb-1 flex items-center justify-between">
        <span className="flex items-center gap-1.5">
          <span className="material-symbols-outlined text-[15px] text-primary">hub</span>
          Execution State Machine
        </span>
        <span className="font-label-code text-[10px] text-secondary">LangGraph Engine</span>
      </div>

      <div className="space-y-1">
        {codeSteps.map((step, idx) => {
          const isExpanded = !!expandedNodes[step.node];
          const hasDetails =
            step.output &&
            ((step.node === "planning" && step.output.plan) ||
              (step.node === "research" && step.output.evidence) ||
              (step.node === "code_generation" && step.output.generated_code) ||
              (step.node === "save_code" && step.output.files) ||
              (step.node === "execute_code" && step.output.execution_output) ||
              (step.node === "testing_code" && step.output.test_output) ||
              (step.node === "critique" && step.output.critique));

          return (
            <div
              key={`${step.node}-${idx}`}
              className="rounded-lg bg-surface-container border border-outline-variant/40 overflow-hidden transition-all shadow-2xs text-xs"
            >
              <div
                onClick={() => hasDetails && toggleExpand(step.node)}
                className={`flex items-center justify-between p-2 px-3 cursor-pointer hover:bg-surface-container-high transition-colors ${
                  step.status === "running" ? "bg-primary-fixed/30 border-l-4 border-l-primary" : ""
                }`}
              >
                <div className="flex items-center gap-2">
                  <div className="w-5 h-5 flex items-center justify-center">
                    {getNodeIcon(step.node, step.status)}
                  </div>
                  <span
                    className={`font-medium text-xs sm:text-[13px] ${
                      step.status === "running" ? "text-primary font-semibold" : "text-on-surface"
                    }`}
                  >
                    {step.label}
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  {step.status === "completed" && (
                    <span className="font-label-badge text-[10px] px-2 py-0.5 rounded-full bg-surface-container-high text-secondary font-semibold flex items-center gap-0.5 border border-outline-variant/50">
                      <span className="material-symbols-outlined text-[13px]">check</span> Done
                    </span>
                  )}
                  {step.status === "running" && (
                    <span className="font-label-badge text-[10px] px-2 py-0.5 rounded-full bg-primary text-on-primary font-semibold animate-pulse shadow-2xs">
                      Running
                    </span>
                  )}
                  {step.status === "failed" && (
                    <span className="font-label-badge text-[10px] px-2 py-0.5 rounded-full bg-error-container text-on-error-container font-semibold">
                      Failed
                    </span>
                  )}
                  {hasDetails && (
                    <span className="material-symbols-outlined text-[16px] text-on-surface-variant transition-transform">
                      {isExpanded ? "expand_less" : "expand_more"}
                    </span>
                  )}
                </div>
              </div>

              {/* Collapsible Content */}
              {isExpanded && hasDetails && (
                <div className="px-3 pb-2.5 pt-1.5 border-t border-outline-variant/40 text-xs bg-surface-container-lowest/80">
                  {/* Planning details */}
                  {step.node === "planning" && step.output?.plan && (
                    <ol className="list-decimal list-inside space-y-1 text-on-surface pl-1 text-xs sm:text-[13px] leading-relaxed">
                      {step.output.plan.map((p: string, pIdx: number) => (
                        <li key={pIdx}>
                          <span className="text-on-surface">{p}</span>
                        </li>
                      ))}
                    </ol>
                  )}

                  {/* Research (Search & RAG) details */}
                  {step.node === "research" && step.output?.evidence && (
                    <div className="space-y-1.5 pt-1">
                      <div className="font-label-badge text-[11px] font-bold text-primary uppercase tracking-wider flex items-center gap-1">
                        <span className="material-symbols-outlined text-[15px]">menu_book</span>
                        Retrieved Technical Evidence &amp; Citations:
                      </div>
                      <div className="space-y-1">
                        {step.output.evidence.map((ev: any, evIdx: number) => (
                          <div
                            key={evIdx}
                            className="p-2 rounded-md bg-surface border border-outline-variant/50 text-[11px] space-y-0.5 shadow-2xs"
                          >
                            <div className="flex items-center justify-between text-primary font-semibold">
                              <span>{ev.title || "Technical Reference"}</span>
                              <span className="font-label-code text-[10px] text-on-surface-variant">
                                {ev.source}
                              </span>
                            </div>
                            <p className="text-on-surface-variant line-clamp-2 leading-relaxed">
                              {ev.snippet}
                            </p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Code generation details */}
                  {step.node === "code_generation" && step.output?.generated_code && (
                    <div className="flex flex-wrap gap-1.5 pt-1">
                      {Object.keys(step.output.generated_code).map((file) => (
                        <button
                          key={file}
                          onClick={() => onFileClick && onFileClick(file)}
                          className="px-2.5 py-1 rounded-md bg-surface-container-high hover:bg-secondary-fixed text-on-surface font-label-code text-xs flex items-center gap-1 border border-outline-variant/60 shadow-2xs transition"
                        >
                          <span className="material-symbols-outlined text-[14px] text-primary">description</span>
                          {file}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* Save code details */}
                  {step.node === "save_code" && step.output?.files && (
                    <div className="text-on-surface-variant text-xs">
                      AST verified &amp; saved {step.output.files.length} file(s) into workspace:{" "}
                      <span className="text-on-surface font-label-code font-semibold">
                        {step.output.files.join(", ")}
                      </span>
                    </div>
                  )}

                  {/* Execution details */}
                  {step.node === "execute_code" && step.output?.execution_output && (
                    <pre className="p-2 bg-inverse-surface text-inverse-on-surface rounded-md font-label-code text-[11px] overflow-x-auto whitespace-pre-wrap max-h-36 leading-relaxed shadow-xs">
                      {step.output.execution_output}
                    </pre>
                  )}

                  {/* Testing details */}
                  {step.node === "testing_code" && step.output?.test_output && (
                    <pre className="p-2 bg-inverse-surface text-inverse-on-surface rounded-md font-label-code text-[11px] overflow-x-auto whitespace-pre-wrap max-h-36 leading-relaxed shadow-xs">
                      {step.output.test_output}
                    </pre>
                  )}

                  {/* Critique details */}
                  {step.node === "critique" && step.output?.critique && (
                    <div className="space-y-1 pt-1 text-xs">
                      <div className="text-secondary font-semibold font-label-badge text-[11px] uppercase tracking-wider flex items-center gap-1">
                        <span className="material-symbols-outlined text-[15px] text-secondary">analytics</span>
                        Diagnosed Issues &amp; Recommended Fixes:
                      </div>
                      <ul className="list-disc list-inside text-error space-y-0.5 pl-1 text-xs">
                        {(step.output.critique.findings || []).map((f: string, fIdx: number) => (
                          <li key={fIdx}>{f}</li>
                        ))}
                      </ul>
                      <div className="text-primary font-medium text-xs pt-1">
                        Recommended: {(step.output.critique.recommended_fixes || []).join("; ")}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
