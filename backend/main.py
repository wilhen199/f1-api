from fastapi import FastAPI, Query, HTTPException
import pathlib
import asyncio
from fastapi.staticfiles import StaticFiles 
import f1_api
from datetime import datetime
import images
import helpers


current_season = datetime.now().year

app = FastAPI()
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "frontend"

@app.get("/api/seasons")
async def get_seasons():
    return await f1_api.seasons()

@app.get("/api/races")
async def get_races(season: int = Query(default=current_season, ge=1950)):
    races = await f1_api.races(season)
    return races

@app.get("/api/standings/drivers")
async def standings_drivers(season: int = Query(default=current_season, ge=1950)):
    standings = await f1_api.driver_standings(season)
    rows = [
        {
            "position": s.get("position") or s.get("positionText"),
            "driver": helpers._driver(s.get("Driver") or {}),
            "nationality": (helpers._driver(s.get("Driver") or {})).get("nationality"),
            "points": s.get("points", "0"),
            "wins": s.get("wins", "0"),
            "team": helpers._team(helpers._constructor(s)),
        }
        for s in standings
    ]
    
    await asyncio.gather(
        helpers._resolve_fotos([r["driver"] for r in rows], "driver"),
        helpers._resolve_fotos([r["team"] for r in rows], "team"),
    )
    
    return {"season": season, "rows": rows}

@app.get("/api/standings/teams")
async def standings_teams(season: int = Query(default=current_season, ge=1950)):
    standings = await f1_api.constructor_standings(season)
    rows = [
        {
            "position": s.get("position") or s.get("positionText"),
            "team": helpers._team(s.get("Constructor") or {}),
            "country" : (helpers._team(s.get("Constructor") or {})).get("country"),
            "points": s.get("points", "0"),
            "wins": s.get("wins", "0"),
        }
        for s in standings
    ]
    
    await asyncio.gather(
    helpers._resolve_fotos([r["team"] for r in rows], "team")
    )
    return {"season": season, "rows": rows}

@app.get("/api/fastestlap")
async def fastest_lap(season: int = Query(default=current_season, ge=1950)):
    fastest = await f1_api.fastest_lap(season)
    return fastest

@app.get("/api/results/season")
async def season_results(season: int = Query(default=current_season, ge=1950)):
    results = await f1_api.season_results(season)
    return results

@app.get("/api/results/qualifying")
async def season_qualifying(season: int = Query(default=current_season, ge=1950)):
    qualifying = await f1_api.season_qualifying(season)
    return qualifying

@app.get("/api/results/sprint")
async def season_sprint(season: int = Query(default=current_season, ge=1950)):
    sprint = await f1_api.season_sprint(season)
    return sprint

@app.get("/api/pitstop")
async def pit_stops(
    season: int = Query(default=current_season, ge=1950),
    race: int = Query(..., ge=1)
    ):
    stops = await f1_api.pit_stops(season, race)
    return stops

@app.get("/api/driver/{driverId}")
async def driver_info(
    driverId: str, season: int = Query(default=current_season, ge=1950)
    ):
    standings = await f1_api.driver_standings(season)
    result_driver = next((row for row in standings if (row.get("Driver") or {}).get("driverId", "").lower() == driverId.lower()), None)
    if not result_driver:
        raise HTTPException(404, "Driver not found on that season")
    
    driver = helpers._driver(result_driver.get("Driver") or {})
    team = helpers._team(helpers._constructor(result_driver))
    
    races = await f1_api.season_results(season)
    races_rows = []
    team_items = [team]
    driver_items = [driver]
    for race in races:
        result_race = next((row for row in race.get("Results", []) if (row.get("Driver") or {}).get("driverId", "").lower() == driverId.lower()), None,)
        if not result_race:
            continue
        row_team = helpers._team(result_race.get("Constructor") or {})
        races_rows.append(
            {
                "round": race.get("round"),
                "raceName": race.get("raceName"),
                "date": race.get("date"),
                "position": result_race.get("position"),
                "positionText": result_race.get("positionText"),
                "grid": result_race.get("grid"),
                "laps": result_race.get("laps"),
                "time": (result_race.get("Time") or {}).get("time"),
                "status": result_race.get("status"),
                "points": result_race.get("points"),
                "fastestLap": (result_race.get("FastestLap") or {}).get("Time", {}).get("time"),
                "team": row_team,
                "flag": images.flag_url((race.get("Circuit") or {}).get("Location", {}).get("country"))
            })
        team_items.append(row_team)

    await asyncio.gather(
        helpers._resolve_fotos(driver_items, "driver"),
        helpers._resolve_fotos(team_items, "team"),
    )
    return {
        "season": season,
        "driver": driver,
        "team": team,
        "position": result_driver.get("position") or result_driver.get("positionText"),
        "points": result_driver.get("points", "0"),
        "wins": result_driver.get("wins", "0"),
        "races": races_rows,
    }

@app.get("/api/fastestpitstops")
async def fastest_pit_stops(season: int = Query(default=current_season, ge=1950)):
    fastest = await f1_api.fastest_pit_stops(season)
    return fastest

@app.get("/api/dotd")
async def driver_of_the_day(season: int = Query(default=current_season, ge=2019)):
    dotd = await f1_api.driver_of_the_day(season)
    return dotd

@app.get("/api/results") # Circuit list
async def results_list(
    season: int = Query(default=current_season, ge=1950)):
    races = await f1_api.season_results(season)
    rows = []
    for race in races:
        raw = race.get("Results", [])
        if not raw: continue
        row = {
            "round": race.get("round"),
            "raceName": race.get("raceName"),
            "circuit": race.get("Circuit", {}).get("circuitName"),
            "date": race.get("date"),
            "country": race.get(("Circuit") or {}).get("Location", {}).get("country"),
            "laps": race.get("Results")[0].get("laps"),
            "flag": images.flag_url((race.get("Circuit") or {}).get("Location", {}).get("country")),
        }
        rows.append(row)
    return {"season": season, "rows": rows}


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")