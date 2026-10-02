import asyncio
import json
import pathlib
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

OUT_DRIVERS = pathlib.Path("backend/data/hall_of_fame.json")
OUT_TEAMS = pathlib.Path("backend/data/hall_of_fame_teams.json")
OUT_DRIVERS.parent.mkdir(parents=True, exist_ok=True)

CURRENT_SEASON = datetime.now(ZoneInfo("America/Bogota")).year


async def get(url):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url, headers={"User-Agent": "f1-stats/1.0"})
        if r.status_code == 200:
            return r.json()
        print(f"  HTTP {r.status_code}, waiting 20s...")
        await asyncio.sleep(20)
        return await get(url)


async def main():
    driver_stats = {}
    team_stats = {}
    for pos in range(1, 11):
        print(f"Position {pos}/10...")
        offset = 0
        while True:
            url = f"https://api.jolpi.ca/ergast/f1/results/{pos}.json?limit=1000&offset={offset}"
            data = await get(url)
            races = data["MRData"]["RaceTable"]["Races"]
            if not races:
                break
            results = 0
            for race in races:
                for r in race.get("Results", []):
                    results += 1

                    # Drivers
                    driver = r["Driver"]
                    driver_id = driver["driverId"]
                    if driver_id not in driver_stats:
                        driver_stats[driver_id] = {
                            "driver": driver,
                            "points": 0.0,
                            "wins": 0,
                            "podiums": 0,
                            "top5": 0,
                            "top10": 0,
                        }
                    s = driver_stats[driver_id]
                    try:
                        s["points"] += float(r.get("points", 0))
                    except (TypeError, ValueError):
                        pass
                    if pos == 1:
                        s["wins"] += 1
                    if pos <= 3:
                        s["podiums"] += 1
                    if pos <= 5:
                        s["top5"] += 1
                    s["top10"] += 1

                    # Constructors
                    constructor = r.get("Constructor")
                    const_id = constructor["constructorId"]
                    if const_id not in team_stats:
                        team_stats[const_id] = {
                            "constructor": constructor,
                            "points": 0.0,
                            "wins": 0,
                            "podiums": 0,
                        }
                    ts = team_stats[const_id]
                    try:
                        ts["points"] += float(r.get("points", 0))
                    except (TypeError, ValueError):
                        pass
                    if pos == 1:
                        ts["wins"] += 1
                    if pos <= 3:
                        ts["podiums"] += 1
            offset += results
            if results == 0 or offset >= int(data["MRData"]["total"]):
                break
        print(f"  → {len(driver_stats)} Drivers, {len(team_stats)} Constructors")

    # --- Driver Championships --- #
    print("\nDriver Championships...")
    driver_years = {}
    for year in range(1950, CURRENT_SEASON):
        try:
            data = await get(
                f"https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json"
            )
            lists = data["MRData"]["StandingsTable"]["StandingsLists"]
            if lists and lists[0].get("DriverStandings"):
                driver_id = lists[0].get("DriverStandings")[0]["Driver"]["driverId"]
                driver_years.setdefault(driver_id, []).append(year)
        except (KeyError, IndexError) as e:
            print(f"  {year}: error {e}")

    # --- Constructor Championships --- #
    print("\nConstructor Championships...")
    team_years = {}
    for year in range(1950, CURRENT_SEASON):
        try:
            data = await get(
                f"https://api.jolpi.ca/ergast/f1/{year}/constructorstandings.json"
            )
            lists = data["MRData"]["StandingsTable"]["StandingsLists"]
            if lists and lists[0].get("ConstructorStandings"):
                const_id = lists[0].get("ConstructorStandings")[0]["Constructor"][
                    "constructorId"
                ]
                team_years.setdefault(const_id, []).append(year)
        except (KeyError, IndexError) as e:
            print(f"  {year}: error {e}")

    for driver_id, years in driver_years.items():
        if driver_id in driver_stats:
            driver_stats[driver_id]["championships"] = len(years)
            driver_stats[driver_id]["seasons"] = sorted(years)
        # else:
        #    print(f"  WARNING driver: {driver_id} campeón pero sin stats")

    for const_id, years in team_years.items():
        if const_id in team_stats:
            team_stats[const_id]["championships"] = len(years)
            team_stats[const_id]["seasons"] = sorted(years)
        # else:
        #    print(f"  AVISO equipo: {cid} campeón pero sin stats")

    OUT_DRIVERS.write_text(json.dumps(driver_stats), encoding="utf-8")
    OUT_TEAMS.write_text(json.dumps(team_stats, indent=2), encoding="utf-8")
    print(f"\nDone: {len(driver_stats)} drivers, {len(team_stats)} teams")
    print(f"  → {OUT_DRIVERS}")
    print(f"  → {OUT_TEAMS}")


asyncio.run(main())
