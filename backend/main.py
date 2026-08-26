from fastapi import FastAPI, Query, HTTPException
import pathlib
import asyncio
from fastapi.staticfiles import StaticFiles 
import f1_api
from datetime import datetime
import images
import helpers
from rich.pretty import pprint

current_season = datetime.now().year

app = FastAPI()
FRONTEND_DIR = pathlib.Path(__file__).resolve().parent.parent / "frontend"


#######################
#------ GENERAL ------#
#######################

@app.get("/api/seasons")
async def get_seasons():
    return await f1_api.seasons()

#########################
#------ STANDINGS ------#
#########################

@app.get("/api/standings/drivers")
async def standings_drivers(season: int = Query(default=current_season, ge=1950)):
    standings = await f1_api.driver_standings(season)
    rows = [
        {
            "position": s.get("position") or s.get("positionText"),
            "points": s.get("points", "0"),
            "wins": s.get("wins", "0"),
            "driver": helpers._driver(s.get("Driver") or {}),
            "team": helpers._team(helpers._constructor(s)),
        }
        for s in standings
    ]
    
    await asyncio.gather(
        helpers._resolve_photos([r["driver"] for r in rows], "driver"),
        helpers._resolve_photos([r["team"] for r in rows], "team"),
    )
    
    return {"season": season, "rows": rows}

@app.get("/api/standings/teams")
async def standings_teams(season: int = Query(default=current_season, ge=1950)):
    standings = await f1_api.constructor_standings(season)
    rows = [
        {
            "position": s.get("position") or s.get("positionText"),
            "points": s.get("points", "0"),
            "wins": s.get("wins", "0"),
            "team": helpers._team(s.get("Constructor") or {}),
        }
        for s in standings
    ]
    
    await asyncio.gather(
    helpers._resolve_photos([r["team"] for r in rows], "team")
    )
    return {"season": season, "rows": rows}

#######################
#------ RESULTS ------#
#######################

@app.get("/api/races")
async def get_races(season: int = Query(default=current_season, ge=1950)):
    races = await f1_api.races(season)
    return races

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

    sprint = await f1_api.season_sprint(season)
    sprint_rows = []
    for race in sprint:
        result_race = next((row for row in race.get("SprintResults", []) if (row.get("Driver") or {}).get("driverId", "").lower() == driverId.lower()), None,)
        if not result_race:
            continue
        row_team = helpers._team(result_race.get("Constructor") or {})
        sprint_rows.append(
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
                "flag": images.flag_url((race.get("Circuit") or {}).get("Location", {}).get("country")),
            })
        team_items.append(row_team)


    qualifying = await f1_api.season_qualifying(season)
    quali_rows = []
    for race in qualifying:
        result_race = next((row for row in race.get("QualifyingResults", []) if (row.get("Driver") or {}).get("driverId", "").lower() == driverId.lower()), None,)
        if not result_race:
            continue
        quali_rows.append({
            "round": race.get("round"),
            "raceName": race.get("raceName"),
            "date": race.get("date"),
            "position": result_race.get("position"),
            "Q1": result_race.get("Q1"),
            "Q2": result_race.get("Q2"),
            "Q3": result_race.get("Q3"),
            "team": row_team,
            "flag": images.flag_url((race.get("Circuit") or {}).get("Location", {}).get("country")),
        })
        team_items.append(row_team)
    
    
    
    await asyncio.gather(
        helpers._resolve_photos(driver_items, "driver"),
        helpers._resolve_photos(team_items, "team"),
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

@app.get("/api/team/{teamId}")
async def driver_info(
    teamId: str, season: int = Query(default=current_season, ge=1950)
    ):
    standings = await f1_api.constructor_standings(season)
    result_team = next((row for row in standings if (row.get("Constructor") or {}).get("constructorId", "").lower() == teamId.lower()), None)
    if not result_team:
        raise HTTPException(404, "Team not found on that season")
    
    team = helpers._team(result_team.get("Constructor") or {})
    races = await f1_api.season_results(season)
    races_rows = []
    team_items = [team]
    driver_items = [
        helpers._driver(d.get("Driver") or {})
        for d in await f1_api.driver_standings(season)
        if (d.get("Constructors") or [{}])[0].get("constructorId", "").lower() == teamId.lower()]
    for race in races:
        result_race = [
            row 
            for row in race.get("Results", []) 
            if (row.get("Constructor") or {}).get("constructorId", "").lower() == teamId.lower()
            ]
        if not result_race:
            continue

        row_driver = [{
            "driver": helpers._driver(r.get("Driver") or {}),
            "position": r.get("position"),
            "points": r.get("points"),
            "status": r.get("status"),
        } 
        for r in result_race
        ]
        
        races_rows.append(
            {
                "round": race.get("round"),
                "raceName": race.get("raceName"),
                "flag": images.flag_url((race.get("Circuit") or {}).get("Location", {}).get("country")),
                "date": race.get("date"),
                "drivers": row_driver,
            })

    await asyncio.gather(
        helpers._resolve_photos(driver_items, "driver"),
        helpers._resolve_photos(team_items, "team"),
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

@app.get("/api/results") # Circuit list
async def results_list(
    season: int = Query(default=current_season, ge=1950)):
    races = await f1_api.season_results(season)
    if not races: raise HTTPException(404, "Season not found")
    rows = [
        {
            "round": race.get("round"),
            "raceName": race.get("raceName"),
            "circuit": race.get("Circuit", {}).get("circuitName"),
            "date": race.get("date"),
            "country": race.get(("Circuit") or {}).get("Location", {}).get("country"),
            "laps": race.get("Results")[0].get("laps"),
            "flag": images.flag_url((race.get("Circuit") or {}).get("Location", {}).get("country")),
        }
        for race in races
        if race.get("Results")
    ]
    return {"season": season, "rows": rows}

@app.get("/api/results/race/{round}")
async def race_detail(
    round: int,
    season: int = Query(default=current_season, ge=1950)
    ):
    info = await f1_api.race_info(season, round)
    if not info: raise HTTPException(404, "Race is not found")
    
    driver_items = []
    team_items = []
    
    # RACE RESULT
    results_rows = [{
        "position": result.get("position"),
        "grid": result.get("grid"),
        "laps": result.get("laps"),
        "time": (result.get("Time") or {}).get("time"),
        "points": result.get("points"),
        "status": result.get("status"),
        "fastestLap": (result.get("FastestLap") or {}).get("Time", {}).get("time"),
        "driver": helpers._driver(result.get("Driver") or {}),
        "team": helpers._team(result.get("Constructor") or {}),
    }
    for result in info.get("results", [])]

    # QUALI RESULT
    quali_rows = [{
        "position": quali.get("position"),
        "Q1": quali.get("Q1"),
        "Q2": quali.get("Q2"),
        "Q3": quali.get("Q3"),
        "driver": helpers._driver(quali.get("Driver") or {}),
        "team": helpers._team(quali.get("Constructor") or {}),
    } 
    for quali in info.get("qualifying", [])]
    
    # POLE POTITION
    pole = None
    quali_raw = sorted(info.get("qualifying", []), key=lambda x: int(x.get("position", 0)))
    if quali_raw:
        p1 = quali_raw[0]
        pole = {
            "driver": helpers._driver(p1.get("Driver") or {}),
            "team": helpers._team(p1.get("Constructor") or {}),
            "time": p1.get("Q3") or p1.get("Q2") or p1.get("Q1"),
        }
        driver_items.append(pole["driver"])
        team_items.append(pole["team"])

    # SPRINT RESULT
    sprint_rows = [{
        "position": sprint.get("position"),
        "grid": sprint.get("grid"),
        "laps": sprint.get("laps"),
        "time": (sprint.get("Time") or {}).get("time"),
        "status": sprint.get("status"),
        "points": sprint.get("points"),
        "fastestLap": (sprint.get("FastestLap") or {}).get("Time", {}).get("time"),
        "driver": helpers._driver(sprint.get("Driver") or {}),
        "team": helpers._team(sprint.get("Constructor") or {}),
    }
    for sprint in info.get("sprint", [])]
    

    # FASTEST PIT STOP
    fps_data = await f1_api.fastest_pit_stops(season)
    fps_item = {}
    round_date = info.get("race", []).get("date")
    country = info.get("Circuit", {}).get("Location", {}).get("country")
    for f in fps_data:
        if f.get("meetingEndDate") == round_date or f.get("meetingIsoCountryName") == country:
            fps_item = f
            break

    # DRIVER OF THE DAY
    dotd_data = await f1_api.driver_of_the_day(season)
    dotd_entry = {}
    for d in dotd_data:
        if d.get("meetingEndDate") == round_date:
            dotd_entry = d
            break
    dotd_row = None
    if dotd_entry:
        search_lastname = dotd_entry.get("driverLastName", "").lower()
        dotd_row = [{
            "driver": helpers._driver(r.get("Driver") or {}),
            "team": helpers._team(r.get("Constructor") or {}),
            "percentage": dotd_entry.get("votePercentage"),
        }
        for r in info.get("results", [])
        if (r.get("Driver") or {}).get("familyName", "").lower() == search_lastname]
        if dotd_row:
            driver_items.append(dotd_row[0]["driver"])
            team_items.append(dotd_row[0]["team"])

#    driver_items = [i["driver"] for i in results_rows]
#    team_items = [t["team"] for t in results_rows]
    driver_items.extend([row["driver"] for row in results_rows])
    team_items.extend([row["team"] for row in results_rows])
    driver_items.extend([row["driver"] for row in quali_rows])
    team_items.extend([row["team"] for row in quali_rows])
    driver_items.extend([row["driver"] for row in sprint_rows])
    team_items.extend([row["team"] for row in sprint_rows])


    await asyncio.gather(
        helpers._resolve_photos(driver_items, "driver"),
        helpers._resolve_photos(team_items, "team"),
    )

    return {
        "season": season,
        "has_sprint": bool(info["sprint"]),
        "race": helpers._race(info.get("race", {}), results_rows),
        "results": results_rows,
        "qualifying": quali_rows,
        "sprint": sprint_rows,
        "pole": pole,
        "fastest_pit_stops": {
                "team": fps_item.get("teamName"),
                "time": fps_item.get("displayTime"),  # e.g. "2.17s"
                "pit_box_time": fps_item.get("pitBoxTime"),  # e.g. "2.170"
                "colour": fps_item.get("teamColourCode"),
            } if fps_item else None,
        "driver_of_the_day": dotd_row
    }


######################
#------ AWARDS ------#
######################

@app.get("/api/fastestlap")
async def fastest_lap(season: int = Query(default=current_season, ge=1950)):
    fastest = await f1_api.fastest_lap(season)
    return fastest

@app.get("/api/fastestpitstops")
async def fastest_pit_stops(season: int = Query(default=current_season, ge=1950)):
    fastest = await f1_api.fastest_pit_stops(season)
    return fastest

@app.get("/api/dotd")
async def driver_of_the_day(season: int = Query(default=current_season, ge=2019)):
    dotd = await f1_api.driver_of_the_day(season)
    return dotd

@app.get("/api/pitstop")
async def pit_stops(
    season: int = Query(default=current_season, ge=1950),
    race: int = Query(..., ge=1)
    ):
    stops = await f1_api.pit_stops(season, race)
    return stops

@app.get("/api/awards")
async def awards(season: int = Query(default=current_season, ge=1950)):
    season_data, quali_data, fps_data, dotd_data, sprint_data = await asyncio.gather(
        f1_api.season_results(season), 
        f1_api.season_qualifying(season), 
        f1_api.fastest_pit_stops(season), 
        f1_api.driver_of_the_day(season),
        f1_api.season_sprint(season),)
        
    rows = []
    driver_items = []
    team_items = []

    for race in season_data:
        round_num = race.get("round")
        round_date = race.get("date")
        country = race.get("Circuit", {}).get("Location", {}).get("country")
        races_results = race.get("Results", [])
        laps = races_results[0].get("laps") if races_results else None
        quali_results = next((r for r in quali_data if r.get("round") == round_num), {}).get("QualifyingResults", [])

        top5 = [{
            "driver": helpers._driver(races_results[i].get("Driver") or {}),
            "team": helpers._team(races_results[i].get("Constructor") or {}),
            "grid": races_results[i].get("grid"),
        } for i in range(5)]
        top5_drivers = [t["driver"] for t in top5]

        driver_items.extend(top5_drivers)

        row_team = helpers._team(races_results[0].get("Constructor") or {})
        team_items.append(row_team)

        fps_item = {}
        for f in fps_data:
            if f.get("meetingEndDate") == round_date or f.get("meetingIsoCountryName") == country:
                fps_item = f
                break

        dotd_entry = {}
        for d in dotd_data:
            if d.get("meetingEndDate") == round_date:
                dotd_entry = d
                break
            
        dotd_row = None
        if dotd_entry:
            search_lastname = dotd_entry.get("driverLastName", "").lower()
            for r in races_results:
                driver_raw = r.get("Driver") or {}
                if driver_raw.get("familyName", "").lower() == search_lastname:
                    dotd_row = {
                        "driver": helpers._driver(driver_raw),
                        "team": helpers._team(r.get("Constructor") or {}),
                        "percentage": dotd_entry.get("votePercentage"),
                    }
                    driver_items.append(dotd_row["driver"])
                    team_items.append(dotd_row["team"])
                    break

        sprint_raw = next((r for r in sprint_data if r.get("round") == round_num), {}).get("SprintResults", [])
        if sprint_raw:
            sprint_winner = helpers._driver(sprint_raw[0].get("Driver") or {})
            driver_items.append(sprint_winner)
            team_items.append(helpers._team(sprint_raw[0].get("Constructor") or {}))

        rows.append({
            "round" : round_num,
            "raceName": race.get("raceName"),
            "circuit": race.get("Circuit", {}).get("circuitName"),
            "date": race.get("date"),
            "country": race.get("Circuit", {}).get("Location", {}).get("country"),
            "flag_circuit": images.flag_url((race.get("Circuit") or {}).get("Location", {}).get("country")),
            "laps": laps,
            "winner": top5_drivers[0],
            "team": row_team,
            "sprint_winner": sprint_winner if sprint_raw else None,
            "top_5": top5,
            "pole": quali_results[0] if quali_results else None,
            "driver_of_the_day": dotd_row,
            "fastest_pit_stop": {
                "team": fps_item.get("teamName"),
                "time": fps_item.get("displayTime"),  # e.g. "2.17s"
                "pit_box_time": fps_item.get("pitBoxTime"),  # e.g. "2.170"
                "colour": fps_item.get("teamColourCode"),
            } if fps_item else None,
        })

    await asyncio.gather(
        helpers._resolve_photos(driver_items, "driver"),
        helpers._resolve_photos(team_items, "team"),
    )
    return {"season": season, "rows": rows}

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")