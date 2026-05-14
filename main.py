from datetime import datetime
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, SQLModel, Session, create_engine, select, delete

from app.scraper import scrape_leaders

DATABASE_URL = "sqlite:///./panthers_leaders.db"
DB_FILE = Path("./panthers_leaders.db")

app = FastAPI(title="Florida Panthers Career Leaders")
app.mount("/static", StaticFiles(directory="static"), name="static")


class Leader(SQLModel, table=True):
    __tablename__ = "leaders"

    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    rank: int
    player_name: str
    value: str
    player_url: Optional[str] = None
    scrape_time: datetime = Field(default_factory=datetime.utcnow)


engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def refresh_leaders() -> int:
    scraped = scrape_leaders()
    leaders = [
        Leader(
            category=item.category,
            rank=item.rank,
            player_name=item.player_name,
            value=item.value,
            player_url=item.player_url,
        )
        for item in scraped
    ]
    with Session(engine) as session:
        session.exec(delete(Leader))
        session.add_all(leaders)
        session.commit()
    return len(leaders)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    if DB_FILE.exists():
        return
    refresh_leaders()


@app.get("/", response_class=FileResponse)
def home() -> FileResponse:
    return FileResponse("static/index.html")


@app.get("/api/leaders", response_model=List[Leader])
def get_leaders() -> List[Leader]:
    with Session(engine) as session:
        leaders = session.exec(select(Leader).order_by(Leader.category, Leader.rank)).all()
        return leaders


@app.get("/api/players")
def get_player_names() -> dict[str, list[str]]:
    with Session(engine) as session:
        results = session.exec(select(Leader.category, Leader.player_name).order_by(Leader.category, Leader.rank)).all()
    categories: dict[str, list[str]] = {}
    for category, player_name in results:
        categories.setdefault(category, [])
        if player_name not in categories[category]:
            categories[category].append(player_name)
    return categories


@app.post("/api/scrape")
def refresh_endpoint() -> JSONResponse:
    try:
        count = refresh_leaders()
        return JSONResponse({"status": "success", "records": count})
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
