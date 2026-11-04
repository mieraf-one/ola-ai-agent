export interface StepInfo {
  node: string;
  label: string;
  status: "running" | "completed" | "failed";
  output?: any;
}

export interface InterruptState {
  node: string;
  plan: string[];
  threadId?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content?: string;
  steps?: StepInfo[];
  finalState?: any;
  interruptState?: InterruptState;
  isInterrupted?: boolean;
  timestamp: string;
}

export interface WorkspaceFile {
  path: string;
  name: string;
  size: number;
  is_test: boolean;
}
