"""Typed runtime data for the Desk integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

    from .api import DeskApiClient
    from .coordinator import DeskDataUpdateCoordinator


@dataclass(slots=True)
class DeskRuntimeData:
    """Runtime data stored on the config entry."""

    client: DeskApiClient
    coordinator: DeskDataUpdateCoordinator


type DeskConfigEntry = ConfigEntry[DeskRuntimeData]
