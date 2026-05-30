"""Number platform for the Desk integration (movement limits)."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfLength
from homeassistant.exceptions import HomeAssistantError

from .api import DeskApiClient, DeskApiError
from .coordinator import DeskData
from .entity import DeskEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DeskDataUpdateCoordinator
    from .data import DeskConfigEntry


@dataclass(frozen=True, kw_only=True)
class DeskLimitNumberDescription(NumberEntityDescription):
    """Describes a configurable limit value."""

    value_fn: Callable[[DeskData], int]
    set_fn: Callable[[DeskApiClient, int], Awaitable[None]]


LIMIT_DESCRIPTIONS: tuple[DeskLimitNumberDescription, ...] = (
    DeskLimitNumberDescription(
        key="lower_limit",
        translation_key="lower_limit",
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
        native_min_value=0,
        native_max_value=10000,
        native_step=1,
        value_fn=lambda data: data.limits.lower,
        set_fn=lambda client, value: client.async_set_limits(lower=value),
    ),
    DeskLimitNumberDescription(
        key="upper_limit",
        translation_key="upper_limit",
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.BOX,
        native_min_value=0,
        native_max_value=10000,
        native_step=1,
        value_fn=lambda data: data.limits.upper,
        set_fn=lambda client, value: client.async_set_limits(upper=value),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DeskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the number platform."""
    coordinator = entry.runtime_data.coordinator
    entities: list[NumberEntity] = [DeskHeightNumber(coordinator)]
    entities.extend(
        DeskLimitNumber(coordinator, description) for description in LIMIT_DESCRIPTIONS
    )
    async_add_entities(entities)


class DeskHeightNumber(DeskEntity, NumberEntity):
    """Number entity that exposes the current desk height in raw units.

    Setting a value moves the desk to that absolute position. The slider
    range follows the firmware's configured lower/upper limits so the value
    shown is the actual height as reported by the desk.
    """

    _attr_device_class = NumberDeviceClass.DISTANCE
    _attr_native_unit_of_measurement = UnitOfLength.MILLIMETERS
    _attr_mode = NumberMode.SLIDER
    _attr_native_step = 1
    _attr_translation_key = "height"
    _attr_icon = "mdi:desk"

    def __init__(self, coordinator: DeskDataUpdateCoordinator) -> None:
        """Initialize the height entity."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-height"

    @property
    def native_min_value(self) -> float:
        """Lower bound from configured limits."""
        if self.coordinator.data is None:
            return 0.0
        return float(self.coordinator.data.limits.lower)

    @property
    def native_max_value(self) -> float:
        """Upper bound from configured limits."""
        if self.coordinator.data is None:
            return 10000.0
        return float(self.coordinator.data.limits.upper)

    @property
    def native_value(self) -> float | None:
        """Return the current raw desk position."""
        if self.coordinator.data is None:
            return None
        return float(self.coordinator.data.position)

    async def async_set_native_value(self, value: float) -> None:
        """Move the desk to the requested absolute position."""
        try:
            await self.coordinator.client.async_move_to(int(value))
        except DeskApiError as err:
            raise HomeAssistantError(f"Failed to move desk: {err}") from err
        await self.coordinator.async_request_refresh()


class DeskLimitNumber(DeskEntity, NumberEntity):
    """Number entity that exposes a configurable movement limit."""

    entity_description: DeskLimitNumberDescription

    def __init__(
        self,
        coordinator: DeskDataUpdateCoordinator,
        description: DeskLimitNumberDescription,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return the configured limit value."""
        if self.coordinator.data is None:
            return None
        return float(self.entity_description.value_fn(self.coordinator.data))

    async def async_set_native_value(self, value: float) -> None:
        """Update the limit via the API."""
        try:
            await self.entity_description.set_fn(self.coordinator.client, int(value))
        except DeskApiError as err:
            raise HomeAssistantError(f"Failed to update desk limit: {err}") from err
        await self.coordinator.async_refresh_limits()
