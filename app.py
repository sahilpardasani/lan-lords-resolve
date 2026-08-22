"""
app.py  --  FastAPI surface for Resolve (Coder 3)

Thin HTTP layer over the run flow. No decision logic here; it calls runtime
(which calls the swappable contract/AI mocks) and reads from mongo_store.

Endpoints:
    GET  /health          -> Mongo + journal status line for the UI
    POST /run             -> execute a full Resolve run, return the result
    GET  /runs/{run_id}   -> replay/export a recorded run from Mongo
    GET  /journal/{run_id}-> the run's journal events in order

Run:  uvicorn app:app --reload --port 8000
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Resolve", version="0.1")

_STATIC = os.path.join(os.path.dirname(__file__), "static")

from resolve import runtime, mongo_store


@app.get("/health")
def health():
    """Status line for the UI (spec §18): MONGODB / journal / contract core."""
    h = mongo_store.health()
    return {
        "mongodb": "ONLINE" if h.get("online") else "OFFLINE",
        "journal_events": h.get("journal_events", 0),
        "replay": h.get("replay", "unavailable"),
        "contract_core": "OPERATIONAL",   # contract never depends on Mongo
    }


@app.post("/run")
def run():
    """Execute a full Resolve run end-to-end and return the outcome."""
    try:
        result = runtime.run()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"run failed: {e}")


@app.get("/runs/{run_id}")
def replay(run_id: str):
    """Reconstruct a recorded run from Mongo (spec §15 replay/export)."""
    export = mongo_store.export_run(run_id)
    if not export["journal_events"]:
        raise HTTPException(status_code=404, detail="run not found")
    return export


@app.get("/journal/{run_id}")
def journal(run_id: str):
    """The run's journal events, in sequence order (the audit trail)."""
    events = mongo_store.list_journal(run_id)
    if not events:
        raise HTTPException(status_code=404, detail="no journal for run")
    return {"run_id": run_id, "count": len(events), "events": events}


@app.get("/audit")
def audit():
    """MongoDB aggregation audit views (spec §21)."""
    return mongo_store.audit_views()


@app.get("/why-blocked/{run_id}")
def why_blocked(run_id: str):
    """Full blocked-decision record from stored events (spec §19)."""
    return mongo_store.why_blocked(run_id)


@app.get("/replay/{run_id}")
def replay_timeline(run_id: str):
    """Ordered replay reconstruction (spec §15)."""
    r = mongo_store.replay_run(run_id)
    if not r["timeline"]:
        raise HTTPException(status_code=404, detail="run not found")
    return r


@app.post("/tamper/{run_id}")
def tamper(run_id: str, sequence: int = 2):
    """Demo-only: corrupt a stored event, then report integrity (spec §20)."""
    mongo_store.connect().journal_events.update_one(
        {"run_id": run_id, "sequence": sequence},
        {"$set": {"payload": {"tampered": True}}})
    return mongo_store.verify_journal_chain(run_id)


@app.get("/")
def root():
    index = os.path.join(_STATIC, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return JSONResponse({"service": "Resolve", "see": ["/health", "/run"]})
