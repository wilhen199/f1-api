"""Tests for helpers.py.

These functions are pure (no network calls), so they don't need
mocking: we just feed them raw-shaped Ergast data and check the
output dict.
"""

import helpers


def test_driver_normalizes_basic_fields():
    """driver() should map raw Ergast keys to our flat dict shape."""
    raw = {
        "driverId": "max_verstappen",
        "code": "VER",
        "givenName": "Max",
        "familyName": "Verstappen",
        "nationality": "Dutch",
        "url": "http://en.wikipedia.org/wiki/Max_Verstappen",
    }

    result = helpers.driver(raw)

    assert result["id"] == "max_verstappen"
    assert result["code"] == "VER"
    assert result["givenName"] == "Max"
    assert result["familyName"] == "Verstappen"
    # "Dutch" is in images.NATIONALITIES, so we expect a real flag URL.
    assert result["flag"] == "https://flagcdn.com/w80/nl.png"


def test_driver_handles_missing_fields():
    """driver() should not raise when the input dict is incomplete."""
    result = helpers.driver({"driverId": "hamilton"})

    assert result["id"] == "hamilton"
    assert result["code"] is None
    assert result["flag"] is None  # no nationality -> no flag


def test_team_normalizes_basic_fields():
    """team() should map raw Ergast Constructor keys to our flat dict shape."""
    raw = {
        "constructorId": "ferrari",
        "name": "Ferrari",
        "nationality": "Italian",
        "url": "http://en.wikipedia.org/wiki/Scuderia_Ferrari",
    }

    result = helpers.team(raw)

    assert result["id"] == "ferrari"
    assert result["name"] == "Ferrari"
    assert result["flag"] == "https://flagcdn.com/w80/it.png"


def test_constructor_reads_singular_key():
    """constructor() should read the 'Constructor' key when present."""
    row = {"Constructor": {"constructorId": "mclaren"}}

    result = helpers.constructor(row)

    assert result["constructorId"] == "mclaren"


def test_constructor_falls_back_to_plural_key():
    """constructor() should fall back to the first item of 'Constructors'."""
    row = {"Constructors": [{"constructorId": "mercedes"}]}

    result = helpers.constructor(row)

    assert result["constructorId"] == "mercedes"


def test_constructor_returns_empty_dict_when_missing():
    """constructor() should return {} instead of raising when no data exists."""
    assert helpers.constructor({}) == {}


def test_parse_position_prefers_position_over_position_text():
    """parse_position() should use 'position' first if it's a valid int."""
    assert helpers.parse_position(pos="3", pos_text="3") == 3


def test_parse_position_falls_back_to_position_text():
    """parse_position() should fall back to positionText when position is invalid (e.g. 'R' for retired)."""
    assert helpers.parse_position(pos="R", pos_text="15") == 15


def test_parse_position_returns_zero_when_nothing_is_valid():
    """parse_position() should return 0 instead of raising when both values are invalid."""
    assert helpers.parse_position(pos="R", pos_text="R") == 0


def test_find_pole_returns_none_for_empty_list():
    """find_pole() should return None when there's no qualifying data."""
    assert helpers.find_pole([]) is None


def test_find_pole_picks_the_p1_driver():
    """find_pole() should pick the qualifying row with position == 1."""
    qualifying = [
        {"position": "2", "Driver": {"driverId": "norris"}, "Q3": "1:10.500"},
        {"position": "1", "Driver": {"driverId": "verstappen"}, "Q3": "1:10.200"},
    ]

    pole = helpers.find_pole(qualifying)

    assert pole["driver"]["id"] == "verstappen"
    assert pole["time"] == "1:10.200"


def test_find_dotd_matches_by_family_name():
    """find_dotd() should match the Driver of the Day entry by last name."""
    results = [
        {
            "Driver": {"driverId": "alonso", "familyName": "Alonso"},
            "Constructor": {"constructorId": "aston_martin"},
        }
    ]
    dotd_entry = {"driverLastName": "Alonso", "votePercentage": "45.2"}

    result = helpers.find_dotd(results, dotd_entry)

    assert result["driver"]["id"] == "alonso"
    assert result["percentage"] == "45.2"


def test_find_dotd_returns_none_when_entry_is_empty():
    """find_dotd() should return None when there's no DOTD entry for that race."""
    assert helpers.find_dotd([{"Driver": {"familyName": "Alonso"}}], {}) is None
