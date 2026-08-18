import images

def _driver(driver):
    return {
        "id": driver.get("driverId"),
        "permanentNumber": driver.get("permanentNumber"),
        "code": driver.get("code"),
        "url": driver.get("url"),
        "givenName": driver.get("givenName"),
        "familyName": driver.get("familyName"),
        "dateOfBirth": driver.get("dateOfBirth"),
        "nationality": driver.get("nationality"),
        "flag": images.flag_url(driver.get("nationality")),
        "url": driver.get("url"),
    
    }

def _constructor(row):
    c = row.get("Constructor")
    if not c:
        constructors = row.get("Constructors") or []
        c = constructors[0] if constructors else {}
    return c or {}

def _team(team):
    nationality = team.get("nationality")
    return {
        "id": team.get("constructorId"),
        "name": team.get("name"),
        "nationality": team.get("nationality"),
        "flag": images.flag_url(nationality),
        "info": team.get("url")
    }

def _race(race, rows):
    return {
        "round": race.get("round"),
        "raceName": race.get("raceName"),
        "date": race.get("date"),
        "time": race.get("time"),
        "circuit": race.get("Circuit", {}).get("circuitName"),
        "country": race.get("Circuit", {}).get("Location", {}).get("country"),
        "flag": images.flag_url(race.get("Circuit", {}).get("Location", {}).get("country")),
        "laps": (rows[0].get("laps") if rows else None)
    }

async def _resolve_fotos(items, kind):
    # Official F1
    for i in items:
        i["photo"] = (
            images.photo_driver(i.get("id")) if kind == "driver" else images.logo_team(i.get("id"))
        )