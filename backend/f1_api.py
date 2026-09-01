"""Async functions to fetch F1 data from the Ergast API and the official F1 website."""

import asyncio
import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

BASE_URL = "https://api.jolpi.ca/ergast/f1"
USER_AGENT = "f1-stats/1.0 (F1 Stats learning project)"
HEADERS = {"User-Agent": USER_AGENT}

F1COM_BASE_URL = os.getenv("F1COM_BASE_URL")
F1COM_APIKEY = os.getenv("F1COM_APIKEY")

CACHE = {}
CACHE_TTL = 3600
LOCKS = {}


async def _fetch(suffix):
    """Perform a GET request to the Ergast API and return the JSON response."""
    url = f"{BASE_URL}/{suffix}"
    now = time.time()

    """ Check if the data is already in the cache and not expired """
    # STEP 1: fast path, no lock needed if already cached and fresh.
    cached = CACHE.get(url)
    if cached and time.time() - cached["timestamp"] < CACHE_TTL:
        return cached["data"]

    # STEP 2: not cached (or expired). Get/create a lock for this URL.
    if url not in LOCKS:
        LOCKS[url] = asyncio.Lock()
    lock = LOCKS[url]

    async with lock:
        # STEP 3: re-check inside the lock — another request might have
        # already fetched and cached this exact URL while we were waiting.
        cached = CACHE.get(url)
        if cached and time.time() - cached["timestamp"] < CACHE_TTL:
            return cached["data"]

        async with httpx.AsyncClient(headers=HEADERS, follow_redirects=True) as client:
            resp = await client.get(url)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Too many requests to the F1 data provider."
                    f"Please try again after {retry_after} seconds"
                ),
                headers={"Retry-After": retry_after},
            )
        resp.raise_for_status()
        data = resp.json()

        CACHE[url] = {"data": data, "timestamp": now}

        return data


async def seasons():
    """Return all available F1 seasons as a list of integers in descending order."""
    data = await _fetch("seasons?limit=1000")
    items = data["MRData"]["SeasonTable"]["Seasons"]
    list_seasons = []
    for s in items:
        num_season = int(s["season"])
        list_seasons.append(num_season)
    list_seasons.reverse()
    return list_seasons


async def races(season):
    """Return all races for the given season."""
    data = await _fetch(f"{season}/races?limit=1000")
    return data["MRData"]["RaceTable"]["Races"]


async def driver_standings(season):
    """Return the driver championship standings for the given season."""
    data = await _fetch(f"{season}/driverstandings")
    list_driver_standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]
    return list_driver_standings["DriverStandings"] if list_driver_standings else []


async def constructor_standings(season):
    """Return the constructor championship standings for the given season."""
    data = await _fetch(f"{season}/constructorstandings")
    standings_lists = data["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings_lists:
        return []
    list_teams_standings = standings_lists[0]
    return list_teams_standings["ConstructorStandings"] if list_teams_standings else []


async def fastest_lap(season):
    """Return the fastest lap results for each race in the given season."""
    data = await _fetch(f"{season}/fastest/1/results/")
    return data["MRData"]["RaceTable"]["Races"]


async def season_results(season):
    """Return all race results for the given season, paginated and grouped by round."""
    races_by_round = {}
    collected = 0
    offset = 0
    while True:
        data = await _fetch(f"{season}/results?limit=100&offset={offset}")
        total = int(data["MRData"]["total"])
        page_count = 0
        race_list = data["MRData"]["RaceTable"]["Races"]
        if not race_list:
            break
        for race in race_list:
            round_number = race["round"]
            if round_number not in races_by_round:
                races_by_round[round_number] = {}
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
    return [races_by_round[r] for r in sorted_round_keys]


async def season_qualifying(season):
    """Return all qualifying results for the given season, paginated and grouped by round."""
    races_by_round = {}
    collected = 0
    offset = 0
    while True:
        data = await _fetch(f"{season}/qualifying?limit=100&offset={offset}")
        total = int(data["MRData"]["total"])
        page_count = 0
        race_list = data["MRData"]["RaceTable"]["Races"]
        if not race_list:
            break
        for race in race_list:
            round_number = race["round"]
            if round_number not in races_by_round:
                races_by_round[round_number] = {}
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
    return [races_by_round[r] for r in sorted_round_keys]


async def season_sprint(season):
    """Return all sprint race results for the given season, paginated and grouped by round."""
    races_by_round = {}
    collected = 0
    offset = 0
    while True:
        data = await _fetch(f"{season}/sprint?limit=100&offset={offset}")
        total = int(data["MRData"]["total"])
        page_count = 0
        race_list = data["MRData"]["RaceTable"]["Races"]
        if not race_list:
            break
        for race in race_list:
            round_number = race["round"]
            if round_number not in races_by_round:
                races_by_round[round_number] = {}
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
    return [races_by_round[r] for r in sorted_round_keys]


async def pit_stops(season, race):
    """Return all pit stop records for a specific race in the given season."""
    data = await _fetch(f"{season}/{race}/pitstops")
    return data["MRData"]["RaceTable"]["Races"][0]["PitStops"]


async def fastest_pit_stops(season):
    """Return the fastest pit stop records per race for the given season from the official F1 API"""
    # Fastest Pit Stops (DHL Awards, ~2 s).
    # Publish Official F1 website at /en/results/{season}/awards/fastest-pit-stops.

    url = f"{F1COM_BASE_URL}/v2/fom-results/fastest-pit-stops?season={season}"
    try:
        async with httpx.AsyncClient(
            timeout=20,
            headers={"User-Agent": USER_AGENT or "", "apikey": F1COM_APIKEY or ""},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            rows = (resp.json() or {}).get("fastestPitStops", [])
    except httpx.HTTPError:
        rows = []

    return rows


async def race_info(season, round_):
    """Return combined results, qualifying, and sprint data for a specific race."""

    # A specific race (results + qualifying + sprint combined).
    async def _one(endpoint):  # results / qualifying / sprint
        try:
            data = await _fetch(f"{season}/{round_}/{endpoint}")
            race_list = data["MRData"]["RaceTable"]["Races"]
            return race_list[0] if race_list else None
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
    """Return Driver of the Day results for each race in the  season from the official F1 API"""

    url = f"{F1COM_BASE_URL}/v2/fom-results/driver-of-the-day?season={season}"
    try:
        async with httpx.AsyncClient(
            timeout=20,
            headers={"User-Agent": USER_AGENT or "", "apikey": F1COM_APIKEY or ""},
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            rows = (resp.json() or {}).get("driverOfTheDay", [])
    except httpx.HTTPError:
        rows = []

    return rows
