"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from homeassistant.const import CONF_ADDRESS
from .Integration import MyCoordinator


class DeskEntity(CoordinatorEntity[MyCoordinator]):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: MyCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = self.coordinator._configData[CONF_ADDRESS]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name="helloWorld",
            model="desk3000",
            manufacturer="selfMade",
        )
