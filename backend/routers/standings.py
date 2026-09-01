"""API routes for driver and constructor championship standings."""

import asyncio

import f1_api
import helpers
from config import CURRENT_SEASON
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/standings", tags=["standings"])


@router.get("/drivers")
async def get_driver_standings(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return driver championship standings for the given season."""
    standings = await f1_api.driver_standings(season)
    rows = [
        {
            "position": helpers.parse_position(
                s.get("position") or s.get("positionText")
            ),
            "points": round(float(s.get("points", "0")), 1),
            "wins": s.get("wins", "0"),
            "driver": helpers.driver(s.get("Driver") or {}),
            "team": helpers.team(helpers.constructor(s)),
        }
        for s in standings
    ]

    await asyncio.gather(
        helpers.resolve_photos([r["driver"] for r in rows], "driver"),
        helpers.resolve_photos([r["team"] for r in rows], "team"),
    )

    return {"season": season, "rows": rows}


@router.get("/teams")
async def get_constructor_standings(
    season: int = Query(default=CURRENT_SEASON, ge=1950)
):
    """Return constructor championship standings for the given season."""
    standings = await f1_api.constructor_standings(season)
    if not standings:
        return {
            "season": season,
            "rows": [],
            "message": "The Constructors Championship was not awarded until 1958",
        }
    rows = [
        {
            "position": helpers.parse_position(
                s.get("position") or s.get("positionText")
            ),
            "points": s.get("points", "0"),
            "wins": s.get("wins", "0"),
            "team": helpers.team(s.get("Constructor") or {}),
        }
        for s in standings
    ]

    await asyncio.gather(helpers.resolve_photos([r["team"] for r in rows], "team"))
    return {"season": season, "rows": rows}
