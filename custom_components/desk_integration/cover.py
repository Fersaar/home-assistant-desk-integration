import logging
from typing import Any

import homeassistant.components.cover as cover
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .Integration import MyCoordinator
from .entity import DeskEntity

ENTITY_DESCRIPTIONS = (
    cover.CoverEntityDescription(
        key="desk_integration",
        name="myDesk",
        icon="mdi:desk",
    ),
)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Config entry example."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Fetch initial data so we have data when entities subscribe
    #
    # If the refresh fails, async_config_entry_first_refresh will
    # raise ConfigEntryNotReady and setup will try again later
    #
    # If you do not want to retry setup on failure, use
    # coordinator.async_refresh() instead
    #
    # await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            MyEntity(coordinator, description, entry.title)
            for description in ENTITY_DESCRIPTIONS
        ]
        # update_before_add=True,
    )


class MyEntity(DeskEntity, cover.CoverEntity):
    """An entity using CoordinatorEntity.

    The CoordinatorEntity class provides:
      should_poll
      async_update
      async_added_to_hass
      available

    """

    def __init__(self, coordinator: MyCoordinator, description, title):
        """Pass coordinator to CoordinatorEntity."""
        super().__init__(coordinator)
        """Pass coordinator to CoordinatorEntity."""
        self.entity_description = description
        self._attr_name = description.name  # + "_attr_name"
        self._attr_device_class = cover.CoverDeviceClass.DAMPER
        self._attr_icon = "mdi:desk"

        self._attr_supported_features = (
            cover.CoverEntityFeature.OPEN
            | cover.CoverEntityFeature.CLOSE
            | cover.CoverEntityFeature.STOP
            | cover.CoverEntityFeature.SET_POSITION
        )

    @property
    def current_cover_position(self) -> float | None:
        return min(0, self.coordinator.percentage)

    @property
    def is_closed(self) -> bool:
        return self.coordinator.position == self.coordinator.lower_limit

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        try:
            await self.coordinator.move_up()
        except Exception as e:
            raise HomeAssistantError("Failed to move up")
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        try:
            await self.coordinator.stop()
        except Exception as e:
            raise HomeAssistantError("Failed to stop")
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Cose the cover."""
        try:
            await self.coordinator.move_down()
        except Exception as e:
            raise HomeAssistantError("Failed to move down")
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """CLose the cover."""
        try:
            await self.coordinator.move_to(int(kwargs[cover.ATTR_POSITION]))
        except Exception as e:
            raise HomeAssistantError("Failed to move down")
        await self.coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self, *args: Any) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
