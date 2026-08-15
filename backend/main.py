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

@app.get("/api/driverstandings")
async def standings_drivers(season: int = Query(default=current_season, ge=1950)):
    standings = await f1_api.driver_standings(season)
    return standings

@app.get("/api/constructorstandings")
async def standings_constructors(season: int = Query(default=current_season, ge=1950)):
    standings = await f1_api.constructor_standings(season)
    return standings

@app.get("/api/fastestlap")
async def fastest_lap(season: int = Query(default=current_season, ge=1950)):
    fastest = await f1_api.fastest_lap(season)
    return fastest

@app.get("/api/seasonresults")
async def season_results(season: int = Query(default=current_season, ge=1950)):
    results = await f1_api.season_results(season)
    return results

@app.get("/api/seasonqualifying")
async def season_qualifying(season: int = Query(default=current_season, ge=1950)):
    qualifying = await f1_api.season_qualifying(season)
    return qualifying

@app.get("/api/seasonsprint")
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

#async def season_info(
#    season: int = Query(default=current_season, ge=1950),
#    round_: int = Query(default=1, ge=1)
#    ):
#    race_info = await f1_api.race_info(season, round_)
#    return race_info

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")