"""Button platform for the Desk integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import (
    ButtonDeviceClass,
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError

from .api import DeskApiError
from .entity import DeskEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DeskDataUpdateCoordinator
    from .data import DeskConfigEntry

AUTO_CALIBRATE_DESCRIPTION = ButtonEntityDescription(
    key="auto_calibrate",
    translation_key="auto_calibrate",
    device_class=ButtonDeviceClass.IDENTIFY,
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: DeskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    async_add_entities([DeskAutoCalibrateButton(entry.runtime_data.coordinator)])


class DeskAutoCalibrateButton(DeskEntity, ButtonEntity):
    """Button that triggers the firmware auto-calibration routine."""

    def __init__(self, coordinator: DeskDataUpdateCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = AUTO_CALIBRATE_DESCRIPTION
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-auto-calibrate"

    async def async_press(self) -> None:
        """Run auto-calibration on the desk."""
        try:
            await self.coordinator.client.async_auto_calibrate()
        except DeskApiError as err:
            msg = f"Auto-calibration failed: {err}"
            raise HomeAssistantError(msg) from err
        # Re-read limits since auto-calibrate updates them.
        await self.coordinator.async_refresh_limits()
