from pathlib import Path
from typing import Optional

from fastapi import FastAPI

from app.database import DEFAULT_DB_PATH, init_db
from app.routes import router


def create_app(db_path: Optional[Path] = None) -> FastAPI:
    resolved_path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH
    init_db(resolved_path)

    app = FastAPI(title="TechDesk Mini IT Helpdesk", version="0.2.0")
    app.state.db_path = resolved_path
    app.include_router(router)
    return app


app = create_app()