from datetime import datetime
from pathlib import Path
import asyncio

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, select

from .db import AsyncSessionLocal, init_db
from .models import Leader
from .schemas import LeaderSchema
from .scraper import scrape_leaders

BASE_PATH = Path(__file__).resolve().parents[1]
TEMPLATES = Jinja2Templates(directory=str(BASE_PATH / "templates"))

app = FastAPI(title="Buffalo Sabres Career Leaders")


async def refresh_leaders() -> int:
    leaders = await asyncio.to_thread(scrape_leaders)

    async with AsyncSessionLocal() as session:
        await session.execute(delete(Leader))
        session.add_all(leaders)
        await session.commit()

    return len(leaders)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()
    await refresh_leaders()


@app.get("/", response_class=HTMLResponse)
async def read_home(request: Request) -> HTMLResponse:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Leader).order_by(Leader.category, Leader.rank))
        rows = result.scalars().all()

    categories = {}
    most_recent = None
    for leader in rows:
        categories.setdefault(leader.category, []).append(leader)
        most_recent = leader.scrape_time

    categories = dict(sorted(categories.items(), key=lambda item: item[0].lower()))

    return TEMPLATES.TemplateResponse(
        "index.html",
        {
            "request": request,
            "categories": categories,
            "updated": most_recent,
        },
    )


@app.get("/api/leaders", response_model=list[LeaderSchema])
async def api_leaders() -> list[LeaderSchema]:
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Leader).order_by(Leader.category, Leader.rank))
        return result.scalars().all()


@app.post("/api/scrape")
async def api_scrape() -> JSONResponse:
    try:
        count = await refresh_leaders()
        return JSONResponse({"status": "success", "records": count})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
