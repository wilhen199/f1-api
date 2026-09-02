"""Helper functions to normalize and enrich F1 data with photos and flags."""

from backend import images

photo_service = images.PhotoService()


def driver(data):
    """Normalize a raw Ergast Driver object into a flat dict."""
    return {
        "id": data.get("driverId"),
        "permanentNumber": data.get("permanentNumber"),
        "code": data.get("code"),
        "url": data.get("url"),
        "givenName": data.get("givenName"),
        "familyName": data.get("familyName"),
        "dateOfBirth": data.get("dateOfBirth"),
        "nationality": data.get("nationality"),
        "flag": images.flag_url(data.get("nationality")),
        "info": data.get("url"),
    }


def constructor(row):
    """Extract the Constructor dict from a standings or results row."""
    c = row.get("Constructor")
    if not c:
        constructors = row.get("Constructors") or []
        c = constructors[0] if constructors else {}
    return c or {}


def team(data):
    """Normalize a raw Ergast Constructor object into a flat dict."""
    nationality = data.get("nationality")
    return {
        "id": data.get("constructorId"),
        "name": data.get("name"),
        "nationality": data.get("nationality"),
        "flag": images.flag_url(nationality),
        "info": data.get("url"),
    }


def race(data, rows):
    """Normalize a raw Ergast Race object into a flat dict."""
    return {
        "round": data.get("round"),
        "raceName": data.get("raceName"),
        "date": data.get("date"),
        "time": data.get("time"),
        "circuit": data.get("Circuit", {}).get("circuitName"),
        "country": data.get("Circuit", {}).get("Location", {}).get("country"),
        "flag": images.flag_url(
            data.get("Circuit", {}).get("Location", {}).get("country")
        ),
        "laps": (rows[0].get("laps") if rows else None),
    }


async def resolve_photos(items, kind):
    """Resolve and attach a photo URL to each item in the list."""
    for i in items:
        # Official F1
        official = (
            images.photo_driver(i.get("id"))
            if kind == "driver"
            else images.logo_team(i.get("id"))
        )
        if official:
            i["photo"] = official
            continue

        # Wikipedia
        wikipedia = i.get("info")
        if wikipedia:
            result = await photo_service.photo_for_wikipedia_url(wikipedia)
            i["photo"] = result["url"] if result else None
        else:
            i["photo"] = None


def driver_race_rows(races, driver_id):
    """Build race result rows for a driver from season results data."""
    rows, team_items = [], []
    for r in races:
        result = next(
            (
                x
                for x in r.get("Results", [])
                if (x.get("Driver") or {}).get("driverId", "").lower()
                == driver_id.lower()
            ),
            None,
        )
        if not result:
            continue
        row_team = team(result.get("Constructor") or {})
        rows.append(
            {
                "round": r.get("round"),
                "raceName": r.get("raceName"),
                "date": r.get("date"),
                "position": result.get("position"),
                "positionText": result.get("positionText"),
                "grid": result.get("grid"),
                "laps": result.get("laps"),
                "time": (result.get("Time") or {}).get("time"),
                "status": result.get("status"),
                "points": result.get("points"),
                "fastestLap": (result.get("FastestLap") or {})
                .get("Time", {})
                .get("time"),
                "team": row_team,
                "flag": images.flag_url(
                    (r.get("Circuit") or {}).get("Location", {}).get("country")
                ),
            }
        )
        team_items.append(row_team)
    return rows, team_items


def driver_sprint_rows(sprint_data, driver_id):
    """Build sprint result rows for a driver from season sprint data."""
    rows, team_items = [], []
    for s in sprint_data:
        result = next(
            (
                x
                for x in s.get("SprintResults", [])
                if (x.get("Driver") or {}).get("driverId", "").lower()
                == driver_id.lower()
            ),
            None,
        )
        if not result:
            continue
        row_team = team(result.get("Constructor") or {})
        rows.append(
            {
                "round": s.get("round"),
                "raceName": s.get("raceName"),
                "date": s.get("date"),
                "position": result.get("position"),
                "positionText": result.get("positionText"),
                "grid": result.get("grid"),
                "laps": result.get("laps"),
                "time": (result.get("Time") or {}).get("time"),
                "status": result.get("status"),
                "points": result.get("points"),
                "fastestLap": (result.get("FastestLap") or {})
                .get("Time", {})
                .get("time"),
                "team": row_team,
                "flag": images.flag_url(
                    (s.get("Circuit") or {}).get("Location", {}).get("country")
                ),
            }
        )
        team_items.append(row_team)
    return rows, team_items


def driver_quali_rows(qualifying_data, driver_id, fallback_team):
    """Build qualifying result rows for a driver from season qualifying data."""
    rows, team_items = [], []
    for q in qualifying_data:
        result = next(
            (
                x
                for x in q.get("QualifyingResults", [])
                if (x.get("Driver") or {}).get("driverId", "").lower()
                == driver_id.lower()
            ),
            None,
        )
        if not result:
            continue
        rows.append(
            {
                "round": q.get("round"),
                "raceName": q.get("raceName"),
                "date": q.get("date"),
                "position": result.get("position"),
                "Q1": result.get("Q1"),
                "Q2": result.get("Q2"),
                "Q3": result.get("Q3"),
                "team": fallback_team,
                "flag": images.flag_url(
                    (q.get("Circuit") or {}).get("Location", {}).get("country")
                ),
            }
        )
        team_items.append(fallback_team)
    return rows, team_items


def team_race_rows(races, team_id):
    """Build race result rows for a constructor from season results data."""
    rows = []
    for r in races:
        results = [
            x
            for x in r.get("Results", [])
            if (x.get("Constructor") or {}).get("constructorId", "").lower()
            == team_id.lower()
        ]
        if not results:
            continue
        rows.append(
            {
                "round": r.get("round"),
                "raceName": r.get("raceName"),
                "date": r.get("date"),
                "flag": images.flag_url(
                    (r.get("Circuit") or {}).get("Location", {}).get("country")
                ),
                "drivers": [
                    {
                        "driver": driver(x.get("Driver") or {}),
                        "position": x.get("position"),
                        "points": x.get("points"),
                        "status": x.get("status"),
                    }
                    for x in results
                ],
            }
        )
    return rows


def race_detail_rows(info):
    """Build results, qualifying and sprint rows from a race info dict."""
    results_rows = [
        {
            "position": r.get("position"),
            "grid": r.get("grid"),
            "laps": r.get("laps"),
            "time": (r.get("Time") or {}).get("time"),
            "points": r.get("points"),
            "status": r.get("status"),
            "fastestLap": (r.get("FastestLap") or {}).get("Time", {}).get("time"),
            "driver": driver(r.get("Driver") or {}),
            "team": team(r.get("Constructor") or {}),
        }
        for r in info.get("results", [])
    ]
    quali_rows = [
        {
            "position": q.get("position"),
            "Q1": q.get("Q1"),
            "Q2": q.get("Q2"),
            "Q3": q.get("Q3"),
            "driver": driver(q.get("Driver") or {}),
            "team": team(q.get("Constructor") or {}),
        }
        for q in info.get("qualifying", [])
    ]
    sprint_rows = [
        {
            "position": s.get("position"),
            "grid": s.get("grid"),
            "laps": s.get("laps"),
            "time": (s.get("Time") or {}).get("time"),
            "status": s.get("status"),
            "points": s.get("points"),
            "fastestLap": (s.get("FastestLap") or {}).get("Time", {}).get("time"),
            "driver": driver(s.get("Driver") or {}),
            "team": team(s.get("Constructor") or {}),
        }
        for s in info.get("sprint", [])
    ]
    return results_rows, quali_rows, sprint_rows


def find_pole(qualifying):
    """Return pole position dict {driver, team, time} from qualifying list, or None."""
    if not qualifying:
        return None
    p1 = min(qualifying, key=lambda x: int(x.get("position", 0)))
    return {
        "driver": driver(p1.get("Driver") or {}),
        "team": team(p1.get("Constructor") or {}),
        "time": p1.get("Q3") or p1.get("Q2") or p1.get("Q1"),
    }


def find_dotd(results, dotd_entry):
    """Return Driver of the Day dict {driver, team, percentage} or None."""
    if not dotd_entry:
        return None
    lastname = dotd_entry.get("driverLastName", "").lower()
    match = next(
        (
            r
            for r in results
            if (r.get("Driver") or {}).get("familyName", "").lower() == lastname
        ),
        None,
    )
    if not match:
        return None
    return {
        "driver": driver(match.get("Driver") or {}),
        "team": team(match.get("Constructor") or {}),
        "percentage": dotd_entry.get("votePercentage"),
    }


def _awards_top5(races_results):
    """Return (top5 list, row_team) for up to the first 5 finishers."""
    top5 = [
        {
            "driver": driver(r.get("Driver") or {}),
            "team": team(r.get("Constructor") or {}),
            "grid": r.get("grid"),
            "points": r.get("points"),
        }
        for r in races_results[:5]
    ]
    return top5, top5[0]["team"] if top5 else team({})


def _awards_sprint(sprint_data, round_num):
    """Return (sprint_winner driver dict or None, sprint_raw list)."""
    sprint_raw = next((r for r in sprint_data if r.get("round") == round_num), {}).get(
        "SprintResults", []
    )
    sprint_winner = driver(sprint_raw[0].get("Driver") or {}) if sprint_raw else None
    return sprint_winner, sprint_raw


def _awards_pole(quali_results):
    """Return pole dict {driver, time} or None from qualifying results list."""
    pole_raw = quali_results[0] if quali_results else None
    if not pole_raw:
        return None
    return {
        "driver": driver(pole_raw.get("Driver") or {}),
        "time": pole_raw.get("Q3") or pole_raw.get("Q2") or pole_raw.get("Q1"),
    }


def awards_race_row(race_data, quali_data, fps_data, dotd_data, sprint_data):
    """Build a single awards row for one race, returning (row, driver_items, team_items)."""
    round_num = race_data.get("round")
    round_date = race_data.get("date")
    country = race_data.get("Circuit", {}).get("Location", {}).get("country")
    races_results = race_data.get("Results", [])

    quali_results = next(
        (r for r in quali_data if r.get("round") == round_num), {}
    ).get("QualifyingResults", [])
    fps_item = next(
        (
            f
            for f in fps_data
            if f.get("meetingEndDate") == round_date
            or f.get("meetingIsoCountryName") == country
        ),
        {},
    )
    dotd_row = find_dotd(
        races_results,
        next((d for d in dotd_data if d.get("meetingEndDate") == round_date), {}),
    )

    top5, row_team = _awards_top5(races_results)
    sprint_winner, sprint_raw = _awards_sprint(sprint_data, round_num)
    pole = _awards_pole(quali_results)

    driver_items = [t["driver"] for t in top5]
    team_items = [t["team"] for t in top5] + [row_team]
    if dotd_row:
        driver_items.append(dotd_row["driver"])
        team_items.append(dotd_row["team"])
    if sprint_winner:
        driver_items.append(sprint_winner)
        team_items.append(team(sprint_raw[0].get("Constructor") or {}))
    if pole:
        driver_items.append(pole["driver"])

    row = {
        "round": round_num,
        "raceName": race_data.get("raceName"),
        "circuit": race_data.get("Circuit", {}).get("circuitName"),
        "date": round_date,
        "country": country,
        "flag_circuit": images.flag_url(country),
        "laps": races_results[0].get("laps") if races_results else None,
        "winner": top5[0]["driver"],
        "team": row_team,
        "sprint_winner": sprint_winner,
        "top_5": top5,
        "pole": pole,
        "driver_of_the_day": dotd_row,
        "fastest_pit_stop": (
            {
                "team": fps_item.get("teamName"),
                "time": fps_item.get("displayTime"),
                "pit_box_time": fps_item.get("pitBoxTime"),
                "colour": fps_item.get("teamColourCode"),
            }
            if fps_item
            else None
        ),
    }
    return row, driver_items, team_items


def parse_position(pos=None, pos_text=None):
    """Parse a position value from the Ergast API."""
    for val in (pos, pos_text):
        if val is None:
            continue
        try:
            return int(val)
        except (ValueError, TypeError):
            continue
    return 0
