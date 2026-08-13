import asyncio
from pprint import pprint
import httpx

BASE_URL = "https://api.jolpi.ca/ergast/f1"
USER_AGENT = "f1-stats/1.0 (Learning project by F1 Stats)"
HEADERS = {"User-Agent": USER_AGENT}


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

if __name__ == "__main__":
    #pprint(asyncio.run(seasons()))
    #pprint(asyncio.run(races(2022)))
    #pprint(asyncio.run(driver_standings(2026)))
    #pprint(asyncio.run(constructor_standings(2026)))
    #pprint(asyncio.run(fastest_lap(2026)))
    pprint(asyncio.run(season_results(2026)))