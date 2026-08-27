"""Helper functions to normalize and enrich F1 data with photos and flags."""

import images

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
