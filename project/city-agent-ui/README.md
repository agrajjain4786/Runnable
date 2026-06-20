# City Agent — Console

A web chat UI for the City Assistant agent (weather + news tools, Mistral via LangChain),
with a live "approve every tool call" console — built so you can host it as a working
AI-agent demo.

```
city-agent-ui/
├── backend/
│   ├── agent_core.py      # tools, LLM, per-session agent + approval gate
│   ├── main.py            # FastAPI app + websocket bridge
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    └── index.html          # single-file chat console (HTML/CSS/JS)
```

## How the approval flow works

The agent runs in a worker thread. When it wants to call `get_weather` or `get_news`,
it sends an `approval_request` over the websocket and **blocks** until your browser
sends back an `approval_response`. That's what lets the "✓ APPROVE / ✕ DENY" card in
the UI actually gate the tool call in real time, the same job `input()` did in the
original CLI script.

## 1. Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in `.env` with your keys:

```
MISTRAL_API_KEY=...
OPENWEATHER_API_KEY=...
TAVILY_API_KEY=...
```

## 2. Run locally

```bash
cd backend
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000**.

## 3. Deploy (free-tier friendly)

Any host that runs a long-lived Python process with websocket support works —
**Render**, **Railway**, or **Fly.io** are the easiest for a project like this.

**Render (quickest):**
1. Push this folder to a GitHub repo.
2. New → Web Service → connect the repo, set root directory to `backend`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add `MISTRAL_API_KEY`, `OPENWEATHER_API_KEY`, `TAVILY_API_KEY` as environment variables.
6. Deploy — Render gives you a public `https://...onrender.com` URL (websockets work over it automatically as `wss://`).

**Railway** and **Fly.io** follow the same shape: same start command, same three env vars.

> Don't deploy to a serverless/static host (Vercel static, GitHub Pages, etc.) — this
> needs a persistent process for the websocket + the blocking agent thread.

## Notes

- Each browser tab/connection gets its own isolated agent + approval state, so multiple
  people can use the demo at once without interfering with each other.
- If a tab disconnects mid-approval, the backend safely unblocks the worker thread
  instead of hanging.
