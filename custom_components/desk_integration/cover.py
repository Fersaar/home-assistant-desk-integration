import logging


import homeassistant.components.cover as cover
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import callback, HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import CONF_ADDRESS
from .const import DOMAIN
from homeassistant.helpers.update_coordinator import CoordinatorEntity


ENTITY_DESCRIPTIONS = (
    cover.CoverEntityDescription(
        key="desk_integration",
        name="myDesk",
        icon="mdi:desk",
    ),
)
from typing import Any

from .const import DOMAIN
from .Integration import MyCoordinator

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
    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        [
            MyEntity(coordinator, description, entry.title)
            for description in ENTITY_DESCRIPTIONS
        ],
        update_before_add=True,
    )


class MyEntity(CoordinatorEntity, cover.CoverEntity):
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
        self._coordinator = coordinator
        self.entity_description = description
        self._attr_unique_id = self._coordinator._configData[CONF_ADDRESS]
        self._attr_name = description.name  # + "_attr_name"
        self._attr_device_class = cover.CoverDeviceClass.DAMPER
        self._attr_icon = "mdi:desk"
        self._attr_device_info = DeviceInfo(
            name=title,
            identifiers={(DOMAIN, self._attr_unique_id)},
            model="desk3000",
            manufacturer="selfMade",
        )
        self._attr_supported_features = (
            cover.CoverEntityFeature.OPEN
            | cover.CoverEntityFeature.CLOSE
            | cover.CoverEntityFeature.STOP
            | cover.CoverEntityFeature.SET_POSITION
        )

    @property
    def current_cover_position(self) -> int | None:
        return self._coordinator.position

    # @property
    # def available(self) -> bool:
    #     """Return True if entity is available"""
    #     return self._coordinator.is_connected

    @property
    def is_closed(self) -> bool:
        """Return True if entity is available"""
        return self._coordinator.position > self._coordinator.lower_limit

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Close the cover."""
        try:
            await self._coordinator.move_up()
        except Exception as e:
            raise HomeAssistantError("Failed to move up")
        await self._coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        try:
            await self._coordinator.stop()
        except Exception as e:
            raise HomeAssistantError("Failed to stop")
        await self._coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Cose the cover."""
        try:
            await self._coordinator.move_down()
        except Exception as e:
            raise HomeAssistantError("Failed to move down")
        await self._coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """CLose the cover."""
        try:
            await self._coordinator.move_to(int(kwargs[cover.ATTR_POSITION]))
        except Exception as e:
            raise HomeAssistantError("Failed to move down")
        await self._coordinator.async_request_refresh()

    @callback
    def _handle_coordinator_update(self, *args: Any) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()
