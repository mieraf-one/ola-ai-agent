"use client";

import React, { useState } from "react";
import {
  FileCode,
  Terminal as TerminalIcon,
  Folder,
  Download,
  Copy,
  Check,
  RefreshCw,
  FileCheck2,
  Play
} from "lucide-react";
import { WorkspaceFile } from "../types";

interface CodeCanvasProps {
  files: WorkspaceFile[];
  selectedFile: string | null;
  fileContent: string;
  executionOutput: string;
  testOutput: string;
  testsPassed: boolean | null;
  onSelectFile: (filePath: string) => void;
  onRefreshFiles: () => void;
  activeTab: "code" | "terminal" | "files";
  setActiveTab: (tab: "code" | "terminal" | "files") => void;
}

export default function CodeCanvas({
  files,
  selectedFile,
  fileContent,
  executionOutput,
  testOutput,
  testsPassed,
  onSelectFile,
  onRefreshFiles,
  activeTab,
  setActiveTab
}: CodeCanvasProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (fileContent) {
      navigator.clipboard.writeText(fileContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleDownloadZip = () => {
    window.open("http://localhost:8000/api/workspace/download", "_blank");
  };

  return (
    <div className="flex flex-col h-full bg-zinc-950 border-l border-zinc-800/80">
      {/* Top Bar / Tab Switcher */}
      <div className="h-14 border-b border-zinc-800 flex items-center justify-between px-4 bg-zinc-900/60 backdrop-blur-md">
        <div className="flex items-center gap-1.5 p-1 bg-zinc-900 border border-zinc-800 rounded-lg">
          <button
            onClick={() => setActiveTab("code")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === "code"
                ? "bg-zinc-800 text-white shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <FileCode className="w-3.5 h-3.5 text-blue-400" />
            Code Viewer
          </button>

          <button
            onClick={() => setActiveTab("terminal")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === "terminal"
                ? "bg-zinc-800 text-white shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <TerminalIcon className="w-3.5 h-3.5 text-emerald-400" />
            Terminal & Tests
            {testsPassed !== null && (
              <span
                className={`w-2 h-2 rounded-full ${
                  testsPassed ? "bg-emerald-400" : "bg-red-400"
                }`}
              />
            )}
          </button>

          <button
            onClick={() => setActiveTab("files")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              activeTab === "files"
                ? "bg-zinc-800 text-white shadow-sm"
                : "text-zinc-400 hover:text-zinc-200"
            }`}
          >
            <Folder className="w-3.5 h-3.5 text-amber-400" />
            Workspace ({files.length})
          </button>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={onRefreshFiles}
            title="Refresh Files"
            className="p-1.5 rounded-md text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          <button
            onClick={handleDownloadZip}
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 rounded-md text-xs font-medium transition"
          >
            <Download className="w-3.5 h-3.5" />
            Download .ZIP
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-auto relative">
        {/* TAB 1: CODE VIEWER */}
        {activeTab === "code" && (
          <div className="flex flex-col h-full">
            {/* File sub-tabs */}
            <div className="flex items-center gap-1 px-3 py-2 bg-zinc-900/40 border-b border-zinc-800 overflow-x-auto">
              {files.map((file) => (
                <button
                  key={file.path}
                  onClick={() => onSelectFile(file.path)}
                  className={`px-3 py-1 rounded text-xs font-mono flex items-center gap-1.5 transition-all ${
                    selectedFile === file.path
                      ? "bg-zinc-800 text-blue-300 border border-zinc-700 shadow-sm"
                      : "text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-300"
                  }`}
                >
                  <FileCode className={`w-3.5 h-3.5 ${file.is_test ? "text-amber-400" : "text-blue-400"}`} />
                  {file.name}
                </button>
              ))}
            </div>

            {/* Code Display */}
            {selectedFile ? (
              <div className="flex-1 flex flex-col relative font-mono text-xs">
                <div className="absolute top-3 right-4 z-10 flex items-center gap-2">
                  <button
                    onClick={() => {
                      if (selectedFile && fileContent) {
                        const blob = new Blob([fileContent], { type: "text/plain;charset=utf-8" });
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement("a");
                        link.href = url;
                        link.download = selectedFile;
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        URL.revokeObjectURL(url);
                      }
                    }}
                    className="p-1.5 px-2.5 rounded bg-zinc-800/90 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 flex items-center gap-1.5 text-xs shadow-md transition"
                    title={`Download ${selectedFile}`}
                  >
                    <Download className="w-3.5 h-3.5 text-blue-400" />
                    Download
                  </button>
                  <button
                    onClick={handleCopy}
                    className="p-1.5 px-2.5 rounded bg-zinc-800/90 hover:bg-zinc-700 text-zinc-300 border border-zinc-700 flex items-center gap-1.5 text-xs shadow-md transition"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                    {copied ? "Copied!" : "Copy"}
                  </button>
                </div>

                <div className="p-4 overflow-auto flex-1 bg-black/40">
                  <pre className="text-zinc-200 leading-relaxed font-mono">
                    <code>{fileContent}</code>
                  </pre>
                </div>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center text-zinc-500 text-sm">
                No file selected. Select a file from the workspace tab.
              </div>
            )}
          </div>
        )}

        {/* TAB 2: TERMINAL & TESTS */}
        {activeTab === "terminal" && (
          <div className="p-4 space-y-4 font-mono text-xs h-full overflow-auto">
            {/* Execution Card */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 overflow-hidden">
              <div className="p-2.5 px-3 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between">
                <span className="font-semibold text-zinc-300 flex items-center gap-1.5">
                  <Play className="w-3.5 h-3.5 text-blue-400" />
                  Application Execution Output
                </span>
              </div>
              <pre className="p-3 bg-black/50 text-zinc-300 overflow-x-auto whitespace-pre-wrap max-h-56">
                {executionOutput || "No application execution recorded yet."}
              </pre>
            </div>

            {/* Pytest Card */}
            <div className="rounded-xl border border-zinc-800 bg-zinc-900/40 overflow-hidden">
              <div className="p-2.5 px-3 bg-zinc-900 border-b border-zinc-800 flex items-center justify-between">
                <span className="font-semibold text-zinc-300 flex items-center gap-1.5">
                  <FileCheck2 className="w-3.5 h-3.5 text-emerald-400" />
                  Pytest Test Suite Output
                </span>
                {testsPassed !== null && (
                  <span
                    className={`text-[11px] px-2 py-0.5 rounded-full border ${
                      testsPassed
                        ? "bg-emerald-950/80 text-emerald-300 border-emerald-800"
                        : "bg-red-950/80 text-red-300 border-red-800"
                    }`}
                  >
                    {testsPassed ? "ALL TESTS PASSED" : "TESTS FAILED"}
                  </span>
                )}
              </div>
              <pre className="p-3 bg-black/50 text-zinc-300 overflow-x-auto whitespace-pre-wrap">
                {testOutput || "No pytest test results yet."}
              </pre>
            </div>
          </div>
        )}

        {/* TAB 3: WORKSPACE FILE LIST */}
        {activeTab === "files" && (
          <div className="p-4">
            <h3 className="text-xs uppercase font-semibold text-zinc-500 tracking-wider mb-3">
              Workspace Files ({files.length})
            </h3>
            <div className="space-y-1.5">
              {files.map((file) => (
                <div
                  key={file.path}
                  onClick={() => {
                    onSelectFile(file.path);
                    setActiveTab("code");
                  }}
                  className="flex items-center justify-between p-2.5 rounded-lg border border-zinc-800/80 bg-zinc-900/40 hover:bg-zinc-800/60 cursor-pointer transition"
                >
                  <div className="flex items-center gap-2 font-mono text-xs text-zinc-200">
                    <FileCode className={`w-4 h-4 ${file.is_test ? "text-amber-400" : "text-blue-400"}`} />
                    <span>{file.name}</span>
                    {file.is_test && (
                      <span className="text-[10px] bg-amber-950/60 text-amber-300 border border-amber-800/50 px-1.5 py-0.2 rounded">
                        test
                      </span>
                    )}
                  </div>
                  <span className="text-[11px] text-zinc-500 font-mono">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
