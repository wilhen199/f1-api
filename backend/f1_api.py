import asyncio
from rich.pretty import pprint
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.jolpi.ca/ergast/f1"
USER_AGENT = "f1-stats/1.0 (F1 Stats learning project)"
HEADERS = {"User-Agent": USER_AGENT}

F1COM_BASE_URL = os.getenv("F1COM_BASE_URL")
F1COM_APIKEY = os.getenv("F1COM_APIKEY")

async def _fetch(suffix):
    url = f"{BASE_URL}/{suffix}"
    data = None
    async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data

async def seasons():
    data = await _fetch("seasons?limit=1000")
    items = data["MRData"]["SeasonTable"]["Seasons"]
    list_seasons = []
    for s in items:
        num_season = int(s["season"])
        list_seasons.append(num_season)
    list_seasons.reverse()
    return list_seasons

async def races(season):
    data = await _fetch(f"{season}/races?limit=1000")
    return data["MRData"]["RaceTable"]["Races"]

async def driver_standings(season):
    data = await _fetch(f"{season}/driverstandings")
    list_driver_standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]
    return list_driver_standings["DriverStandings"] if list_driver_standings else []

async def constructor_standings(season):
    data = await _fetch(f"{season}/constructorstandings")
    list_teams_standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]
    return list_teams_standings["ConstructorStandings"] if list_teams_standings else []

async def fastest_lap(season):
    data = await _fetch(f"{season}/fastest/1/results/")
    return data["MRData"]["RaceTable"]["Races"]

async def season_results(season):
    races_by_round = {}
    collected = 0
    offset = 0
    while True:
        data = await _fetch(f"{season}/results?limit=100&offset={offset}")
        total = int(data["MRData"]["total"])
        page_count = 0
        races = data["MRData"]["RaceTable"]["Races"]
        if not races: break
        for race in races:
            round_number = race["round"]
            if round_number not in races_by_round: races_by_round[round_number] = {} 
            weekend = races_by_round[round_number]
            if "Results" not in weekend:
                weekend["Results"] = []
            if "Results" in race:
                drivers = race["Results"]
            else: 
                drivers = []
            page_count += len(drivers)
            
            weekend["Results"].extend(drivers)

            for key, value in race.items():
                if key != "Results" and key != "season":
                    weekend[key] = value

        collected += page_count
        if collected >= total or page_count == 0:
            break
        offset += page_count

    sorted_round_keys = sorted(races_by_round.keys(), key=int)
    ordered_races = []
    for r in sorted_round_keys:
        ordered_races.append(races_by_round[r])

    return ordered_races

async def season_qualifying(season):
    races_by_round = {}
    collected = 0
    offset = 0
    while True:
        data = await _fetch(f"{season}/qualifying?limit=100&offset={offset}")
        total = int(data["MRData"]["total"])
        page_count = 0
        races = data["MRData"]["RaceTable"]["Races"]
        if not races: break
        for race in races:
            round_number = race["round"]
            if round_number not in races_by_round: races_by_round[round_number] = {} 
            weekend = races_by_round[round_number]
            if "QualifyingResults" not in weekend:
                weekend["QualifyingResults"] = []
            if "QualifyingResults" in race:
                drivers = race["QualifyingResults"]
            else: 
                drivers = []
            page_count += len(drivers)
            
            weekend["QualifyingResults"].extend(drivers)

            for key, value in race.items():
                if key != "QualifyingResults" and key != "season":
                    weekend[key] = value

        collected += page_count
        if collected >= total or page_count == 0:
            break
        offset += page_count

    sorted_round_keys = sorted(races_by_round.keys(), key=int)
    ordered_races = []
    for r in sorted_round_keys:
        ordered_races.append(races_by_round[r])

    return ordered_races

async def season_sprint(season):
    races_by_round = {}
    collected = 0
    offset = 0
    while True:
        data = await _fetch(f"{season}/sprint?limit=100&offset={offset}")
        total = int(data["MRData"]["total"])
        page_count = 0
        races = data["MRData"]["RaceTable"]["Races"]
        if not races: break
        for race in races:
            round_number = race["round"]
            if round_number not in races_by_round: races_by_round[round_number] = {} 
            weekend = races_by_round[round_number]
            if "SprintResults" not in weekend:
                weekend["SprintResults"] = []
            if "SprintResults" in race:
                drivers = race["SprintResults"]
            else: 
                drivers = []
            page_count += len(drivers)
            
            weekend["SprintResults"].extend(drivers)

            for key, value in race.items():
                if key != "SprintResults" and key != "season":
                    weekend[key] = value

        collected += page_count
        if collected >= total or page_count == 0:
            break
        offset += page_count

    sorted_round_keys = sorted(races_by_round.keys(), key=int)
    ordered_races = []
    for r in sorted_round_keys:
        ordered_races.append(races_by_round[r])

    return ordered_races

async def pit_stops(season, race):
    data = await _fetch(f"{season}/{race}/pitstops")
    return data["MRData"]["RaceTable"]["Races"][0]["PitStops"]

async def driver_info(driverId):
    data = await _fetch(f"drivers/{driverId}")
    return data["MRData"]["DriverTable"]["Drivers"][0]

async def driver_race_results(driverId):
    data = await _fetch(f"drivers/{driverId}/results?limit=1000")
    return data["MRData"]["RaceTable"]["Races"]

async def fastest_pit_stops(season):
    #Fastest Pit Stops (DHL Awards, ~2 s). Publish Official F1 website at /en/results/{season}/awards/fastest-pit-stops.

    url = f"{F1COM_BASE_URL}/v2/fom-results/fastest-pit-stops?season={season}"
    try:
        async with httpx.AsyncClient(timeout=20, headers={"User-Agent": USER_AGENT, "apikey": F1COM_APIKEY},) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            rows = (resp.json() or {}).get("fastestPitStops", [])
    except httpx.HTTPError:
        rows = []

    return rows

async def race_info(season, round_):
    #A specific race (results + qualifying + sprint combined).
    async def _one(endpoint): # results / qualifying / sprint
        try:
            data = await _fetch(f"{season}/{round_}/{endpoint}")
            races = data["MRData"]["RaceTable"]["Races"]
            return races[0] if races else None
        except httpx.HTTPError:
            return None

    results, qualifying, sprint = await asyncio.gather(
        _one("results"), _one("qualifying"), _one("sprint")
    )
    return {
        "race": results,
        "results": results.get("Results", []) if results else [],
        "qualifying": qualifying.get("QualifyingResults", []) if qualifying else [],
        "sprint": sprint.get("SprintResults", []) if sprint else [],
    }

async def driver_of_the_day(season):

    url = f"{F1COM_BASE_URL}/v2/fom-results/driver-of-the-day?season={season}"
    try:
        async with httpx.AsyncClient(
            timeout=20,
            headers={"User-Agent": USER_AGENT, "apikey": F1COM_APIKEY},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            rows = (resp.json() or {}).get("driverOfTheDay", [])
    except httpx.HTTPError:
        rows = []

    return rows

if __name__ == "__main__":
    #pprint(asyncio.run(seasons()))
    #pprint(asyncio.run(races(2022)))
    #pprint(asyncio.run(driver_standings(2026)))
    #pprint(asyncio.run(constructor_standings(2026)))
    #pprint(asyncio.run(fastest_lap(2026)))
    #pprint(asyncio.run(season_results(2026)))
    #pprint(asyncio.run(season_qualifying(2026)))
    #pprint(asyncio.run(season_sprint(2026)))
    #pprint(asyncio.run(driver_race_results("hamilton")))
    #pprint((asyncio.run(fastest_pit_stops(2026))))
    #pprint(asyncio.run(race_info(2026, 1)))
    pprint(asyncio.run(driver_of_the_day(2019)))
