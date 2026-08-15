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

def _race(race):
    return {
        "raceId": race.get("raceId"),
        "season": race.get("season"),
        "round": race.get("round"),
        "url": race.get("url"),
        "raceName": race.get("raceName"),
        "date": race.get("date"),
        "time": race.get("time"),
        "Circuit": {
            "circuitId": race.get("Circuit", {}).get("circuitId"),
            "url": race.get("Circuit", {}).get("url"),
            "circuitName": race.get("Circuit", {}).get("circuitName"),
            "Location": {
                "lat": race.get("Circuit", {}).get("Location", {}).get("lat"),
                "long": race.get("Circuit", {}).get("Location", {}).get("long"),
                "locality": race.get("Circuit", {}).get("Location", {}).get("locality"),
                "country": race.get("Circuit", {}).get("Location", {}).get("country"),
            },
        },
    }

async def _resolve_fotos(items, kind):
    # Official F1
    for i in items:
        i["photo"] = (
            images.photo_driver(i.get("id")) if kind == "driver" else images.logo_team(i.get("id"))
        )