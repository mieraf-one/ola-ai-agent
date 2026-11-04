"use client";

import React, { useState, useEffect, useRef } from "react";
import Stepper from "../components/Stepper";
import ApprovalCard from "../components/ApprovalCard";
import ThinkingIndicator from "../components/ThinkingIndicator";
import MarkdownRenderer from "../components/MarkdownRenderer";
import { ChatMessage, WorkspaceFile, StepInfo } from "../types";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome-1",
      role: "assistant",
      content:
        "Hello! I am **Ola**, your autonomous AI software engineer. Tell me what Python code, algorithms, or test suites you would like to design and build.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const [threadId, setThreadId] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [input, setInput] = useState<string>("");

  // Right Context & Canvas state
  const [workspaceFiles, setWorkspaceFiles] = useState<WorkspaceFile[]>([]);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileContent, setFileContent] = useState<string>("");
  const [executionOutput, setExecutionOutput] = useState<string>("");
  const [testOutput, setTestOutput] = useState<string>("");
  const [testsPassed, setTestsPassed] = useState<boolean | null>(null);
  const [activeTab, setActiveTab] = useState<"code" | "terminal" | "tests">("code");
  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [copyCodeSuccess, setCopyCodeSuccess] = useState<boolean>(false);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Initialize unique threadId
  useEffect(() => {
    setThreadId(`thread_${Math.random().toString(36).substring(2, 9)}`);
    fetchFiles();
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const fetchFiles = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/workspace/files");
      const data = await res.json();
      if (data.files) {
        setWorkspaceFiles(data.files);
        if (data.files.length > 0 && !selectedFile) {
          loadFileContent(data.files[0].path);
        }
      }
    } catch (err) {
      console.error("Error fetching workspace files:", err);
    }
  };

  const loadFileContent = async (path: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/workspace/file?path=${encodeURIComponent(path)}`);
      const data = await res.json();
      if (data.content !== undefined) {
        setSelectedFile(path);
        setFileContent(data.content);
      }
    } catch (err) {
      console.error("Error fetching file content:", err);
    }
  };

  const handleNewChat = () => {
    const newId = `thread_${Math.random().toString(36).substring(2, 9)}`;
    setThreadId(newId);
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        role: "assistant",
        content: "Started a fresh conversation session with **Ola**. What Python system or module would you like to build next?",
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      },
    ]);
    setExecutionOutput("");
    setTestOutput("");
    setTestsPassed(null);
  };

  const handleSendMessage = async (textToSend?: string) => {
    const taskText = (textToSend !== undefined ? textToSend : input).trim();
    if (isLoading || !taskText) return;

    setInput("");
    const userMsgId = `user-${Date.now()}`;
    const assistantMsgId = `assistant-${Date.now()}`;

    const userMsg: ChatMessage = {
      id: userMsgId,
      role: "user",
      content: taskText,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: "assistant",
      steps: [],
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ task: taskText, thread_id: threadId }),
      });

      if (!response.body) throw new Error("No response body stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const block of lines) {
          if (!block.trim()) continue;
          const eventMatch = block.match(/^event:\s*(\w+)/m);
          const dataMatch = block.match(/^data:\s*(.+)$/m);

          if (eventMatch && dataMatch) {
            const eventType = eventMatch[1];
            const data = JSON.parse(dataMatch[1]);

            if (eventType === "start") {
              if (data.thread_id) {
                setThreadId(data.thread_id);
              }
            } else if (eventType === "step") {
              const { node, label, output, status: stepStatus, thread_id: streamThreadId } = data;
              if (streamThreadId) {
                setThreadId(streamThreadId);
              }

              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;

                  const existingSteps = msg.steps || [];
                  const stepIndex = existingSteps.findIndex((s) => s.node === node);

                  const updatedStep: StepInfo = {
                    node,
                    label,
                    status: (stepStatus as any) || "completed",
                    output,
                  };

                  let newSteps = [...existingSteps];
                  if (stepIndex >= 0) {
                    newSteps[stepIndex] = updatedStep;
                  } else {
                    newSteps.push(updatedStep);
                  }

                  return { ...msg, steps: newSteps };
                })
              );

              // Update code viewer automatically if files generated
              if (output?.generated_code) {
                const firstFilename = Object.keys(output.generated_code)[0];
                if (firstFilename) {
                  setSelectedFile(firstFilename);
                  setFileContent(output.generated_code[firstFilename]);
                }
              }

              if ((node === "chat" || node === "conclusion") && (output?.chat_response || output?.final_response)) {
                const text = output.final_response || output.chat_response;
                setMessages((prev) =>
                  prev.map((msg) => {
                    if (msg.id !== assistantMsgId) return msg;
                    return { ...msg, content: text };
                  })
                );
              }

              if (output?.execution_output) setExecutionOutput(output.execution_output);
              if (output?.test_output) {
                setTestOutput(output.test_output);
                setTestsPassed(output.tests_passed ?? null);
              }
            } else if (eventType === "interrupt") {
              const { node, plan, thread_id: streamThreadId } = data;
              const resolvedThreadId = streamThreadId || threadId;
              if (streamThreadId) setThreadId(streamThreadId);

              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;
                  return {
                    ...msg,
                    isInterrupted: true,
                    interruptState: { node, plan, threadId: resolvedThreadId },
                  };
                })
              );
              setIsLoading(false);
            } else if (eventType === "reject") {
              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;
                  return {
                    ...msg,
                    isInterrupted: false,
                    content: data.message || "Task cancelled by user.",
                  };
                })
              );
              setIsLoading(false);
            } else if (eventType === "complete") {
              const finalState = data.state;
              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;

                  let displayContent = finalState?.final_response || finalState?.chat_response || msg.content || "";
                  if (!displayContent) {
                    displayContent = finalState?.tests_passed
                      ? "Task completed successfully! All unit tests passed."
                      : "Task finished execution. Inspect the test terminal for details.";
                  }

                  return {
                    ...msg,
                    content: displayContent,
                    finalState,
                  };
                })
              );

              if (finalState?.execution_output) setExecutionOutput(finalState.execution_output);
              if (finalState?.test_output) {
                setTestOutput(finalState.test_output);
                setTestsPassed(finalState.tests_passed ?? null);
              }
              fetchFiles();
            } else if (eventType === "error") {
              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;
                  return {
                    ...msg,
                    content: `Error encountered: ${data.error}`,
                  };
                })
              );
            }
          }
        }
      }
    } catch (err: any) {
      console.error("Stream error:", err);
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.id !== assistantMsgId) return msg;
          return {
            ...msg,
            content: `Failed to connect to backend: ${err.message}`,
          };
        })
      );
    } finally {
      setIsLoading(false);
      fetchFiles();
    }
  };

  const handleResumeWorkflow = async (
    assistantMsgId: string,
    action: "approve" | "update" | "reject",
    newPlan?: string[],
    overrideThreadId?: string
  ) => {
    const activeThreadId = overrideThreadId || threadId;
    setIsLoading(true);

    setMessages((prev) =>
      prev.map((msg) => {
        if (msg.id !== assistantMsgId) return msg;
        const existingSteps = (msg.steps || []).filter((s) => s.node !== "code_generation");
        const runningStep: StepInfo = {
          node: "code_generation",
          label: "Generating Python code & tests...",
          status: "running",
        };
        return {
          ...msg,
          isInterrupted: false,
          steps: [...existingSteps, runningStep],
        };
      })
    );

    if (action === "reject") {
      setMessages((prev) =>
        prev.map((msg) => {
          if (msg.id !== assistantMsgId) return msg;
          return { ...msg, content: "Task cancelled by user." };
        })
      );
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/api/chat/resume", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          thread_id: activeThreadId,
          action,
          plan: newPlan,
        }),
      });

      if (!response.body) throw new Error("No response body stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const block of lines) {
          if (!block.trim()) continue;
          const eventMatch = block.match(/^event:\s*(\w+)/m);
          const dataMatch = block.match(/^data:\s*(.+)$/m);

          if (eventMatch && dataMatch) {
            const eventType = eventMatch[1];
            const data = JSON.parse(dataMatch[1]);

            if (eventType === "step") {
              const { node, label, output, status: stepStatus, thread_id: streamThreadId } = data;
              if (streamThreadId) setThreadId(streamThreadId);

              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;

                  const existingSteps = msg.steps || [];
                  const stepIndex = existingSteps.findIndex((s) => s.node === node);

                  const updatedStep: StepInfo = {
                    node,
                    label,
                    status: (stepStatus as any) || "completed",
                    output,
                  };

                  let newSteps = [...existingSteps];
                  if (stepIndex >= 0) {
                    newSteps[stepIndex] = updatedStep;
                  } else {
                    newSteps.push(updatedStep);
                  }

                  return { ...msg, steps: newSteps };
                })
              );

              if (node === "conclusion" && (output?.final_response || output?.chat_response)) {
                const text = output.final_response || output.chat_response;
                setMessages((prev) =>
                  prev.map((msg) => {
                    if (msg.id !== assistantMsgId) return msg;
                    return { ...msg, content: text };
                  })
                );
              }

              if (output?.generated_code) {
                const firstFilename = Object.keys(output.generated_code)[0];
                if (firstFilename) {
                  setSelectedFile(firstFilename);
                  setFileContent(output.generated_code[firstFilename]);
                }
              }

              if (output?.execution_output) setExecutionOutput(output.execution_output);
              if (output?.test_output) {
                setTestOutput(output.test_output);
                setTestsPassed(output.tests_passed ?? null);
              }
            } else if (eventType === "complete") {
              const finalState = data.state;
              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;

                  let displayContent = finalState?.final_response || finalState?.chat_response || msg.content || "";
                  if (!displayContent) {
                    displayContent = finalState?.tests_passed
                      ? "Task completed successfully! All unit tests passed."
                      : "Task finished execution.";
                  }

                  return {
                    ...msg,
                    content: displayContent,
                    finalState,
                  };
                })
              );

              if (finalState?.execution_output) setExecutionOutput(finalState.execution_output);
              if (finalState?.test_output) {
                setTestOutput(finalState.test_output);
                setTestsPassed(finalState.tests_passed ?? null);
              }
              fetchFiles();
            } else if (eventType === "error") {
              setMessages((prev) =>
                prev.map((msg) => {
                  if (msg.id !== assistantMsgId) return msg;
                  return {
                    ...msg,
                    content: `Error during code generation: ${data.error}`,
                  };
                })
              );
            }
          }
        }
      }
    } catch (err: any) {
      console.error("Resume error:", err);
    } finally {
      setIsLoading(false);
      fetchFiles();
    }
  };

  const handleCopyCode = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopyCodeSuccess(true);
    setTimeout(() => setCopyCodeSuccess(false), 2000);
  };

  const handleDownloadFile = (fileName: string, content?: string) => {
    if (content) {
      const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } else {
      window.open(
        `http://localhost:8000/api/workspace/file/download?path=${encodeURIComponent(fileName)}`,
        "_blank"
      );
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="bg-surface font-body-md text-on-surface antialiased selection:bg-secondary-fixed selection:text-on-secondary-fixed min-h-screen flex text-xs sm:text-[13px]">
      {/* 1. LEFT SIDEBAR */}
      <aside
        className={`fixed left-0 top-0 h-full ${
          isSidebarOpen ? "w-56" : "w-14"
        } bg-surface-container-low z-50 flex flex-col justify-between shadow-[0_1px_6px_rgba(0,0,0,0.03)] border-r border-outline-variant/30 transition-all duration-200`}
      >
        <div className="flex flex-col flex-1 overflow-y-auto px-2.5 pt-2.5">
          {/* Logo & Collapse */}
          <div className="flex items-center justify-between px-1 mb-2.5">
            {isSidebarOpen && (
              <div className="flex items-center gap-1.5">
                <div className="w-6 h-6 rounded-full bg-primary text-on-primary flex items-center justify-center shadow-xs">
                  <span className="material-symbols-outlined text-[15px]">neurology</span>
                </div>
                <span className="font-headline-sm text-sm text-on-surface font-bold tracking-tight">
                  Ola
                </span>
                <span className="font-label-badge text-[9px] px-1.5 py-0.2 rounded-full bg-primary-fixed text-on-primary-fixed font-bold">
                  2.5
                </span>
              </div>
            )}
            <button
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="w-7 h-7 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors ml-auto"
              title="Toggle sidebar"
              type="button"
            >
              <span className="material-symbols-outlined text-[16px]">dock_to_right</span>
            </button>
          </div>

          {/* New Chat Button */}
          {isSidebarOpen && (
            <div className="mb-2.5">
              <button
                onClick={handleNewChat}
                className="w-full flex items-center justify-center gap-1.5 py-1.5 px-3 rounded-full bg-primary text-on-primary font-headline-sm text-xs shadow-2xs hover:bg-primary-container transition-all"
                type="button"
              >
                <span className="material-symbols-outlined text-[15px]">add</span>
                <span className="font-semibold">New Chat</span>
              </button>
            </div>
          )}

          {/* Active Navigation / Sessions */}
          {isSidebarOpen && (
            <div className="flex-1 space-y-2">
              <div className="space-y-0.5">
                <div className="px-1 py-0.5">
                  <span className="font-label-badge text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">
                    Current Session
                  </span>
                </div>
                <nav className="space-y-0.5">
                  <div className="group flex items-center justify-between px-2 py-1 rounded-md bg-surface-container-high text-on-surface font-medium text-xs shadow-2xs">
                    <span className="truncate flex items-center gap-1.5">
                      <span className="material-symbols-outlined text-[14px] text-primary">chat_bubble</span>
                      <span className="truncate">{messages[1]?.content?.slice(0, 18) || "Python Agent"}...</span>
                    </span>
                    <span className="font-label-code text-[9px] text-secondary">Active</span>
                  </div>
                </nav>
              </div>

              {/* Workspace Files Section */}
              <div className="space-y-0.5">
                <div className="px-1 py-0.5 flex items-center justify-between">
                  <span className="font-label-badge text-[10px] text-on-surface-variant uppercase tracking-wider font-semibold">
                    Workspace ({workspaceFiles.length})
                  </span>
                  <button
                    onClick={fetchFiles}
                    className="text-primary hover:text-primary-container text-[11px] font-mono"
                    title="Refresh files"
                  >
                    <span className="material-symbols-outlined text-[13px]">refresh</span>
                  </button>
                </div>
                <nav className="space-y-0.5 max-h-40 overflow-y-auto pr-0.5">
                  {workspaceFiles.map((file) => (
                    <button
                      key={file.path}
                      onClick={() => {
                        loadFileContent(file.path);
                        setActiveTab("code");
                      }}
                      className={`w-full group flex items-center justify-between px-2 py-1 rounded text-left transition-colors text-[11px] ${
                        selectedFile === file.path
                          ? "bg-secondary-fixed text-on-secondary-fixed font-semibold"
                          : "text-on-surface-variant hover:bg-surface-container hover:text-on-surface"
                      }`}
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <span className="material-symbols-outlined text-[14px] text-primary">
                          {file.is_test ? "science" : "description"}
                        </span>
                        <span className="font-label-code text-[11px] truncate">{file.name}</span>
                      </div>
                      <span className="font-label-code text-[9px] opacity-70">
                        {Math.round(file.size / 1024 * 10) / 10}k
                      </span>
                    </button>
                  ))}
                  {workspaceFiles.length === 0 && (
                    <div className="text-[10px] text-on-surface-variant/70 italic px-1 py-0.5">
                      No files generated yet
                    </div>
                  )}
                </nav>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar Footer */}
        {isSidebarOpen && (
          <div className="p-2 border-t border-outline-variant/30 bg-surface-container-low text-xs">
            <nav className="space-y-0.5">
              <div className="flex items-center gap-1.5 px-1.5 py-1 rounded text-on-surface-variant text-[11px]">
                <span className="material-symbols-outlined text-[14px] text-secondary">memory</span>
                <span>LangGraph MemorySaver</span>
              </div>
              <div className="flex items-center justify-between px-1.5 py-0.5 text-on-surface-variant font-label-code text-[10px]">
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
                  FastAPI Live
                </span>
                <span>Port 8000</span>
              </div>
            </nav>
          </div>
        )}
      </aside>

      {/* 2. MAIN VIEW AREA (Shifted by Sidebar) */}
      <div className={`flex-1 ${isSidebarOpen ? "pl-56" : "pl-14"} min-h-screen flex flex-col bg-surface transition-all duration-200`}>
        {/* Top Fixed Header */}
        <header className={`fixed top-0 ${isSidebarOpen ? "left-56" : "left-14"} right-0 h-10 bg-surface/90 backdrop-blur-xl z-40 shadow-[0_1px_4px_rgba(0,0,0,0.3)] border-b border-outline-variant/40 transition-all duration-200`}>
          <div className="w-full h-10 px-3 sm:px-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1.5">
                <span className="material-symbols-outlined text-primary text-[16px]">terminal</span>
                <span className="font-headline-sm text-xs sm:text-sm font-semibold text-on-surface">
                  Ola AI Code Agent Studio
                </span>
                <span className="font-label-badge text-[9px] px-1.5 py-0.2 rounded-full bg-secondary-fixed text-on-secondary-fixed font-bold">
                  Autonomous
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex items-center gap-1">
                {/* Download Workspace Zip */}
                <a
                  href="http://localhost:8000/api/workspace/download"
                  download="workspace.zip"
                  className="w-7 h-7 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
                  title="Download workspace zip"
                >
                  <span className="material-symbols-outlined text-[15px]">download</span>
                </a>

                {/* Session Reset */}
                <button
                  onClick={handleNewChat}
                  className="w-7 h-7 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container hover:text-on-surface transition-colors"
                  title="Restart session"
                  type="button"
                >
                  <span className="material-symbols-outlined text-[15px]">restart_alt</span>
                </button>
              </div>

              {/* Active Thread Tag */}
              <div className="font-label-code text-[10px] text-on-surface-variant bg-surface-container px-2 py-0.5 rounded-full border border-outline-variant/40">
                {threadId}
              </div>
            </div>
          </div>
        </header>

        {/* Main Body */}
        <main className="relative pt-10 flex-1 w-full bg-surface">
          <div className="flex-1 w-full flex items-start justify-between relative pb-24">
            {/* CENTRAL CONVERSATION THREAD */}
            <div className="flex-1 max-w-3xl mx-auto px-3 sm:px-4 py-3 w-full flex flex-col space-y-2.5">
              {/* Topic Metadata Header */}
              <div className="flex flex-wrap items-center justify-between gap-1 pb-1 border-b border-outline-variant/30 text-xs">
                <div className="flex items-center gap-1.5">
                  <span className="font-medium text-on-surface flex items-center gap-1 text-xs">
                    <span className="material-symbols-outlined text-primary text-[15px]">verified</span>
                    LangGraph Multi-Category Tool State Machine
                  </span>
                </div>
                <div className="flex items-center gap-1 text-on-surface-variant text-[11px]">
                  <span className="material-symbols-outlined text-[14px]">history_edu</span>
                  <span>Checkpointer active</span>
                </div>
              </div>

              {/* Messages Feed */}
              {messages.map((msg, idx) => {
                const isLast = idx === messages.length - 1;
                const isThinking = isLast && msg.role === "assistant" && isLoading && !msg.isInterrupted;
                const hasNoSteps = !msg.steps || msg.steps.length === 0;
                const hasNoContent = !msg.content || msg.content.trim() === "";

                // Check if message output generated code files
                const codeFiles =
                  msg.finalState?.generated_code ||
                  msg.steps?.find((s) => s.output?.generated_code)?.output?.generated_code;

                const generatedFileNames: string[] = Array.from(
                  new Set([
                    ...(msg.finalState?.files || []),
                    ...(codeFiles ? Object.keys(codeFiles) : [])
                  ])
                );

                return (
                  <div key={msg.id} className="w-full">
                    {/* USER TURN */}
                    {msg.role === "user" && (
                      <div className="flex flex-col items-end w-full group mb-2">
                        <div className="flex items-center gap-1 mb-0.5 pr-1">
                          <span className="font-label-code text-[10px] text-on-surface-variant/60">
                            {msg.timestamp}
                          </span>
                        </div>
                        <div className="max-w-xl bg-secondary-fixed text-on-secondary-fixed rounded-xl rounded-tr-xs p-2.5 px-3.5 shadow-2xs">
                          <p className="text-xs sm:text-[13px] leading-relaxed whitespace-pre-wrap">
                            {msg.content}
                          </p>
                        </div>
                      </div>
                    )}

                    {/* ASSISTANT (OLA) TURN */}
                    {msg.role === "assistant" && (
                      <div className="flex flex-col w-full mb-2.5">
                        {/* Identity Header */}
                        <div className="flex items-center justify-between mb-1">
                          <div className="flex items-center gap-1.5">
                            <div className="w-6 h-6 rounded-full bg-primary text-on-primary flex items-center justify-center shadow-xs">
                              <span className="material-symbols-outlined text-[14px]">neurology</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="text-xs sm:text-[13px] font-bold text-on-surface">
                                Ola
                              </span>
                              <span className="font-label-badge text-[9px] px-1.5 py-0.2 rounded-full bg-surface-container text-on-surface-variant font-medium">
                                Autonomous Code Agent
                              </span>
                            </div>
                          </div>
                          <span className="font-label-code text-[10px] text-on-surface-variant/70">
                            {msg.timestamp}
                          </span>
                        </div>

                        {/* Collapsible Reasoning & Evidence Drawer */}
                        {msg.steps && msg.steps.length > 0 && (
                          <div className="bg-surface-container-low rounded-lg p-2 mb-1.5 border border-outline-variant/40 shadow-2xs">
                            <details className="group cursor-pointer">
                              <summary className="flex items-center justify-between text-on-surface-variant list-none select-none text-xs">
                                <div className="flex items-center gap-1.5">
                                  <span
                                    className="material-symbols-outlined text-primary text-[15px] animate-spin"
                                    style={{ animationDuration: "6s" }}
                                  >
                                    psychology
                                  </span>
                                  <span className="font-medium text-on-surface">
                                    {msg.steps.length} LangGraph nodes executed
                                  </span>
                                  <span className="text-outline-variant">•</span>
                                  <span className="text-on-surface-variant text-[11px]">
                                    Search, RAG, Pytest, &amp; AST validation verified
                                  </span>
                                </div>
                                <span className="material-symbols-outlined text-[15px] transition-transform duration-200 group-open:rotate-180">
                                  expand_more
                                </span>
                              </summary>
                              <div className="mt-1 pt-1 pl-2 space-y-0.5 font-label-code text-[11px] text-on-surface-variant">
                                {msg.finalState?.decision_explanations?.map((dec: string, dIdx: number) => (
                                  <p key={dIdx} className="leading-relaxed">
                                    {dIdx + 1}. {dec}
                                  </p>
                                ))}
                              </div>
                            </details>
                          </div>
                        )}

                        {/* Stepper Workflow */}
                        {msg.steps && msg.steps.length > 0 && (
                          <Stepper
                            steps={msg.steps}
                            onFileClick={(file) => {
                              loadFileContent(file);
                              setActiveTab("code");
                            }}
                          />
                        )}

                        {/* Human-in-the-Loop Plan Approval Card */}
                        {msg.isInterrupted && msg.interruptState && (
                          <ApprovalCard
                            plan={msg.interruptState.plan}
                            onApprove={() =>
                              handleResumeWorkflow(msg.id, "approve", undefined, msg.interruptState?.threadId)
                            }
                            onUpdatePlan={(newPlan) =>
                              handleResumeWorkflow(msg.id, "update", newPlan, msg.interruptState?.threadId)
                            }
                            onReject={() =>
                              handleResumeWorkflow(msg.id, "reject", undefined, msg.interruptState?.threadId)
                            }
                            disabled={isLoading}
                          />
                        )}

                        {/* Initial Thinking State */}
                        {isThinking && hasNoSteps && hasNoContent && (
                          <div className="my-1.5">
                            <ThinkingIndicator label="Ola is reasoning and planning..." variant="full" />
                          </div>
                        )}

                        {/* Markdown Output */}
                        {msg.content && (
                          <div className="bg-surface-container-lowest rounded-xl p-3 px-3.5 shadow-2xs border border-outline-variant/30 my-1 text-xs sm:text-[13px]">
                            <MarkdownRenderer content={msg.content} />
                          </div>
                        )}

                        {/* Code Artifact Box if Code Generated */}
                        {codeFiles && Object.keys(codeFiles).length > 0 && (
                          <div className="rounded-xl bg-surface-container-highest shadow-2xs overflow-hidden my-2 border border-outline-variant/60">
                            {/* Artifact Toolbar */}
                            <div className="bg-surface-container-high px-3 py-1.5 flex items-center justify-between text-xs">
                              <div className="flex items-center gap-1.5">
                                <span className="material-symbols-outlined text-primary text-[16px]">
                                  code_blocks
                                </span>
                                <span className="font-label-code font-semibold text-on-surface">
                                  {Object.keys(codeFiles)[0]}
                                </span>
                                <span className="px-1.5 py-0.2 rounded bg-surface-container text-on-surface-variant font-label-code text-[10px]">
                                  Python 3.14
                                </span>
                              </div>
                              <div className="flex items-center gap-1">
                                <button
                                  onClick={() => handleCopyCode(codeFiles[Object.keys(codeFiles)[0]])}
                                  className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-surface text-on-surface hover:bg-surface-container-lowest text-xs shadow-2xs transition-all"
                                  type="button"
                                >
                                  <span className="material-symbols-outlined text-[13px]">content_copy</span>
                                  <span>{copyCodeSuccess ? "Copied!" : "Copy"}</span>
                                </button>
                                <button
                                  onClick={() => handleDownloadFile(Object.keys(codeFiles)[0], codeFiles[Object.keys(codeFiles)[0]])}
                                  className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-surface-container-low text-primary hover:bg-surface-container text-xs shadow-2xs transition-all font-medium border border-outline-variant/30"
                                  title={`Download ${Object.keys(codeFiles)[0]}`}
                                  type="button"
                                >
                                  <span className="material-symbols-outlined text-[13px]">download</span>
                                  <span>Download</span>
                                </button>
                                <button
                                  onClick={() => {
                                    loadFileContent(Object.keys(codeFiles)[0]);
                                    setActiveTab("code");
                                  }}
                                  className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-primary text-on-primary hover:bg-primary-container text-xs shadow-2xs transition-all font-medium"
                                  type="button"
                                >
                                  <span className="material-symbols-outlined text-[14px]">visibility</span>
                                  <span>Open in Canvas</span>
                                </button>
                              </div>
                            </div>
                            {/* Code Box */}
                            <div className="p-2.5 bg-inverse-surface text-inverse-on-surface font-label-code text-xs overflow-x-auto leading-relaxed max-h-56">
                              <pre className="font-label-code">
                                <code>{codeFiles[Object.keys(codeFiles)[0]]}</code>
                              </pre>
                            </div>
                            <div className="px-3 py-0.5 bg-surface-container-high text-on-surface-variant flex items-center justify-between font-label-code text-[10px]">
                              <span>AST syntax verified • pytest suite included</span>
                              <span className="text-primary font-medium">Ready</span>
                            </div>
                          </div>
                        )}

                        {/* Task Completed - Download Files Banner */}
                        {generatedFileNames.length > 0 && !isThinking && (
                          <div className="mt-2.5 p-2 px-3 rounded-xl bg-surface-container-low border border-primary/25 shadow-2xs flex flex-wrap items-center justify-between gap-2">
                            <div className="flex items-center gap-1.5">
                              <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                                <span className="material-symbols-outlined text-[13px]">check_circle</span>
                              </span>
                              <span className="text-xs font-semibold text-on-surface">Task Finished:</span>
                              <span className="text-[11px] text-on-surface-variant font-mono">
                                {generatedFileNames.length} file{generatedFileNames.length > 1 ? "s" : ""} generated
                              </span>
                            </div>
                            <div className="flex items-center flex-wrap gap-1.5">
                              {generatedFileNames.map((fname) => (
                                <button
                                  key={fname}
                                  onClick={() => handleDownloadFile(fname, codeFiles?.[fname])}
                                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-surface-container-high hover:bg-surface-container-highest text-primary border border-outline-variant/40 text-xs font-mono font-medium shadow-2xs transition-all hover:scale-[1.02]"
                                  title={`Download ${fname}`}
                                  type="button"
                                >
                                  <span className="material-symbols-outlined text-[13px]">download</span>
                                  <span>Download {fname}</span>
                                </button>
                              ))}
                              {generatedFileNames.length > 1 && (
                                <a
                                  href="http://localhost:8000/api/workspace/download"
                                  download="workspace.zip"
                                  className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary text-on-primary hover:bg-primary-container text-xs font-medium shadow-2xs transition-all hover:scale-[1.02]"
                                  title="Download all workspace files as zip"
                                >
                                  <span className="material-symbols-outlined text-[13px]">folder_zip</span>
                                  <span>Download All (.zip)</span>
                                </a>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Bottom scroll target */}
              <div ref={chatEndRef} />
            </div>

            {/* 3. PINNED CONTEXT & KNOWLEDGE RAIL (RIGHT SIDE) */}
            <aside className="hidden xl:flex flex-col w-68 bg-surface-container-low/90 backdrop-blur-md rounded-l-xl p-2.5 space-y-2 ml-2 sticky top-12 shadow-2xs border-l border-outline-variant/30 max-h-[calc(100vh-4rem)] overflow-y-auto text-xs">
              {/* Rail Header */}
              <div className="flex items-center justify-between pb-1 border-b border-outline-variant/30">
                <div className="flex items-center gap-1">
                  <span className="material-symbols-outlined text-primary text-[16px]">dataset</span>
                  <span className="font-semibold text-on-surface text-xs">
                    Context &amp; Canvas
                  </span>
                </div>
                <span className="px-1.5 py-0.2 rounded-full bg-secondary-fixed text-on-secondary-fixed font-label-badge text-[9px] font-semibold">
                  Live Sync
                </span>
              </div>

              {/* Active Persona Box */}
              <div className="bg-surface-container-lowest rounded-lg p-2 shadow-2xs space-y-1 border border-outline-variant/40">
                <div className="flex items-center justify-between">
                  <span className="font-label-badge text-[9px] uppercase tracking-wider text-on-surface-variant font-bold">
                    Active Agent
                  </span>
                  <span className="material-symbols-outlined text-primary text-[14px]">badge</span>
                </div>
                <p className="font-semibold text-on-surface text-xs">
                  Ola — Python Engineer
                </p>
                <p className="font-label-code text-[10px] text-on-surface-variant">
                  Tools: Search, RAG, Pytest, AST
                </p>
              </div>

              {/* Tab Selector for Code / Execution / Tests */}
              <div className="flex items-center gap-1 p-0.5 bg-surface-container rounded-md border border-outline-variant/50">
                <button
                  onClick={() => setActiveTab("code")}
                  className={`flex-1 py-0.5 px-1.5 rounded text-xs font-medium transition ${
                    activeTab === "code"
                      ? "bg-surface-container-lowest text-primary font-semibold shadow-2xs"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  Code
                </button>
                <button
                  onClick={() => setActiveTab("terminal")}
                  className={`flex-1 py-0.5 px-1.5 rounded text-xs font-medium transition ${
                    activeTab === "terminal"
                      ? "bg-surface-container-lowest text-primary font-semibold shadow-2xs"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  Run
                </button>
                <button
                  onClick={() => setActiveTab("tests")}
                  className={`flex-1 py-0.5 px-1.5 rounded text-xs font-medium transition ${
                    activeTab === "tests"
                      ? "bg-surface-container-lowest text-primary font-semibold shadow-2xs"
                      : "text-on-surface-variant hover:text-on-surface"
                  }`}
                >
                  Tests
                </button>
              </div>

              {/* Live Canvas View Box */}
              <div className="bg-surface-container-lowest rounded-lg p-2 shadow-2xs border border-outline-variant/40 min-h-[160px]">
                {activeTab === "code" && (
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-label-code text-[11px] font-bold text-primary truncate">
                        {selectedFile || "No file selected"}
                      </span>
                      {fileContent && (
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleCopyCode(fileContent)}
                            className="text-[10px] font-mono text-secondary hover:underline"
                          >
                            Copy
                          </button>
                          <button
                            onClick={() => handleDownloadFile(selectedFile || "code.py", fileContent)}
                            className="text-[10px] font-mono text-primary hover:underline flex items-center gap-0.5"
                            title={`Download ${selectedFile || "code.py"}`}
                          >
                            <span className="material-symbols-outlined text-[11px]">download</span>
                            Download
                          </button>
                        </div>
                      )}
                    </div>
                    {fileContent ? (
                      <pre className="p-2 bg-inverse-surface text-inverse-on-surface rounded font-label-code text-xs overflow-x-auto max-h-48 leading-relaxed">
                        <code>{fileContent}</code>
                      </pre>
                    ) : (
                      <div className="text-on-surface-variant/70 text-xs text-center py-7 italic">
                        Select a file to inspect
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "terminal" && (
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant mb-1.5">
                      Subprocess Output
                    </div>
                    {executionOutput ? (
                      <pre className="p-2 bg-inverse-surface text-inverse-on-surface rounded font-label-code text-xs overflow-x-auto max-h-48 whitespace-pre-wrap leading-relaxed">
                        {executionOutput}
                      </pre>
                    ) : (
                      <div className="text-on-surface-variant/70 text-xs text-center py-7 italic">
                        No execution runs yet
                      </div>
                    )}
                  </div>
                )}

                {activeTab === "tests" && (
                  <div>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-on-surface-variant">
                        Pytest Suite
                      </span>
                      {testsPassed !== null && (
                        <span
                          className={`font-label-badge text-[9px] px-1.5 py-0.2 rounded-full font-bold ${
                            testsPassed
                              ? "bg-emerald-950/80 text-emerald-300 border border-emerald-800/50"
                              : "bg-red-950/80 text-red-300 border border-red-800/50"
                          }`}
                        >
                          {testsPassed ? "PASSED" : "FAILED"}
                        </span>
                      )}
                    </div>
                    {testOutput ? (
                      <pre className="p-2 bg-inverse-surface text-inverse-on-surface rounded font-label-code text-xs overflow-x-auto max-h-48 whitespace-pre-wrap leading-relaxed">
                        {testOutput}
                      </pre>
                    ) : (
                      <div className="text-on-surface-variant/70 text-xs text-center py-7 italic">
                        No test results yet
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Context Utilization Gauge */}
              <div className="bg-surface-container-lowest rounded-lg p-2 shadow-2xs space-y-1 border border-outline-variant/40">
                <div className="flex items-center justify-between">
                  <span className="font-label-badge text-[9px] uppercase tracking-wider text-on-surface-variant font-bold">
                    Memory Checkpoint
                  </span>
                  <span className="font-label-code text-[10px] font-bold text-primary">
                    {workspaceFiles.length} files saved
                  </span>
                </div>
                <div className="w-full bg-surface-container-high rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-primary h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(workspaceFiles.length * 20, 100)}%` }}
                  />
                </div>
                <div className="flex items-center justify-between font-label-code text-[10px] text-on-surface-variant">
                  <span>State: {isLoading ? "Processing" : "Idle & Ready"}</span>
                  <span>LangGraph Active</span>
                </div>
              </div>
            </aside>
          </div>

          {/* 4. DOCKED FLOATING BOTTOM COMPOSER */}
          <div
            className={`fixed bottom-0 ${
              isSidebarOpen ? "left-56" : "left-14"
            } right-0 pointer-events-none z-30 flex flex-col items-center px-3 pb-3 transition-all duration-200`}
          >
            <div className="w-full max-w-3xl pointer-events-auto">
              {/* Minimal Elevated Input Capsule */}
              <div className="bg-surface-container-lowest/95 backdrop-blur-2xl rounded-xl shadow-md p-1.5 px-2 border border-outline-variant/50 flex items-center gap-2">
                {/* Textarea Row */}
                <div className="flex-1 px-1">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    disabled={isLoading}
                    className="w-full bg-transparent resize-none outline-none text-xs sm:text-[13px] text-on-surface placeholder:text-on-surface-variant/50 focus:ring-0 leading-relaxed max-h-28 py-1 block"
                    placeholder="Message Ola to build, research, execute, or test Python code..."
                    rows={1}
                  />
                </div>

                {/* Send Action Button */}
                <button
                  onClick={() => handleSendMessage()}
                  disabled={!input.trim() || isLoading}
                  className="w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-primary text-on-primary disabled:bg-surface-container-high disabled:text-on-surface-variant/40 flex items-center justify-center shadow-xs hover:bg-primary-container transition-all flex-shrink-0"
                  title="Send Message"
                  type="button"
                >
                  {isLoading ? (
                    <span className="material-symbols-outlined text-[16px] animate-spin">
                      progress_activity
                    </span>
                  ) : (
                    <span className="material-symbols-outlined text-[16px]">arrow_upward</span>
                  )}
                </button>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
