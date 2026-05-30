"""Sensor platform for the Desk integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory

from .const import STATE_MOVING_DOWN, STATE_MOVING_UP, STATE_NOT_MOVING
from .coordinator import DeskData
from .entity import DeskEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import DeskDataUpdateCoordinator
    from .data import DeskConfigEntry


@dataclass(frozen=True, kw_only=True)
class DeskSensorEntityDescription(SensorEntityDescription):
    """Describes a Desk sensor."""

    value_fn: Callable[[DeskData], int | str | None]


SENSOR_DESCRIPTIONS: tuple[DeskSensorEntityDescription, ...] = (
    DeskSensorEntityDescription(
        key="position",
        translation_key="position",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda data: data.position,
    ),
    DeskSensorEntityDescription(
        key="movement",
        translation_key="movement",
        device_class=SensorDeviceClass.ENUM,
        options=[STATE_MOVING_UP, STATE_MOVING_DOWN, STATE_NOT_MOVING],
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.movement,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DeskConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        DeskSensor(coordinator, description) for description in SENSOR_DESCRIPTIONS
    )


class DeskSensor(DeskEntity, SensorEntity):
    """Sensor exposing a value derived from the coordinator data."""

    entity_description: DeskSensorEntityDescription

    def __init__(
        self,
        coordinator: DeskDataUpdateCoordinator,
        description: DeskSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}-{description.key}"

    @property
    def native_value(self) -> int | str | None:
        """Return the current value."""
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
