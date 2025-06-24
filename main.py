#!/usr/bin/env python3
# main.py
# ---------------------------------------------------------------------
# Schlanker, segmentierter Downloader mit Web‑API & Live‑GUI
# ---------------------------------------------------------------------
import asyncio, math, pathlib, shutil, uuid, yaml, time
from typing import List, Dict, Optional
import aiohttp, aiofiles, uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# ─────────────────────── Konfiguration einlesen ──────────────────────
import shutil

CONFIG_PATH = pathlib.Path.home() / ".config" / "ddl_downloader" / "config.yaml"

# Falls die Datei nicht existiert: Hinweis + Vorlage kopieren (wenn vorhanden)
if not CONFIG_PATH.exists():
    print(f"⚠️  Konfigurationsdatei fehlt: {CONFIG_PATH}")
    fallback = pathlib.Path(__file__).parent / "config.example.yaml"
    if fallback.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(fallback, CONFIG_PATH)
        print("📄 Beispielkonfiguration wurde automatisch kopiert.")
    raise SystemExit("Bitte config.yaml anpassen und erneut starten.")

# Config laden
CFG = yaml.safe_load(CONFIG_PATH.read_text())

DOWNLOAD_DIR = pathlib.Path(CFG.get("download_dir", "downloads")).expanduser()
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

SEGMENT_SIZE = CFG.get("segment_size", 8 * 1024 * 1024)  # 8 MiB
MAX_CONCURRENCY = CFG.get("max_concurrency", 6)
API_KEY = CFG.get("ddownload_api_key", "")
LANG = CFG.get("ui_language", "en")

# ─────────────────────────── Plug‑in‑System ───────────────────────────
import importlib, pkgutil

PLUGIN_REGISTRY = {}


def load_plugins():
    for _, name, _ in pkgutil.iter_modules(["plugins"]):
        mod = importlib.import_module(f"plugins.{name}")
        if hasattr(mod, "match") and hasattr(mod, "resolve"):
            PLUGIN_REGISTRY[name] = mod


def resolve_direct_link(url: str) -> str:
    """
    Iteriert über alle Plug‑ins und gibt ersten gültigen direct‑URL zurück.
    Bei Fehler: HTTPException 400.
    """
    for plugin in PLUGIN_REGISTRY.values():
        if plugin.match(url):
            return plugin.resolve(url, API_KEY)
    raise HTTPException(status_code=400, detail="Kein Plug‑in für diese URL")


load_plugins()

# ───────────────────────── Models / DTOs ──────────────────────────────
class AddJob(BaseModel):
    url: str = Field(..., description="Download‑Link (Seiten‑ oder Direkt‑URL)")
    password: Optional[str] = Field(
        None, description="Archiv‑/Rar‑Passwort (optional)"
    )
    package: Optional[str] = Field(None, description="Paketname (optional)")


class JobStatus(BaseModel):
    id: str
    filename: str
    size: int
    downloaded: int
    speed: float
    eta: Optional[str]
    complete: bool = False
    failed: bool = False
    msg: str = ""


# ────────────────────────── FastAPI‑Setup ─────────────────────────────
from contextlib import asynccontextmanager

active_jobs: Dict[str, JobStatus] = {}
finished_jobs: Dict[str, JobStatus] = {}

ws_clients: List[WebSocket] = []

async def broadcast_updates():
    while True:
        data = {
            "active": [job.model_dump() for job in active_jobs.values()],
            "finished": [job.model_dump() for job in finished_jobs.values()],
        }
        living = []
        for ws in ws_clients:
            try:
                await ws.send_json(data)
                living.append(ws)
            except WebSocketDisconnect:
                pass
        ws_clients[:] = living
        await asyncio.sleep(1)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(broadcast_updates())
    yield  # optional shutdown logic here

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/api/add", response_model=JobStatus)
async def api_add(job: AddJob):
    direct_url = resolve_direct_link(job.url)
    job_id = uuid.uuid4().hex
    status = JobStatus(
        id=job_id,
        filename="...",
        size=0,
        downloaded=0,
        speed=0.0,
        eta=None,
        complete=False,
    )
    active_jobs[job_id] = status
    asyncio.create_task(download_worker(job_id, direct_url, job.password))
    return status


@app.get("/api/downloads")
def api_all():
    return {
        "active": [j.model_dump() for j in active_jobs.values()],
        "finished": [j.model_dump() for j in finished_jobs.values()],
    }


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    ws_clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # Ping/Pong o. Ä.
    except WebSocketDisconnect:
        ws_clients.remove(ws)


@app.get("/{file_path:path}")
def serve_file(file_path: str):
    fp = DOWNLOAD_DIR / file_path
    if fp.exists():
        return FileResponse(fp)
    raise HTTPException(404, "Datei nicht gefunden")


# ───────────────────── Segmentierter Downloader ──────────────────────
async def download_worker(job_id: str, url: str, password: str | None):
    session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=300)
    async with aiohttp.ClientSession(timeout=session_timeout) as session:
        # HEAD – Dateigröße ermitteln
        async with session.head(url, allow_redirects=True) as r:
            size = int(r.headers.get("Content-Length", "0"))
            filename = (
                pathlib.Path(r.url.path).name or f"{job_id}.bin"
            )  # Fallback Name
        status = active_jobs[job_id]
        status.filename = filename
        status.size = size

        parts = math.ceil(size / SEGMENT_SIZE)
        sem = asyncio.Semaphore(MAX_CONCURRENCY)
        part_files = []

        async def fetch_part(idx: int, start: int, end: int):
            nonlocal part_files
            headers = {"Range": f"bytes={start}-{end}"}
            tmp_path = DOWNLOAD_DIR / f".{filename}.part{idx:04d}"
            part_files.append(tmp_path)
            async with sem:
                async with session.get(url, headers=headers) as resp:
                    if resp.status not in (200, 206):
                        raise IOError(f"Status {resp.status} für Segment {idx}")
                    async with aiofiles.open(tmp_path, "wb") as f:
                        async for chunk in resp.content.iter_chunked(128 * 1024):
                            await f.write(chunk)
                            status.downloaded += len(chunk)

        tasks = []
        offset = 0
        for idx in range(parts):
            start = offset
            end = min(offset + SEGMENT_SIZE - 1, size - 1)
            tasks.append(asyncio.create_task(fetch_part(idx, start, end)))
            offset += SEGMENT_SIZE

        # Geschwindigkeit / ETA ermitteln
        start_time = time.perf_counter()
        while any(not t.done() for t in tasks):
            await asyncio.sleep(1)
            elapsed = time.perf_counter() - start_time
            status.speed = status.downloaded / elapsed
            remaining = size - status.downloaded
            status.eta = (
                f"{int(remaining / status.speed)} s"
                if status.speed > 0
                else "–"
            )

        # Prüfen auf Fehler
        if any(t.exception() for t in tasks):
            status.failed = True
            status.msg = "; ".join(
                str(t.exception()) for t in tasks if t.exception()
            )
            finished_jobs[job_id] = status
            active_jobs.pop(job_id, None)
            return

        # Zusammenführen
        final_path = DOWNLOAD_DIR / filename
        with open(final_path, "wb") as dest:
            for pf in sorted(part_files):
                with open(pf, "rb") as src:
                    shutil.copyfileobj(src, dest)
                pf.unlink(missing_ok=True)

        status.complete = True
        status.downloaded = size
        status.speed = size / max(1e-3, time.perf_counter() - start_time)
        status.eta = "0"
        finished_jobs[job_id] = status
        active_jobs.pop(job_id, None)


# ────────────────────────────── Runner ────────────────────────────────
if __name__ == "__main__":
    uvicorn.run("main:app", host=CFG.get("listen_host", "0.0.0.0"), port=CFG.get("listen_port", 8000))

