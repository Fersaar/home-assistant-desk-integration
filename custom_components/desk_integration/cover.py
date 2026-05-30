"""Cover platform for the Desk integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityDescription,
    CoverEntityFeature,
)
from homeassistant.exceptions import HomeAssistantError

from .api import DeskApiError
from .const import STATE_MOVING_DOWN, STATE_MOVING_UP
from .entity import DeskEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DeskDataUpdateCoordinator
    from .data import DeskConfigEntry

COVER_DESCRIPTION = CoverEntityDescription(
    key="desk",
    translation_key="desk",
)


async def async_setup_entry(
    _hass: HomeAssistant,
    entry: DeskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the cover platform."""
    async_add_entities([DeskCover(entry.runtime_data.coordinator)])


class DeskCover(DeskEntity, CoverEntity):
    """Cover entity exposing desk movement and absolute positioning."""

    _attr_device_class = CoverDeviceClass.DAMPER
    _attr_supported_features = (
        CoverEntityFeature.OPEN
        | CoverEntityFeature.CLOSE
        | CoverEntityFeature.STOP
        | CoverEntityFeature.SET_POSITION
    )

    def __init__(self, coordinator: DeskDataUpdateCoordinator) -> None:
        """Initialize the cover entity."""
        super().__init__(coordinator)
        self.entity_description = COVER_DESCRIPTION
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-cover"

    # ---- Position helpers --------------------------------------------

    def _to_percentage(self, raw_position: int) -> int:
        """Convert a raw firmware position to a 0..100 cover position."""
        limits = self.coordinator.data.limits
        span = limits.upper - limits.lower
        if span <= 0:
            return 0
        clamped = max(min(raw_position, limits.upper), limits.lower)
        return round((clamped - limits.lower) * 100 / span)

    def _from_percentage(self, percentage: int) -> int:
        """Convert a 0..100 HA position to a raw firmware target."""
        limits = self.coordinator.data.limits
        span = limits.upper - limits.lower
        return round(limits.lower + span * (percentage / 100))

    # ---- Cover properties --------------------------------------------

    @property
    def current_cover_position(self) -> int | None:
        """Position from 0 (fully down/closed) to 100 (fully up/open)."""
        if self.coordinator.data is None:
            return None
        return self._to_percentage(self.coordinator.data.position)

    @property
    def is_closed(self) -> bool | None:
        """Return True if the desk is at the lower limit."""
        position = self.current_cover_position
        if position is None:
            return None
        return position <= 0

    @property
    def is_opening(self) -> bool:
        """Return True if the desk is currently moving up."""
        return self.coordinator.data.movement == STATE_MOVING_UP

    @property
    def is_closing(self) -> bool:
        """Return True if the desk is currently moving down."""
        return self.coordinator.data.movement == STATE_MOVING_DOWN

    # ---- Commands -----------------------------------------------------

    async def async_open_cover(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Move the desk up."""
        try:
            await self.coordinator.client.async_move_up()
        except DeskApiError as err:
            msg = f"Failed to move desk up: {err}"
            raise HomeAssistantError(msg) from err
        await self.coordinator.async_request_refresh()

    async def async_close_cover(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Move the desk down."""
        try:
            await self.coordinator.client.async_move_down()
        except DeskApiError as err:
            msg = f"Failed to move desk down: {err}"
            raise HomeAssistantError(msg) from err
        await self.coordinator.async_request_refresh()

    async def async_stop_cover(self, **kwargs: Any) -> None:  # noqa: ARG002
        """Stop any active movement."""
        try:
            await self.coordinator.client.async_stop()
        except DeskApiError as err:
            msg = f"Failed to stop desk: {err}"
            raise HomeAssistantError(msg) from err
        await self.coordinator.async_request_refresh()

    async def async_set_cover_position(self, **kwargs: Any) -> None:
        """Move the desk to a specific 0..100 position."""
        percentage = int(kwargs[ATTR_POSITION])
        target = self._from_percentage(percentage)
        try:
            await self.coordinator.client.async_move_to(target)
        except DeskApiError as err:
            msg = f"Failed to set desk position: {err}"
            raise HomeAssistantError(msg) from err
        await self.coordinator.async_request_refresh()
