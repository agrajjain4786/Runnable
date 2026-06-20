"""
FastAPI backend.

Each websocket connection gets its own Session. The agent (LangChain) runs
synchronously in a worker thread (it blocks on tool-approval), while the
websocket coroutine forwards messages between the browser and that thread:

  browser --user_message--> [worker thread runs agent.invoke] --agent_message--> browser
                                        |
                                        v (tool call requested)
  browser <--approval_request-- session.request_approval() [thread blocks here]
  browser --approval_response--> session.resolve_approval() [thread unblocks]
"""

import asyncio
import threading
import uuid
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from agent_core import build_agent

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

app = FastAPI(title="City Agent Console")


class Session:
    """Bridges the sync agent thread and the async websocket loop."""

    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self.out_queue: asyncio.Queue = asyncio.Queue()
        self.approval_event = threading.Event()
        self.approval_decision = False
        self.pending_approval_id = None

    def request_approval(self, tool_name: str, tool_args: dict) -> bool:
        """Called from the worker thread. Blocks until the browser replies."""
        approval_id = str(uuid.uuid4())
        self.pending_approval_id = approval_id
        self.approval_event.clear()

        message = {
            "type": "approval_request",
            "id": approval_id,
            "tool": tool_name,
            "args": tool_args,
        }
        self.loop.call_soon_threadsafe(self.out_queue.put_nowait, message)

        self.approval_event.wait()
        return self.approval_decision

    def resolve_approval(self, approval_id: str, approved: bool) -> None:
        """Called from the websocket coroutine when the browser responds."""
        if approval_id == self.pending_approval_id:
            self.approval_decision = approved
            self.approval_event.set()

    def unblock(self) -> None:
        """Safety valve so a disconnect never leaves the worker thread hung."""
        self.approval_decision = False
        self.approval_event.set()


@app.get("/")
async def index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    session = Session(loop)
    agent = build_agent(session)

    async def writer():
        while True:
            message = await session.out_queue.get()
            await websocket.send_json(message)

    writer_task = asyncio.create_task(writer())

    def run_agent(content: str):
        result = agent.invoke({"messages": [{"role": "user", "content": content}]})
        return result["messages"][-1].content

    try:
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type")

            if msg_type == "user_message":
                content = (data.get("content") or "").strip()
                if not content:
                    continue
                await websocket.send_json({"type": "status", "state": "thinking"})
                try:
                    reply = await loop.run_in_executor(None, run_agent, content)
                except Exception as exc:  # noqa: BLE001
                    reply = f"⚠️ Agent error: {exc}"
                await websocket.send_json({"type": "agent_message", "content": reply})
                await websocket.send_json({"type": "status", "state": "idle"})

            elif msg_type == "approval_response":
                session.resolve_approval(data.get("id"), bool(data.get("approved")))

    except WebSocketDisconnect:
        pass
    finally:
        writer_task.cancel()
        session.unblock()
