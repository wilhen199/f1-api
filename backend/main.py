from fastapi import FastAPI, Query
import pathlib # para manejar rutas de archivos (frontend/, cache/)
from fastapi.staticfiles import StaticFiles 
import f1_api
from datetime import datetime

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
    driver_info = await f1_api.driver_race_results(driverId)
    return driver_info

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