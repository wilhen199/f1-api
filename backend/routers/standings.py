"""API routes for driver and constructor championship standings."""

import asyncio
import json
from pathlib import Path

from fastapi import APIRouter, Query

from backend import f1_api, helpers
from backend.config import CURRENT_SEASON
from backend.data.champions import championship_counts

router = APIRouter(prefix="/api/standings", tags=["standings"])

HOF_FILE = Path(__file__).parent.parent / "data" / "hall_of_fame.json"


@router.get("/drivers")
async def get_driver_standings(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return driver championship standings for the given season."""
    standings = await f1_api.driver_standings(season)
    top_n = await f1_api.driver_top_n(season, [3, 5, 10])
    podiums = top_n[3]
    top5 = top_n[5]
    top10 = top_n[10]
    rows = [
        {
            "position": helpers.parse_position(
                s.get("position") or s.get("positionText")
            ),
            "points": round(float(s.get("points", "0")), 1),
            "wins": s.get("wins", "0"),
            "podiums": podiums.get((s.get("Driver") or {}).get("driverId"), 0),
            "top_5": top5.get((s.get("Driver") or {}).get("driverId"), 0),
            "top_10": top10.get((s.get("Driver") or {}).get("driverId"), 0),
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


@router.get("/hall-of-fame")
async def get_hall_of_fame():
    """Return all world champions with all-time stats, ranked by titles."""
    if not HOF_FILE.exists():
        return {"rows": [], "message": "Run data/build_hof.py first"}

    stats = json.loads(HOF_FILE.read_text(encoding="utf-8"))
    titles = championship_counts()

    rows = []
    for driver_id, entry in stats.items():
        if driver_id not in titles:
            continue
        rows.append(
            {
                "championships": titles[driver_id],
                "points": round(entry["points"], 1),
                "wins": entry["wins"],
                "podiums": entry["podiums"],
                "top5": entry["top5"],
                "top10": entry["top10"],
                "driver": helpers.driver(entry["driver"]),
            }
        )

    rows.sort(
        key=lambda r: (
            -r["championships"],
            -r["wins"],
            -r["podiums"],
            -r["points"],
        )
    )
    for i, r in enumerate(rows, start=1):
        r["position"] = i

    await helpers.resolve_photos([r["driver"] for r in rows], "driver")
    return {"rows": rows}
