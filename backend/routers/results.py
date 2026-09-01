"""API routes for races, season results, qualifying, sprint, and driver/team/race detail pages."""

import asyncio

import f1_api
import helpers
import images
from config import CURRENT_SEASON
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(prefix="/api", tags=["results"])


@router.get("/races")
async def get_races(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return the list of races for the given season."""
    return await f1_api.races(season)


@router.get("/results/season")
async def get_season_results(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return all race results for the given season."""
    return await f1_api.season_results(season)


@router.get("/results/qualifying")
async def get_season_qualifying(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return all qualifying results for the given season."""
    qualifying = await f1_api.season_qualifying(season)
    if not qualifying:
        return {
            "season": season,
            "rows": [],
            "message": "There is no qualifying data from source",
        }
    return qualifying


@router.get("/results/sprint")
async def get_season_sprint(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return all sprint race results for the given season."""
    return await f1_api.season_sprint(season)


@router.get("/driver/{driver_id}")
async def get_driver_info(
    driver_id: str, season: int = Query(default=CURRENT_SEASON, ge=1950)
):
    """Return full season detail for a specific driver."""
    standings = await f1_api.driver_standings(season)
    result_driver = next(
        (
            row
            for row in standings
            if (row.get("Driver") or {}).get("driverId", "").lower()
            == driver_id.lower()
        ),
        None,
    )
    if not result_driver:
        raise HTTPException(404, "Driver not found on that season")

    driver_data = helpers.driver(result_driver.get("Driver") or {})
    team_data = helpers.team(helpers.constructor(result_driver))

    races_data, sprint_data, qualifying_data = await asyncio.gather(
        f1_api.season_results(season),
        f1_api.season_sprint(season),
        f1_api.season_qualifying(season),
    )

    races_rows, race_teams = helpers.driver_race_rows(races_data, driver_id)
    sprint_rows, sprint_teams = helpers.driver_sprint_rows(sprint_data, driver_id)
    quali_rows, quali_teams = helpers.driver_quali_rows(
        qualifying_data, driver_id, team_data
    )

    await asyncio.gather(
        helpers.resolve_photos([driver_data], "driver"),
        helpers.resolve_photos(
            [team_data] + race_teams + sprint_teams + quali_teams, "team"
        ),
    )
    return {
        "season": season,
        "driver": driver_data,
        "team": team_data,
        "position": helpers.parse_position(
            result_driver.get("position") or result_driver.get("positionText")
        ),
        "points": result_driver.get("points", "0"),
        "wins": result_driver.get("wins", "0"),
        "races": races_rows,
        **({"sprint": sprint_rows} if sprint_data else {}),
        **({"qualifying": quali_rows} if qualifying_data else {}),
    }


@router.get("/team/{team_id}")
async def get_team_info(
    team_id: str, season: int = Query(default=CURRENT_SEASON, ge=1950)
):
    """Return full season detail for a specific constructor."""
    standings, driver_standings, races_data = await asyncio.gather(
        f1_api.constructor_standings(season),
        f1_api.driver_standings(season),
        f1_api.season_results(season),
    )
    result_team = next(
        (
            row
            for row in standings
            if (row.get("Constructor") or {}).get("constructorId", "").lower()
            == team_id.lower()
        ),
        None,
    )
    if not result_team:
        raise HTTPException(404, "Team not found on that season")

    team_data = helpers.team(result_team.get("Constructor") or {})
    driver_items = [
        helpers.driver(d.get("Driver") or {})
        for d in driver_standings
        if (d.get("Constructors") or [{}])[0].get("constructorId", "").lower()
        == team_id.lower()
    ]
    races_rows = helpers.team_race_rows(races_data, team_id)

    await asyncio.gather(
        helpers.resolve_photos(driver_items, "driver"),
        helpers.resolve_photos([team_data], "team"),
    )
    return {
        "season": season,
        "team": team_data,
        "driver": driver_items,
        "position": helpers.parse_position(
            result_team.get("position") or result_team.get("positionText")
        ),
        "points": result_team.get("points", "0"),
        "wins": result_team.get("wins", "0"),
        "races": races_rows,
    }


@router.get("/results")  # Circuit list
async def get_results_list(season: int = Query(default=CURRENT_SEASON, ge=1950)):
    """Return the list of completed races with circuit info for the given season."""
    races = await f1_api.season_results(season)
    if not races:
        raise HTTPException(404, "Season not found")
    rows = [
        {
            "round": race.get("round"),
            "raceName": race.get("raceName"),
            "circuit": race.get("Circuit", {}).get("circuitName"),
            "date": race.get("date"),
            "country": race.get("Circuit").get("Location", {}).get("country"),
            "laps": race.get("Results")[0].get("laps"),
            "flag": images.flag_url(
                (race.get("Circuit") or {}).get("Location", {}).get("country")
            ),
        }
        for race in races
        if race.get("Results")
    ]
    return {"season": season, "rows": rows}


@router.get("/results/race/{round_num}")
async def get_race_detail(
    round_num: int, season: int = Query(default=CURRENT_SEASON, ge=1950)
):
    """Return full detail for a single race including results, qualifying, sprint and awards."""
    info, fps_data, dotd_data = await asyncio.gather(
        f1_api.race_info(season, round_num),
        f1_api.fastest_pit_stops(season),
        f1_api.driver_of_the_day(season),
    )
    if not info:
        raise HTTPException(404, "Race is not found")

    results_rows, quali_rows, sprint_rows = helpers.race_detail_rows(info)
    pole = helpers.find_pole(info.get("qualifying", []))

    round_date = (info.get("race") or {}).get("date")
    fps_item = next((f for f in fps_data if f.get("meetingEndDate") == round_date), {})
    dotd_entry = next(
        (d for d in dotd_data if d.get("meetingEndDate") == round_date), {}
    )
    dotd_row = helpers.find_dotd(info.get("results", []), dotd_entry)

    driver_items = [row["driver"] for row in results_rows + quali_rows + sprint_rows]
    team_items = [row["team"] for row in results_rows + quali_rows + sprint_rows]
    if pole:
        driver_items.append(pole["driver"])
        team_items.append(pole["team"])
    if dotd_row:
        driver_items.append(dotd_row["driver"])
        team_items.append(dotd_row["team"])

    await asyncio.gather(
        helpers.resolve_photos(driver_items, "driver"),
        helpers.resolve_photos(team_items, "team"),
    )
    return {
        "season": season,
        "has_sprint": bool(info["sprint"]),
        "race": helpers.race(info.get("race", {}), results_rows),
        "results": results_rows,
        "qualifying": quali_rows,
        "sprint": sprint_rows,
        "pole": pole,
        "fastest_pit_stops": (
            {
                "team": fps_item.get("teamName"),
                "time": fps_item.get("displayTime"),
                "pit_box_time": fps_item.get("pitBoxTime"),
                "colour": fps_item.get("teamColourCode"),
            }
            if fps_item
            else None
        ),
        "driver_of_the_day": dotd_row,
    }
