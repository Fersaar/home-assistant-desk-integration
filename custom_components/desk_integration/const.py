"""Constants for the Desk integration."""

from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "desk_integration"
NAME: Final = "Schreibtisch"
MANUFACTURER: Final = "Self Made"
MODEL: Final = "Desk 3000"

LOGGER: Final = logging.getLogger(__package__)

# Polling interval (seconds). Short enough to track live movement.
DEFAULT_SCAN_INTERVAL: Final = 2
# HTTP request timeout (seconds).
REQUEST_TIMEOUT: Final = 5

# Movement state strings reported by the firmware.
STATE_MOVING_UP: Final = "moving up"
STATE_MOVING_DOWN: Final = "moving down"
STATE_NOT_MOVING: Final = "not moving"
