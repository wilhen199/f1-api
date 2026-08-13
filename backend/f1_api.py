import asyncio
import random
import time

import requests
from pprint import pprint
import pandas as pd

import httpx

BASE_URL = "https://api.jolpi.ca/ergast/f1"
USER_AGENT = "f1-stats/1.0 (Learning project by F1 Stats)"
HEADERS = {"User-Agent": USER_AGENT}


def _fetch(suffix):
    url = f"{BASE_URL}/{suffix}"
    data = None
    resp = requests.get(url, headers=HEADERS)
#    with httpx.AsyncClient(headers=HEADER, follow_redirects=True) as client:
#        resp = client.get(url)
    resp.raise_for_status()
    data = resp.json()
    return data
    

def seasons():
    data = _fetch("seasons?limit=1000")
    items = data["MRData"]["SeasonTable"]["Seasons"]
    list_seasons = []
    for s in items:
        num_season = int(s["season"])
        list_seasons.append(num_season)
    list_seasons.reverse()
    return list_seasons

def races(season):
    data = _fetch(f"{season}/races?limit=1000")
    return data["MRData"]["RaceTable"]["Races"]

def driver_standings(season):
    data = _fetch(f"{season}/driverstandings")
    list_driver_standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]
    return list_driver_standings["DriverStandings"] if list_driver_standings else []
    #pprint(list_driver_standings["DriverStandings"])

def constructor_standings(season):
    data = _fetch(f"{season}/constructorstandings")
    list_teams_standings = data["MRData"]["StandingsTable"]["StandingsLists"][0]
    return list_teams_standings["ConstructorStandings"] if list_teams_standings else []
    #pprint(list_teams_standings["ConstructorStandings"])

def fastest_lap(season):
    data = _fetch(f"{season}/fastest/1/results/")
    return data["MRData"]["RaceTable"]["Races"]
    #pprint(data["MRData"]["RaceTable"]["Races"])

def season_results(season):
    races_by_round = {}
    collected = 0
    offset = 0

    while True:
        data = _fetch(f"{season}/results?limit=100&offset={offset}")
        total = int(data["MRData"]["total"])
        page_count = 0
        races = data["MRData"]["RaceTable"]["Races"]
        if not races: break
        for race in races:
            round = race["round"]
            if round not in races_by_round: races_by_round[round] = {} 
            weekend = races_by_round[round]
            if "Results" not in weekend:
                weekend["Results"] = []
            if "Results" in race:
                drivers = race["Results"]
            else: 
                drivers = []
            page_count += len(drivers)
            
            for driver in drivers:
                weekend["Results"].append(driver)
            
#            for key, value in race.items():
#                if key != "Results" and key != "season":
#                    weekend[key] = value
                    
#           weekend["Results"].extend(drivers)

            #pprint(round)
            #pprint(weekend)
            #pprint(drivers)
        collected += page_count
        if collected >= total or page_count == 0:
            break
        offset += page_count
        
    sorted_round_keys = sorted(races_by_round.keys(), key=int)

    ordered_races = []
    for r in sorted_round_keys:
        ordered_races.append(races_by_round[r])
    
    #pprint(ordered_races)
    export_results(ordered_races)
    return ordered_races


def export_results(ordered_races):
    rows = []

    for round_idx, weekend in enumerate(ordered_races, start=1):
        for driver in weekend.get("Results", []):
            driver_info = driver.get("Driver", {})
            constructor_info = driver.get("Constructor", {})

            item = {
                "Ronda": round_idx,
                "Posición": driver.get("position"),
                "Número": driver.get("number"),
                "Piloto": f"{driver_info.get('givenName', '')} {driver_info.get('familyName', '')}".strip(),
                "Nacionalidad": driver_info.get("nationality"),
                "Escudería": constructor_info.get("name"),
                "Puntos": driver.get("points"),
                "Estado": driver.get("status")
            }
            rows.append(item)
    
    
    df = pd.DataFrame(rows)
    pprint(df)
    #return pd.DataFrame(rows)
    
season_results(2026)