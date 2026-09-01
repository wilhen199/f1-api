"""API routes for season awards: fastest lap, fastest pit stop, Driver of the Day, and the awards summary."""

import asyncio

import f1_api
import helpers
from config import CURRENT_SEASON
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api", tags=["awards"])


@router.get("/fastestlap")
async def get_fastest_lap(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return fastest lap data for the given season."""
    return await f1_api.fastest_lap(season)


@router.get("/fastestpitstops")
async def get_fastest_pit_stops(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return fastest pit stop data for the given season."""
    return await f1_api.fastest_pit_stops(season)


@router.get("/dotd")
async def get_driver_of_the_day(season: int = Query(default=CURRENT_SEASON, ge=2019)):
    """Return Driver of the Day results for the given season."""
    return await f1_api.driver_of_the_day(season)


@router.get("/pitstop")
async def get_pit_stops(
    season: int = Query(default=CURRENT_SEASON, ge=1950), race: int = Query(..., ge=1)
):
    """Return pit stop data for a specific race."""
    return await f1_api.pit_stops(season, race)


@router.get("/awards")
async def get_awards(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return per-race awards summary (winner, pole, DOTD, fastest pit stop) for the season."""
    season_data, quali_data, fps_data, dotd_data, sprint_data = await asyncio.gather(
        f1_api.season_results(season),
        f1_api.season_qualifying(season),
        f1_api.fastest_pit_stops(season),
        f1_api.driver_of_the_day(season),
        f1_api.season_sprint(season),
    )

    rows, driver_items, team_items = [], [], []
    for race in season_data:
        row, d_items, t_items = helpers.awards_race_row(
            race, quali_data, fps_data, dotd_data, sprint_data
        )
        rows.append(row)
        driver_items.extend(d_items)
        team_items.extend(t_items)

    await asyncio.gather(
        helpers.resolve_photos(driver_items, "driver"),
        helpers.resolve_photos(team_items, "team"),
    )
    return {"season": season, "rows": rows}
