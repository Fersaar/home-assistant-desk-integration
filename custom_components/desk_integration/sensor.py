"""Representation of Idasen Desk sensors."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import CONF_ADDRESS, UnitOfLength
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .Integration import MyCoordinator
from .entity import DeskEntity

SENSORS = (
    SensorEntityDescription(
        key="height",
        translation_key="height",
        native_unit_of_measurement=UnitOfLength.MILLIMETERS,
        device_class=SensorDeviceClass.DISTANCE,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        suggested_display_precision=3,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Idasen Desk sensors."""
    async_add_entities(
        IdasenDeskSensor(hass.data[DOMAIN][entry.entry_id], sensor_description)
        for sensor_description in SENSORS
    )


class IdasenDeskSensor(DeskEntity, SensorEntity):
    """IdasenDesk sensor."""

    entity_description: SensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: MyCoordinator,
        description,
    ) -> None:
        """Initialize the IdasenDesk sensor entity."""
        super().__init__(coordinator)
        self.entity_description = description

    @property
    def native_value(self) -> int | None:
        """Return the native value of the sensor."""
        return self.coordinator.position

    @callback
    def _handle_coordinator_update(self, *args: Any) -> None:
        """Handle data update."""
        self.async_write_ha_state()
