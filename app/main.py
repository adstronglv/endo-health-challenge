"""
FastAPI web app for the Endo Health Blog Header Generator.
Bonus deliverable: live-hosted web interface.
"""

import asyncio
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Load .env from project root (not CWD)
_project_root = Path(__file__).parent.parent
load_dotenv(_project_root / ".env")

from app.generator import BLOG_PROMPTS, build_prompt, get_client, generate_image, download_image
from app.postprocess import apply_brand_overlay

app = FastAPI(title="Endo Health Blog Header Generator")

STATIC_DIR = Path(__file__).parent / "static"
OUTPUT_DIR = STATIC_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Generation state
generation_state = {
    "running": False,
    "current": 0,
    "total": 0,
    "results": [],
    "errors": [],
}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with blog titles and gallery."""
    # Check for existing generated images
    existing = sorted(OUTPUT_DIR.glob("*_header.webp"))
    images = []
    for img_path in existing:
        idx = int(img_path.stem.split("_")[0]) - 1
        if 0 <= idx < len(BLOG_PROMPTS):
            images.append({
                "title": BLOG_PROMPTS[idx]["title"],
                "path": f"/static/output/{img_path.name}",
                "index": idx + 1,
            })

    return templates.TemplateResponse("index.html", {
        "request": request,
        "blog_entries": BLOG_PROMPTS,
        "images": images,
        "state": generation_state,
    })


@app.post("/generate")
async def start_generation():
    """Start generating all blog header images."""
    if generation_state["running"]:
        return {"error": "Generierung laeuft bereits"}

    generation_state["running"] = True
    generation_state["current"] = 0
    generation_state["total"] = len(BLOG_PROMPTS)
    generation_state["results"] = []
    generation_state["errors"] = []

    asyncio.create_task(_run_generation())
    return {"status": "started", "total": len(BLOG_PROMPTS)}


async def _run_generation():
    """Background task: generate all images."""
    try:
        client = get_client()
        for i, entry in enumerate(BLOG_PROMPTS, 1):
            generation_state["current"] = i
            try:
                prompt = build_prompt(entry)
                image_url = await generate_image(client, prompt)

                raw_path = OUTPUT_DIR / f"{i:02d}_raw.png"
                await download_image(image_url, raw_path)

                final_path = apply_brand_overlay(
                    raw_path,
                    entry["title"],
                    output_path=OUTPUT_DIR / f"{i:02d}_header",
                )

                generation_state["results"].append({
                    "index": i,
                    "title": entry["title"],
                    "path": f"/static/output/{final_path.name}",
                })
            except Exception as e:
                generation_state["errors"].append({
                    "index": i,
                    "title": entry["title"],
                    "error": str(e),
                })
    finally:
        generation_state["running"] = False


@app.get("/api/status")
async def get_status():
    """Get current generation status."""
    return generation_state


@app.get("/api/stream")
async def stream_progress():
    """SSE endpoint for real-time generation progress."""
    async def event_stream():
        last_current = -1
        while True:
            if generation_state["current"] != last_current:
                last_current = generation_state["current"]
                data = json.dumps({
                    "current": generation_state["current"],
                    "total": generation_state["total"],
                    "running": generation_state["running"],
                    "results": generation_state["results"],
                    "errors": generation_state["errors"],
                })
                yield f"data: {data}\n\n"

            if not generation_state["running"] and last_current > 0:
                data = json.dumps({
                    "current": generation_state["current"],
                    "total": generation_state["total"],
                    "running": False,
                    "results": generation_state["results"],
                    "errors": generation_state["errors"],
                    "done": True,
                })
                yield f"data: {data}\n\n"
                break

            await asyncio.sleep(0.5)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
