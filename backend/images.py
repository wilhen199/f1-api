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
from datetime import datetime

import httpx

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
    """Return the flag image URL for a given country name or nationality."""
    if not name:
        return None
    code = COUNTRIES.get(name) or NATIONALITIES.get(name) or UNKNOWN_CODE
    if not code.isalpha() or len(code) > 4:
        return None
    return f"https://flagcdn.com/{SIZE}/{urllib.parse.quote(code)}.png"


# 2) Official photos
# Website https://www.formula1.com publishes the season's photos at
# media.formula1.com. The URL follow this format:
#   .../common/f1/2026/{equipo}/{codigo}/2026{equipo}{codigo}right.webp
# For each SEASON, items must be updated:
#   - SEASON  -> the current year
#   - VERSION    -> files version used by F1 website
#   - TEAMS    -> Teams racing this season
#   - DRIVERS    -> Drivers racing this season


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
    """Return the official portrait URL for a current season driver."""
    if not driver_id:
        return None
    entry = DRIVERS.get(driver_id)
    if not entry:
        return None
    team, code = entry
    slug = TEAMS.get(team, team)
    return (
        "https://media.formula1.com/image/upload/"
        # c_fill,g_north,w_440,h_440 = 440x440 square anchored at top (keeps head).
        # q_auto = automatic quality.
        f"c_fill,g_north,w_440,h_440/q_auto/"
        f"d_common:f1:{SEASON}:fallback:driver:{SEASON}fallbackdriverright.webp/"
        f"{VERSION}/common/f1/{SEASON}/{slug}/{code}/"
        f"{SEASON}{slug}{code}right.webp"
    )


def logo_team(constructor_id):
    """Return the official logo URL for a current season team."""
    if not constructor_id:
        return None
    slug = TEAMS.get(constructor_id)
    if not slug:
        return None
    return (
        "https://media.formula1.com/image/upload/"
        f"c_lfill,w_200/q_auto/{VERSION}/"  # images properties crop to fill a frame, w_440, q_auto = automatic quality.
        f"common/f1/{SEASON}/{slug}/{SEASON}{slug}logowhite.webp"
    )


# 3) PHOTOS FROM WIKIPEDIA
USER_AGENT = "f1-stats/1.0 (F1 Stats learning project)"
CACHE_FILE = pathlib.Path(__file__).parent / "cache" / "photos.json"


class PhotoService:
    """Resolves and caches the photo of a Wikipedia page."""

    def __init__(self):
        """Initialize in-memory and disk cache, and per-title locks."""
        self._results = {}
        # One asyncio.Lock per title, so two requests for the SAME title
        # don't both call Wikipedia at the same time (wasted work).
        self._locks = {}
        self._load()

    # ------------------------------------------------------------------
    # Disk persistence
    # ------------------------------------------------------------------

    def _load(self):
        """Load the cache from disk, if the file already exists."""
        try:
            if CACHE_FILE.exists():
                self._results = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            self._results = {}

    def _save(self):
        """Write the current in-memory cache to disk."""
        try:
            CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            CACHE_FILE.write_text(json.dumps(self._results, indent=2), encoding="utf-8")
        except OSError:
            # Not critical: worst case, we lose the cache on next restart.
            pass

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def photo_for_wikipedia_url(self, wikipedia_url):
        """Same as photo_for(), but takes a full Wikipedia URL
        (e.g. "http://en.wikipedia.org/wiki/Ayrton_Senna") instead of
        a bare page title.
        """
        if not wikipedia_url:
            return None
        page_title = self._title_from_url(wikipedia_url)
        return await self.photo_for(page_title)

    def _title_from_url(self, wikipedia_url):
        """Extract the page title from a full Wikipedia URL.

        "http://en.wikipedia.org/wiki/Ayrton_Senna" -> "Ayrton_Senna"

        Also decodes percent-encoded characters (e.g. %C3%A4 -> "ä"),
        so the title matches exactly what's stored in the cache and
        what _fetch() will re-encode when calling Wikipedia's API.
        """
        path = urllib.parse.urlparse(wikipedia_url).path
        title = path.split("/wiki/")[-1]
        return urllib.parse.unquote(title)

    # ------------------------------------------------------------------
    # Core logic: cache-first, then fetch with a per-title lock
    # ------------------------------------------------------------------

    async def photo_for(self, page_title):
        """Return {'url': photo, 'canonical': real_title} or None.

        'canonical' is the REAL title of the page after Wikipedia
        resolves redirects (e.g. "Kimi_Antonelli" redirects to
        "Andrea_Kimi_Antonelli"). Use it for any "view on Wikipedia"
        link, since the original title might not be a valid URL.
        """
        # STEP 1: fast path. Already resolved before? Return it directly,
        # no network call, no lock needed.
        if page_title in self._results:
            return self._results[page_title]

        # STEP 2: not cached yet. Get (or create) a lock just for this
        # title, so if two callers ask for the same title at the same
        # time, only one of them actually hits the network.
        if page_title not in self._locks:
            self._locks[page_title] = asyncio.Lock()
        lock = self._locks[page_title]

        async with lock:
            # STEP 3: check again. While we were waiting for the lock,
            # another task might have already resolved this exact title
            # and saved it — no need to fetch it twice.
            if page_title in self._results:
                return self._results[page_title]

            # STEP 4: genuinely new title, ask Wikipedia.
            result = await self._fetch(page_title)

            # STEP 5: decide what to do based on the 3 possible outcomes.
            if result is False:
                # Temporary error (rate limit, Wikipedia down, network
                # issue). Don't cache anything, so the next call retries
                # instead of being stuck with a bad answer forever.
                return None

            # Either a real dict with the photo, or None (page exists
            # but has no photo). Both are permanent facts about this
            # title, so we cache them either way.
            self._results[page_title] = result
            self._save()
            return result

    async def _fetch(self, page_title):
        """Fetch the photo for a Wikipedia page title.

        Returns:
            dict  -> {"url": ..., "canonical": ...}  if there is a photo
            None  -> the page has no photo, or doesn't exist
            False -> temporary error, should retry later (do not cache)
        """
        encoded_title = urllib.parse.quote(page_title)
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

            canonical_title = self._pick_canonical_title(data, page_title)

            return {"url": image_url, "canonical": canonical_title}

        except httpx.HTTPError:
            # Network problem (timeout, connection refused, etc).
            return False

    def _pick_image_url(self, data):
        """Pick the best available image URL from the Wikipedia response.

        Preferences: 1 -> original image, 2 -> thumbnail image.
        """

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
        """Return the canonical title of the page, falling back to the original title."""

        titles_data = data.get("titles")
        if titles_data and titles_data.get("canonical"):
            return titles_data["canonical"]
        return fallback_title
