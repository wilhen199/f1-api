"""Images: flags and driver/team photos.

1. Country and nationality flags  -> flagcdn.com
2. Driver and tems photos
   - The OFFICIAL photo for the current season (from F1 web).
   - If no official photos is available (e.g. for drivers from past season),
     is used photo from the driver'sor team's Wikipedia page.
"""

import asyncio
import json
import pathlib
import urllib.parse

import httpx
from datetime import datetime 

# 1) FLAGS
COUNTRIES = {
    "Australia": "au",
    "Austria": "at",
    "Azerbaijan": "az",
    "Bahrain": "bh",
    "Belgium": "be",
    "Brazil": "br",
    "Canada": "ca",
    "China": "cn",
    "Colombia": "co",
    "Czech Republic": "cz",
    "Denmark": "dk",
    "France": "fr",
    "Germany": "de",
    "Hungary": "hu",
    "India": "in",
    "Indonesia": "id",
    "Italy": "it",
    "Japan": "jp",
    "Korea": "kr",
    "Luxembourg": "lu",
    "Malaysia": "my",
    "Mexico": "mx",
    "Monaco": "mc",
    "Morocco": "ma",
    "Netherlands": "nl",
    "Portugal": "pt",
    "Qatar": "qa",
    "Russia": "ru",
    "San Marino": "sm",
    "Saudi Arabia": "sa",
    "Singapore": "sg",
    "South Africa": "za",
    "Spain": "es",
    "Sweden": "se",
    "Switzerland": "ch",
    "Thailand": "th",
    "Turkey": "tr",
    "UAE": "ae",
    "UK": "gb",
    "USA": "us",
    "United States": "us",
    "Vietnam": "vn",
}

NATIONALITIES = {
    "American": "us",
    "Argentine": "ar",
    "Australian": "au",
    "Austrian": "at",
    "Belgian": "be",
    "Brazilian": "br",
    "British": "gb",
    "Canadian": "ca",
    "Chilean": "cl",
    "Chinese": "cn",
    "Colombian": "co",
    "Czech": "cz",
    "Danish": "dk",
    "Dutch": "nl",
    "Finnish": "fi",
    "French": "fr",
    "German": "de",
    "Hungarian": "hu",
    "Indian": "in",
    "Indonesian": "id",
    "Irish": "ie",
    "Italian": "it",
    "Japanese": "jp",
    "Malaysian": "my",
    "Mexican": "mx",
    "Monegasque": "mc",
    "Moroccan": "ma",
    "New Zealander": "nz",
    "Polish": "pl",
    "Portuguese": "pt",
    "Rhodesian": "zw",
    "Russian": "ru",
    "South African": "za",
    "Spanish": "es",
    "Swedish": "se",
    "Swiss": "ch",
    "Thai": "th",
    "Uruguayan": "uy",
    "Venezuelan": "ve",
}

UNKNOWN_CODE = "xx"

SIZE = "w80"

def flag_url(name):
    if not name:
        return None
    code = COUNTRIES.get(name) or NATIONALITIES.get(name) or UNKNOWN_CODE
    return f"https://flagcdn.com/{SIZE}/{code}.png"


# 2) Official photos 
"""
Website https://www.formula1.com publishes the season's photos at 
media.formula1.com. The URL follow this format:
  .../common/f1/2026/{equipo}/{codigo}/2026{equipo}{codigo}right.webp
For each SEASON, items must be updated:
  - SEASON  -> the current year
  - VERSION    -> files version used by F1 website
  - TEAMS    -> Teams racing this season
  - DRIVERS    -> Drivers racing this season
"""

SEASON = datetime.now().year
VERSION = "v1740000001"  # version de los archivos en la web de F1

TEAMS = {
    "alpine": "alpine",
    "aston_martin": "astonmartin",
    "audi": "audi",
    "cadillac": "cadillac",
    "ferrari": "ferrari",
    "haas": "haasf1team",
    "mclaren": "mclaren",
    "mercedes": "mercedes",
    "rb": "racingbulls",
    "red_bull": "redbullracing",
    "williams": "williams",
}

DRIVERS = {
    "antonelli": ("mercedes", "andant01"),
    "hamilton": ("ferrari", "lewham01"),
    "russell": ("mercedes", "georus01"),
    "leclerc": ("ferrari", "chalec01"),
    "norris": ("mclaren", "lannor01"),
    "max_verstappen": ("red_bull", "maxver01"),
    "piastri": ("mclaren", "oscpia01"),
    "hadjar": ("red_bull", "isahad01"),
    "lawson": ("rb", "lialaw01"),
    "gasly": ("alpine", "piegas01"),
    "arvid_lindblad": ("rb", "arvlin01"),
    "colapinto": ("alpine", "fracol01"),
    "bearman": ("haas", "olibea01"),
    "bortoleto": ("audi", "gabbor01"),
    "sainz": ("williams", "carsai01"),
    "albon": ("williams", "alealb01"),
    "ocon": ("haas", "estoco01"),
    "hulkenberg": ("audi", "nichul01"),
    "alonso": ("aston_martin", "feralo01"),
    "stroll": ("aston_martin", "lanstr01"),
    "bottas": ("cadillac", "valbot01"),
    "perez": ("cadillac", "serper01"),
}

def photo_driver(driver_id):
    #URL of the driver's current official portrait.
    if not driver_id:
        return None
    entry = DRIVERS.get(driver_id)
    if not entry:
        return None
    team, code = entry
    slug = TEAMS.get(team, team)
    return (
        "https://media.formula1.com/image/upload/"
        f"c_fill,g_north,w_440,h_440/q_auto/" # images properties crop to fill a frame, w_440,h_440 = 440×440 square, g_north = anchor at the top (keeps the head, not the chest), q_auto = automatic quality.
        f"d_common:f1:{SEASON}:fallback:driver:{SEASON}fallbackdriverright.webp/"
        f"{VERSION}/common/f1/{SEASON}/{slug}/{code}/"
        f"{SEASON}{slug}{code}right.webp"
    )

def logo_team(constructor_id):
    #URL of the team's current official logo.
    if not constructor_id:
        return None
    slug = TEAMS.get(constructor_id)
    if not slug:
        return None
    return (
        "https://media.formula1.com/image/upload/"
        f"c_lfill,w_200/q_auto/{VERSION}/" # images properties crop to fill a frame, w_440, q_auto = automatic quality.
        f"common/f1/{SEASON}/{slug}/{SEASON}{slug}logowhite.webp"
    )


# 3) PHOTOS FROM WIKIPEDIA
USER_AGENT = "f1-stats/1.0 (F1 Stats learning project)"
CACHE_FILE = pathlib.Path(__file__).parent / "cache" / "photos.json"

class PhotoService:
    #Finds the photo of a Wikipedia page and caches the result.

    def __init__(self):
        self._results = {}
        self._locks = {} # One asyncio.Lock per title, used to avoid asking Wikipedia for the same title twice at the same time.
        self._load()

    def _load(self):
        #Load the cache from disk, if the file exists.
        try:
            if CACHE_FILE.exists():
                self._results = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._results = {}

    def _save(self):
        """Write the current cache to disk."""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            CACHE_FILE.write_text(
                json.dumps(self._results, indent=2), encoding="utf-8"
            )
        except OSError:
            # If we can't save, it's not critical
            pass

    async def photo_for_wikipedia_url(self, wikipedia_url):
        # e.g. http://en.wikipedia.org/wiki/Ayrton_Senna
        if not wikipedia_url:
            return None

        title = self._title_from_url(wikipedia_url)
        return await self.photo_for(title)

    def _title_from_url(self, wikipedia_url):
        #Extract the page title from a full Wikipedia URL. http://en.wikipedia.org/wiki/Ayrton_Senna" -> "Ayrton_Senna"
        
        path = urllib.parse.urlparse(wikipedia_url).path  # "/wiki/Ayrton_Senna"
        title = path.split("/wiki/")[-1] # Ayrton_Senna
        return urllib.parse.unquote(title)

    async def photo_for(self, title):
        #""Return {'url': photo, 'canonical': real_title} or None.
        #'canonical' is the real title of the page. 
        #for example "Kimi_Antonelli" redirects to "Andrea_Kimi_Antonelli".
        
        if title in self._results:
            cached_value = self._results[title]
            return cached_value or None

        if title not in self._locks:
            self._locks[title] = asyncio.Lock()
        lock = self._locks[title]

        async with lock:
            if title in self._results:
                cached_value = self._results[title]
                return cached_value or None

            result = await self._fetch(title)

            if result is False:
                # Temporary error (Wikipedia down, rate limit, etc). 
                return None

            if result is None:
                self._results[title] = None
                self._save()
                return None

            # Result is a dict with "url" and "canonical".
            self._results[title] = result
            self._save()
            return result

    async def _fetch(self, title):
        #Returns:
        #    dict  -> {"url": ..., "canonical": ...}  if there is a photo
        #    None  -> the page has no photo, or doesn't exist
        #    False -> temporary error, should retry later (do not cache)
        encoded_title = urllib.parse.quote(title)
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_title}"

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers={"User-Agent": USER_AGENT})

            # 429 = "too many requests", 5xx = Wikipedia's own server error.
            # Both are temporary problems, not related to this specific page.
            if resp.status_code == 429 or resp.status_code >= 500:
                return False

            # Any other non-200 status usually means "page not found".
            if resp.status_code != 200:
                return None

            data = resp.json()

            # Some pages are "disambiguation" (a list of pages with the same name) or "missing".
            page_type = data.get("type")
            if page_type in ("disambiguation", "missing"):
                return None

            image_url = self._pick_image_url(data)
            if not image_url:
                return None

            canonical_title = self._pick_canonical_title(data, title)

            return {"url": image_url, "canonical": canonical_title}

        except httpx.HTTPError:
            # Network problem (timeout, connection refused, etc).
            return False

    def _pick_image_url(self, data):
        #Pick the best available image URL from the Wikipedia response.
        # Preferences: 1 -> original image, 2 -> thumbnail image.
        
        thumbnail_data = data.get("thumbnail")
        if thumbnail_data:
            thumbnail_url = thumbnail_data.get("source")
        else:
            thumbnail_url = None

        original_data = data.get("originalimage")
        if original_data:
            original_url = original_data.get("source")
        else:
            original_url = None

        if original_url:
            image_url = original_url
        elif thumbnail_url:
            image_url = thumbnail_url
        else:
            return None

        # Wikipedia image URLs sometimes have a "?something" at the end,
        # used for cache-busting. We remove it to keep a clean, stable URL.
        image_url = image_url.split("?")[0]
        return image_url

    def _pick_canonical_title(self, data, fallback_title):
        #Pick the real ("canonical") title of the page.

        titles_data = data.get("titles")
        if titles_data and titles_data.get("canonical"):
            return titles_data["canonical"]
        return fallback_title