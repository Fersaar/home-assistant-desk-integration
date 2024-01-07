"""BlueprintEntity class."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN, NAME, VERSION
from .coordinator import IoLinkMasterDataUpdateCoordinator


class IoLinkMasterEntity(CoordinatorEntity):
    """BlueprintEntity class."""

    _attr_attribution = ATTRIBUTION

    def __init__(self, coordinator: IoLinkMasterDataUpdateCoordinator) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_unique_id = coordinator.config_entry.entry_id
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.unique_id)},
            name=coordinator.config_entry.data["ident"]["productName"],
            model=coordinator.config_entry.data["ident"]["productId"],
            manufacturer=coordinator.config_entry.data["ident"]["vendorName"],
        )
