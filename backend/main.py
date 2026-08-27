"""FastAPI route handlers for the F1 Stats API."""

import asyncio
import pathlib
from datetime import datetime

import f1_api
import helpers
import images
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles

current_season = datetime.now().year

app = FastAPI()
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "frontend"


#######################
# ------ GENERAL ------#
#######################


@app.get("/api/seasons")
async def get_seasons():
    """Return the list of available F1 seasons."""
    return await f1_api.seasons()


#########################
# ------ STANDINGS ------#
#########################


@app.get("/api/standings/drivers")
async def standings_drivers(season: int = Query(default=current_season, ge=1950)):
    """Return driver championship standings for the given season."""
    standings = await f1_api.driver_standings(season)
    rows = [
        {
            "position": s.get("position") or s.get("positionText"),
            "points": s.get("points", "0"),
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


@app.get("/api/standings/teams")
async def standings_teams(season: int = Query(default=current_season, ge=1950)):
    """Return constructor championship standings for the given season."""
    standings = await f1_api.constructor_standings(season)
    rows = [
        {
            "position": s.get("position") or s.get("positionText"),
            "points": s.get("points", "0"),
            "wins": s.get("wins", "0"),
            "team": helpers.team(s.get("Constructor") or {}),
        }
        for s in standings
    ]

    await asyncio.gather(helpers.resolve_photos([r["team"] for r in rows], "team"))
    return {"season": season, "rows": rows}


#######################
# ------ RESULTS ------#
#######################


@app.get("/api/races")
async def get_races(season: int = Query(default=current_season, ge=1950)):
    """Return the list of races for the given season."""
    races = await f1_api.races(season)
    return races


@app.get("/api/results/season")
async def season_results(season: int = Query(default=current_season, ge=1950)):
    """Return all race results for the given season."""
    results = await f1_api.season_results(season)
    return results


@app.get("/api/results/qualifying")
async def season_qualifying(season: int = Query(default=current_season, ge=1950)):
    """Return all qualifying results for the given season."""
    qualifying = await f1_api.season_qualifying(season)
    return qualifying


@app.get("/api/results/sprint")
async def season_sprint(season: int = Query(default=current_season, ge=1950)):
    """Return all sprint race results for the given season."""
    sprint = await f1_api.season_sprint(season)
    return sprint


@app.get("/api/driver/{driver_id}")
async def driver_info(
    driver_id: str, season: int = Query(default=current_season, ge=1950)
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

    driver = helpers.driver(result_driver.get("Driver") or {})
    team = helpers.team(helpers.constructor(result_driver))

    races_data, sprint_data, qualifying_data = await asyncio.gather(
        f1_api.season_results(season),
        f1_api.season_sprint(season),
        f1_api.season_qualifying(season),
    )

    races_rows, race_teams = helpers.driver_race_rows(races_data, driver_id)
    sprint_rows, sprint_teams = helpers.driver_sprint_rows(sprint_data, driver_id)
    quali_rows, quali_teams = helpers.driver_quali_rows(
        qualifying_data, driver_id, team
    )

    await asyncio.gather(
        helpers.resolve_photos([driver], "driver"),
        helpers.resolve_photos(
            [team] + race_teams + sprint_teams + quali_teams, "team"
        ),
    )
    return {
        "season": season,
        "driver": driver,
        "team": team,
        "position": result_driver.get("position") or result_driver.get("positionText"),
        "points": result_driver.get("points", "0"),
        "wins": result_driver.get("wins", "0"),
        "races": races_rows,
        "sprint": sprint_rows,
        "qualifying": quali_rows,
    }


@app.get("/api/team/{team_id}")
async def team_info(team_id: str, season: int = Query(default=current_season, ge=1950)):
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

    team = helpers.team(result_team.get("Constructor") or {})
    driver_items = [
        helpers.driver(d.get("Driver") or {})
        for d in driver_standings
        if (d.get("Constructors") or [{}])[0].get("constructorId", "").lower()
        == team_id.lower()
    ]
    races_rows = helpers.team_race_rows(races_data, team_id)

    await asyncio.gather(
        helpers.resolve_photos(driver_items, "driver"),
        helpers.resolve_photos([team], "team"),
    )
    return {
        "season": season,
        "team": team,
        "driver": driver_items,
        "position": int(result_team.get("position") or result_team.get("positionText")),
        "points": result_team.get("points", "0"),
        "wins": result_team.get("wins", "0"),
        "races": races_rows,
    }


@app.get("/api/results")  # Circuit list
async def results_list(season: int = Query(default=current_season, ge=1950)):
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
            "country": race.get(("Circuit") or {}).get("Location", {}).get("country"),
            "laps": race.get("Results")[0].get("laps"),
            "flag": images.flag_url(
                (race.get("Circuit") or {}).get("Location", {}).get("country")
            ),
        }
        for race in races
        if race.get("Results")
    ]
    return {"season": season, "rows": rows}


@app.get("/api/results/race/{round_num}")
async def race_detail(
    round_num: int, season: int = Query(default=current_season, ge=1950)
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


######################
# ------ AWARDS ------#
######################


@app.get("/api/fastestlap")
async def fastest_lap(season: int = Query(default=current_season, ge=1950)):
    """Return fastest lap data for the given season."""
    fastest = await f1_api.fastest_lap(season)
    return fastest


@app.get("/api/fastestpitstops")
async def fastest_pit_stops(season: int = Query(default=current_season, ge=1950)):
    """Return fastest pit stop data for the given season."""
    fastest = await f1_api.fastest_pit_stops(season)
    return fastest


@app.get("/api/dotd")
async def driver_of_the_day(season: int = Query(default=current_season, ge=2019)):
    """Return Driver of the Day results for the given season."""
    dotd = await f1_api.driver_of_the_day(season)
    return dotd


@app.get("/api/pitstop")
async def pit_stops(
    season: int = Query(default=current_season, ge=1950), race: int = Query(..., ge=1)
):
    """Return pit stop data for a specific race."""
    stops = await f1_api.pit_stops(season, race)
    return stops


@app.get("/api/awards")
async def awards(season: int = Query(default=current_season, ge=1950)):
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


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
