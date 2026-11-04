import io
import json
import uuid
import zipfile
from pathlib import Path
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from langgraph.checkpoint.memory import MemorySaver

from agent.graph import builder
from backend.logger import log_agent_event, log_agent_error, LOG_FILE

# Persistent memory for multi-turn threads & Human-in-the-loop interrupts
checkpointer = MemorySaver()
agent_graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["code_generation"]
)

WORKSPACE = (Path(__file__).resolve().parent.parent / "workspace")
WORKSPACE.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Ola AI Code Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    task: str
    thread_id: Optional[str] = None


class ResumeRequest(BaseModel):
    thread_id: str
    action: str  # "approve" | "update" | "reject"
    plan: Optional[list[str]] = None


@app.get("/api/health")
def health_check():
    return {"status": "ok", "workspace": str(WORKSPACE)}


@app.get("/api/workspace/files")
def get_workspace_files():
    """List all user-created files in workspace (ignoring caches)."""
    files = []
    ignored_dirs = {".pytest_cache", "__pycache__", ".git"}

    for item in WORKSPACE.rglob("*"):
        if item.is_file():
            if any(part in ignored_dirs for part in item.parts):
                continue
            rel_path = str(item.relative_to(WORKSPACE))
            files.append({
                "path": rel_path,
                "name": item.name,
                "size": item.stat().st_size,
                "is_test": item.name.startswith("test_") or item.name.endswith("_test.py")
            })
    return {"files": sorted(files, key=lambda f: (f["is_test"], f["name"]))}


@app.get("/api/workspace/file")
def get_workspace_file(path: str = Query(..., description="Relative file path")):
    """Get the contents of a specific file in the workspace."""
    safe_path = (WORKSPACE / path).resolve()
    if not safe_path.is_relative_to(WORKSPACE) or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    content = safe_path.read_text(encoding="utf-8")
    return {
        "path": path,
        "name": safe_path.name,
        "content": content
    }


@app.get("/api/workspace/file/download")
def download_workspace_file(path: str = Query(..., description="Relative file path")):
    """Download a specific workspace file directly as an attachment."""
    safe_path = (WORKSPACE / path).resolve()
    if not safe_path.is_relative_to(WORKSPACE) or not safe_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=safe_path,
        filename=safe_path.name,
        media_type="application/octet-stream"
    )


@app.get("/api/workspace/download")
def download_workspace():
    """Zip the workspace files and return as download."""
    zip_buffer = io.BytesIO()
    ignored_dirs = {".pytest_cache", "__pycache__", ".git"}

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for item in WORKSPACE.rglob("*"):
            if item.is_file():
                if any(part in ignored_dirs for part in item.parts):
                    continue
                rel_path = item.relative_to(WORKSPACE)
                zip_file.write(item, arcname=str(rel_path))

    zip_buffer.seek(0)
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=workspace.zip"}
    )


@app.get("/api/logs")
def get_agent_logs(limit: int = Query(default=100, ge=1, le=1000)):
    """Fetch the latest agent log lines from the persistent log file."""
    if not LOG_FILE.exists():
        return {"logs": [], "total_lines": 0, "log_file": str(LOG_FILE)}

    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    return {
        "logs": [line.rstrip() for line in lines[-limit:]],
        "total_lines": len(lines),
        "log_file": str(LOG_FILE)
    }


@app.get("/api/chat/history")
def get_chat_history(thread_id: str = Query(..., description="Thread ID to retrieve history for")):
    """Get the multi-turn conversation history for a specific thread."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = agent_graph.get_state(config)
    if not snapshot or not snapshot.values:
        return {"thread_id": thread_id, "messages": []}

    return {
        "thread_id": thread_id,
        "messages": snapshot.values.get("chat_history", []),
        "files": snapshot.values.get("files", []),
        "tests_passed": snapshot.values.get("tests_passed")
    }


labels = {
    "router": "Classifying request intent...",
    "chat": "Thinking of reply...",
    "planning": "Creating architectural plan...",
    "research": "Searching documentation & retrieving knowledge (Search & RAG)...",
    "code_generation": "Generating Python code & tests...",
    "save_code": "Writing files to workspace (AST validated)...",
    "execute_code": "Executing application code...",
    "testing_code": "Running pytest test suite...",
    "critique": "Critiquing errors & diagnosing root causes (Meta-Tool)...",
    "retry": "Test failed. Preparing self-correction...",
    "fix_code": "Analyzing errors and fixing code...",
    "conclusion": "Generating task summary with evidence citations..."
}


async def run_resume_stream(thread_id: str, config: dict) -> AsyncGenerator[str, None]:
    """Execute and stream resumed LangGraph nodes."""
    try:
        log_agent_event("RESUME", thread_id, "Resuming paused LangGraph workflow after human approval/action")
        # Immediate running status event for UI
        yield f"event: step\ndata: {json.dumps({'node': 'code_generation', 'label': 'Generating Python code & tests...', 'status': 'running', 'thread_id': thread_id})}\n\n"

        for chunk in agent_graph.stream(None, config=config):
            if "__interrupt__" in chunk:
                log_agent_event("INTERRUPT", thread_id, "Workflow paused again on interrupt")
                break
            for node_name, node_output in chunk.items():
                lbl = labels.get(node_name, f"Executing {node_name}...")
                log_agent_event("NODE_STEP", thread_id, f"Completed node '{node_name}': {lbl}")
                event_data = {
                    "node": node_name,
                    "label": lbl,
                    "output": node_output,
                    "thread_id": thread_id
                }
                yield f"event: step\ndata: {json.dumps(event_data)}\n\n"

        final_snapshot = agent_graph.get_state(config)
        final_state = final_snapshot.values if final_snapshot else {}
        tests_passed = final_state.get("tests_passed")
        log_agent_event("COMPLETE", thread_id, f"Resumed workflow finished successfully. Tests passed: {tests_passed}")

        yield f"event: complete\ndata: {json.dumps({'thread_id': thread_id, 'state': final_state})}\n\n"

    except Exception as e:
        log_agent_error(thread_id, f"Error during resumed workflow: {str(e)}", e)
        yield f"event: error\ndata: {json.dumps({'error': str(e), 'thread_id': thread_id})}\n\n"


def is_affirmative_intent(task: str) -> bool:
    t = task.strip().lower().rstrip(".! ")
    exact_matches = {
        "yes", "ok", "okay", "approve", "approved", "proceed", "go ahead",
        "run", "continue", "y", "sure", "yep", "yeah", "lgtm", "looks good",
        "looks great", "do it", "go for it", "please proceed", "accept"
    }
    if t in exact_matches:
        return True
    return any(t.startswith(w) for w in ["yes", "ok", "okay", "proceed", "approve", "go ahead", "sure", "looks good", "continue"])


def is_negative_intent(task: str) -> bool:
    t = task.strip().lower().rstrip(".! ")
    exact_matches = {"no", "reject", "rejected", "cancel", "stop", "abort", "n", "quit", "halt"}
    if t in exact_matches:
        return True
    return any(t.startswith(w) for w in ["cancel", "abort", "reject", "stop"])


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    thread_id = request.thread_id.strip() if request.thread_id and request.thread_id.strip() else str(uuid.uuid4())
    task = request.task
    config = {"configurable": {"thread_id": thread_id}}

    log_agent_event("REQUEST", thread_id, f"Received user prompt/task: {task[:150]}")

    # Check if thread is currently paused waiting for plan approval
    snapshot = agent_graph.get_state(config)
    is_paused = snapshot and snapshot.next and "code_generation" in snapshot.next

    if is_paused and is_affirmative_intent(task):
        log_agent_event("HUMAN_APPROVAL", thread_id, f"User confirmed plan via chat ('{task}')")
        return StreamingResponse(
            run_resume_stream(thread_id, config),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    if is_paused and is_negative_intent(task):
        log_agent_event("HUMAN_REJECT", thread_id, f"User rejected plan via chat ('{task}')")
        async def cancel_generator():
            yield f"event: reject\ndata: {json.dumps({'thread_id': thread_id, 'message': 'Plan was rejected by user. Task aborted.'})}\n\n"

        return StreamingResponse(
            cancel_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )

    async def event_generator() -> AsyncGenerator[str, None]:
        yield f"event: start\ndata: {json.dumps({'thread_id': thread_id, 'task': task})}\n\n"

        # Retrieve prior conversation history from checkpointed state for this thread
        curr_snapshot = agent_graph.get_state(config)
        prior_history = []
        if curr_snapshot and curr_snapshot.values and "chat_history" in curr_snapshot.values:
            prior_history = list(curr_snapshot.values["chat_history"])

        new_chat_history = prior_history + [{"role": "user", "content": task}]

        initial_state = {
            "task": task,
            "chat_history": new_chat_history,
            "retry_count": 0,
            "step_count": 0,
            "max_steps": 12
        }

        try:
            interrupted = False
            for chunk in agent_graph.stream(initial_state, config=config):
                if "__interrupt__" in chunk:
                    interrupted = True
                    break
                for node_name, node_output in chunk.items():
                    lbl = labels.get(node_name, f"Executing {node_name}...")
                    log_agent_event("NODE_STEP", thread_id, f"Completed node '{node_name}': {lbl}")
                    event_data = {
                        "node": node_name,
                        "label": lbl,
                        "output": node_output,
                        "thread_id": thread_id
                    }
                    yield f"event: step\ndata: {json.dumps(event_data)}\n\n"

            snapshot = agent_graph.get_state(config)
            if interrupted or (snapshot and snapshot.next and "code_generation" in snapshot.next):
                plan = snapshot.values.get("plan", [])
                log_agent_event("INTERRUPT", thread_id, "Paused for Human-in-the-Loop review", {"plan_steps": len(plan)})
                interrupt_data = {
                    "thread_id": thread_id,
                    "node": "code_generation",
                    "plan": plan,
                    "state": snapshot.values
                }
                yield f"event: interrupt\ndata: {json.dumps(interrupt_data)}\n\n"
            else:
                final_state = snapshot.values if snapshot else {}
                log_agent_event("COMPLETE", thread_id, "Task execution finished", {"tests_passed": final_state.get("tests_passed")})
                yield f"event: complete\ndata: {json.dumps({'thread_id': thread_id, 'state': final_state})}\n\n"

        except Exception as e:
            log_agent_error(thread_id, f"Error during execution: {str(e)}", e)
            yield f"event: error\ndata: {json.dumps({'error': str(e), 'thread_id': thread_id})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/chat/resume")
async def resume_endpoint(request: ResumeRequest):
    """Resume execution of an interrupted thread after human approval or plan edits."""
    thread_id = request.thread_id
    config = {"configurable": {"thread_id": thread_id}}

    log_agent_event("RESUME_ACTION", thread_id, f"Received resume action: {request.action}")

    snapshot = agent_graph.get_state(config)
    if not snapshot or not snapshot.values:
        log_agent_error(thread_id, "Resume requested but thread is not active or paused")
        raise HTTPException(
            status_code=400,
            detail=f"Thread '{thread_id}' is not in an active or paused state. Please start a task first."
        )

    if request.action == "reject":
        log_agent_event("HUMAN_REJECT", thread_id, "User rejected plan via action button")
        async def reject_generator():
            yield f"event: reject\ndata: {json.dumps({'thread_id': thread_id, 'message': 'Plan was rejected by user. Task aborted.'})}\n\n"

        return StreamingResponse(
            reject_generator(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache"}
        )

    # If user provided a modified plan, update state before resuming
    if request.action == "update" and request.plan:
        log_agent_event("PLAN_UPDATED", thread_id, "User updated plan steps", {"new_plan_steps": len(request.plan)})
        agent_graph.update_state(config, {"plan": request.plan})

    return StreamingResponse(
        run_resume_stream(thread_id, config),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
