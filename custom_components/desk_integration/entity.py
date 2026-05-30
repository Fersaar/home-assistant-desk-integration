"""Base entity for the Desk integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, NAME

if TYPE_CHECKING:
    from .coordinator import DeskDataUpdateCoordinator


class DeskEntity(CoordinatorEntity["DeskDataUpdateCoordinator"]):
    """Base class for desk entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DeskDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.config_entry.entry_id)},
            name=NAME,
            manufacturer=MANUFACTURER,
            model=MODEL,
            configuration_url=coordinator.client.base_url,
        )
