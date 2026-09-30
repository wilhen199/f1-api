import asyncio
import json
import pathlib

import httpx

OUT = pathlib.Path("backend/data/hall_of_fame.json")
OUT.parent.mkdir(parents=True, exist_ok=True)


async def get(url):
    async with httpx.AsyncClient(timeout=30) as c:
        r = await c.get(url, headers={"User-Agent": "f1-stats/1.0"})
        if r.status_code == 200:
            return r.json()
        print(f"  HTTP {r.status_code}, esperando 20s...")
        await asyncio.sleep(20)
        return await get(url)


async def main():
    stats = {}
    for pos in range(1, 11):
        print(f"Posicion {pos}/10...")
        offset = 0
        while True:
            url = f"https://api.jolpi.ca/ergast/f1/results/{pos}.json?limit=1000&offset={offset}"
            data = await get(url)
            races = data["MRData"]["RaceTable"]["Races"]
            if not races:
                break
            n = 0
            for race in races:
                for r in race.get("Results", []):
                    n += 1
                    d = r["Driver"]
                    did = d["driverId"]
                    if did not in stats:
                        stats[did] = {
                            "driver": d,
                            "points": 0.0,
                            "wins": 0,
                            "podiums": 0,
                            "top5": 0,
                            "top10": 0,
                        }
                    s = stats[did]
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
            offset += n
            if n == 0 or offset >= int(data["MRData"]["total"]):
                break
        OUT.write_text(json.dumps(stats, indent=2), encoding="utf-8")
        print(f"  Guardado. {len(stats)} pilotos hasta ahora.")

    print(f"\nListo. {len(stats)} pilotos en {OUT}")


asyncio.run(main())
