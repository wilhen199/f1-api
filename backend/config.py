"""Shared application configuration.

Keeping CURRENT_SEASON here avoids repeating the same
datetime/timezone calculation in every router file.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

CURRENT_SEASON = datetime.now(ZoneInfo("America/Bogota")).year
