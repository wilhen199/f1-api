"""FastAPI route handlers for the F1 Stats API."""

import pathlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "frontend"

from routers import awards, results, standings

from backend import f1_api

#######################
# ------ GENERAL ------#
#######################

app = FastAPI(title="F1 Stats API")

FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "frontend"

app.include_router(standings.router)
app.include_router(results.router)
app.include_router(awards.router)


@app.get("/api/seasons", tags=["general"])
async def get_seasons():
    """Return the list of available F1 seasons."""
    return await f1_api.seasons()


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
