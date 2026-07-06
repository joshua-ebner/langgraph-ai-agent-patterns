"""FastAPI application for LangGraph pattern demos."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from ui.api.registry import PATTERNS, get_pattern
from ui.api.runner import GraphRunner
from ui.api.schemas import HitlResumeRequest, PatternInfo, RunRequest, RunResponse

runner: GraphRunner | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global runner
    runner = GraphRunner()
    yield
    runner = None


app = FastAPI(title="LangGraph Agent Patterns", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_runner() -> GraphRunner:
    if runner is None:
        raise HTTPException(status_code=503, detail="Graph runner not initialized")
    return runner


@app.get("/api/patterns", response_model=list[PatternInfo])
def list_patterns() -> list[PatternInfo]:
    return PATTERNS


@app.get("/api/patterns/{pattern_id}", response_model=PatternInfo)
def get_pattern_info(pattern_id: str) -> PatternInfo:
    try:
        return get_pattern(pattern_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/patterns/{pattern_id}/run", response_model=RunResponse)
def run_pattern(pattern_id: str, request: RunRequest) -> RunResponse:
    try:
        return get_runner().run(pattern_id, request.inputs)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/patterns/p04/state/{thread_id}", response_model=RunResponse)
def get_hitl_state(thread_id: str) -> RunResponse:
    try:
        return get_runner().get_hitl_state(thread_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/api/patterns/p04/resume", response_model=RunResponse)
def resume_hitl(request: HitlResumeRequest) -> RunResponse:
    try:
        return get_runner().resume_hitl(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


dist_dir = Path(__file__).resolve().parents[1] / "web" / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="web")
