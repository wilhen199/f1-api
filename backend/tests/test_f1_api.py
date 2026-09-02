"""Tests for f1_api.py"""

import asyncio

from backend import f1_api


def reset_f1_api_state():
    """Empty f1_api's cache and locks so tests don't interfere with each other"""
    f1_api.CACHE.clear()
    f1_api.LOCKS.clear()


def test_seasons_returns_years_in_descending_order():
    """seasons() should convert season strings to ints and reverse the order"""
    reset_f1_api_state()

    # This is the fake data our fake _fetch() will return, shaped
    # exactly like the real Ergast API response for this endpoint.
    fake_data = {
        "MRData": {
            "SeasonTable": {
                "Seasons": [
                    {"season": "2023"},
                    {"season": "2024"},
                    {"season": "2025"},
                    {"season": "2026"},
                ]
            }
        }
    }

    async def fake_fetch(suffix):
        """Stand-in for the real _fetch(): returns fake data, no network call."""
        return fake_data

    # Save the real _fetch function in a variable, so we can
    original_fetch = f1_api._fetch

    # Replace it with our fake version.
    f1_api._fetch = fake_fetch

    try:
        # Run the real seasons() function.
        result = asyncio.run(f1_api.seasons())

        # Check the result is what we expect.
        assert result == [2026, 2025, 2024, 2023]
    finally:
        f1_api._fetch = original_fetch


def test_driver_standings_returns_empty_list_when_no_data():
    """driver_standings() should return [] instead of raising when StandingsLists is empty."""
    reset_f1_api_state()

    # StandingsLists containing a single "None" simulates what the
    # Ergast API returns for a season with no standings data yet.
    fake_data = {"MRData": {"StandingsTable": {"StandingsLists": [None]}}}

    async def fake_fetch(suffix):
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.driver_standings(2026))
        assert result == []
    finally:
        f1_api._fetch = original_fetch


def test_races_returns_the_race_list_for_a_season():
    """races() should return the Races list from the raw data, unchanged."""
    reset_f1_api_state()
    fake_races = [{"round": "1", "raceName": "Bahrain Grand Prix"}]
    fake_data = {"MRData": {"RaceTable": {"Races": fake_races}}}

    async def fake_fetch(suffix):
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch
    try:
        result = asyncio.run(f1_api.races(2024))
        assert result == fake_races
    finally:
        f1_api._fetch = original_fetch


def test_constructor_standings():
    """constructor_standings() should return the ConstructorStandings list from the raw data, unchanged."""
    reset_f1_api_state()
    fake_constructor_standings = [
        {"position": "1", "constructorName": "McLaren"},
        {"position": "2", "constructorName": "Mercedes"},
    ]
    fake_data = {
        "MRData": {
            "StandingsTable": {
                "StandingsLists": [{"ConstructorStandings": fake_constructor_standings}]
            }
        }
    }

    async def fake_fetch(suffix):
        assert suffix == "2025/constructorstandings"
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.constructor_standings(2025))
        assert result == fake_constructor_standings
    finally:
        f1_api._fetch = original_fetch


def test_constructor_standings_empty():
    """constructor_standings() should return [] instead of raising when StandingsLists is empty."""

    reset_f1_api_state()

    fake_data = {"MRData": {"StandingsTable": {"StandingsLists": []}}}

    async def fake_fetch(suffix):
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.constructor_standings(2026))
        assert result == []
    finally:
        f1_api._fetch = original_fetch


def test_fastest_lap():
    """fastest_lap() should return the Races list containing fastest lap data for a season."""
    reset_f1_api_state()
    fake_races = [{"round": "1", "FastestLap": {"rank": "1", "lap": "42"}}]
    fake_data = {"MRData": {"RaceTable": {"Races": fake_races}}}

    async def fake_fetch(suffix):
        assert suffix == "2024/fastest/1/results/"
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.fastest_lap(2024))
        assert result == fake_races
    finally:
        f1_api._fetch = original_fetch


def test_season_results_paginated():
    """season_results() should aggregate paginated race results and group them by round."""
    reset_f1_api_state()

    # Page 1 contains 2 results for round 1
    page_1 = {
        "MRData": {
            "total": "3",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "1",
                        "raceName": "Bahrain GP",
                        "Results": [{"position": "1"}, {"position": "2"}],
                    }
                ]
            },
        }
    }

    # Page 2 contains the remaining 1 result for round 1
    page_2 = {
        "MRData": {
            "total": "3",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "1",
                        "raceName": "Bahrain GP",
                        "Results": [{"position": "3"}],
                    }
                ]
            },
        }
    }

    async def fake_fetch(suffix):
        if "offset=0" in suffix:
            return page_1
        elif "offset=2" in suffix:
            return page_2
        return {"MRData": {"total": "0", "RaceTable": {"Races": []}}}

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.season_results(2024))
        # Expected: single race entry for round 1 containing all 3 combined driver results
        assert len(result) == 1
        assert result[0]["round"] == "1"
        assert len(result[0]["Results"]) == 3
    finally:
        f1_api._fetch = original_fetch


def test_season_qualifying():
    """season_qualifying() should aggregate qualifying results grouped by round."""
    reset_f1_api_state()
    fake_data = {
        "MRData": {
            "total": "1",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "1",
                        "raceName": "Bahrain GP",
                        "QualifyingResults": [
                            {"position": "1", "driverId": "verstappen"}
                        ],
                    }
                ]
            },
        }
    }

    async def fake_fetch(suffix):
        assert suffix == "2024/qualifying?limit=100&offset=0"
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.season_qualifying(2024))
        assert len(result) == 1
        assert result[0]["QualifyingResults"][0]["driverId"] == "verstappen"
    finally:
        f1_api._fetch = original_fetch


def test_season_sprint():
    """season_sprint() should aggregate sprint race results grouped by round."""
    reset_f1_api_state()
    fake_data = {
        "MRData": {
            "total": "1",
            "RaceTable": {
                "Races": [
                    {
                        "season": "2024",
                        "round": "5",
                        "raceName": "Chinese GP",
                        "SprintResults": [{"position": "1", "driverId": "verstappen"}],
                    }
                ]
            },
        }
    }

    async def fake_fetch(suffix):
        assert suffix == "2024/sprint?limit=100&offset=0"
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.season_sprint(2024))
        assert len(result) == 1
        assert result[0]["SprintResults"][0]["driverId"] == "verstappen"
    finally:
        f1_api._fetch = original_fetch


def test_pit_stops():
    """pit_stops() should return PitStops list for a specific race round."""
    reset_f1_api_state()
    fake_pit_stops = [{"driverId": "hamilton", "lap": "18", "stop": "1"}]
    fake_data = {
        "MRData": {
            "RaceTable": {
                "Races": [
                    {
                        "round": "1",
                        "PitStops": fake_pit_stops,
                    }
                ]
            }
        }
    }

    async def fake_fetch(suffix):
        assert suffix == "2024/1/pitstops"
        return fake_data

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.pit_stops(2024, 1))
        assert result == fake_pit_stops
    finally:
        f1_api._fetch = original_fetch


def test_race_info_combines_endpoints():
    """race_info() should aggregate results, qualifying, and sprint data for a round."""
    reset_f1_api_state()

    async def fake_fetch(suffix):
        if suffix == "2024/1/results":
            return {
                "MRData": {
                    "RaceTable": {
                        "Races": [
                            {
                                "raceName": "Bahrain GP",
                                "Results": [
                                    {"position": "1", "driverId": "verstappen"}
                                ],
                            }
                        ]
                    }
                }
            }
        elif suffix == "2024/1/qualifying":
            return {
                "MRData": {
                    "RaceTable": {
                        "Races": [
                            {
                                "QualifyingResults": [
                                    {"position": "1", "driverId": "verstappen"}
                                ]
                            }
                        ]
                    }
                }
            }
        elif suffix == "2024/1/sprint":
            # Return empty race list simulating a weekend without a sprint
            return {"MRData": {"RaceTable": {"Races": []}}}
        return {"MRData": {"RaceTable": {"Races": []}}}

    original_fetch = f1_api._fetch
    f1_api._fetch = fake_fetch

    try:
        result = asyncio.run(f1_api.race_info(2024, 1))
        assert result["race"]["raceName"] == "Bahrain GP"
        assert len(result["results"]) == 1
        assert len(result["qualifying"]) == 1
        assert result["sprint"] == []
    finally:
        f1_api._fetch = original_fetch
