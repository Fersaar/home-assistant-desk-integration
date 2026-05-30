"""DataUpdateCoordinator for the Desk integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DeskApiError, DeskLimits, DeskStatus
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER, STATE_NOT_MOVING

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .api import DeskApiClient
    from .data import DeskConfigEntry


@dataclass(slots=True)
class DeskData:
    """Aggregated state polled from the desk."""

    position: int
    movement: str
    limits: DeskLimits


class DeskDataUpdateCoordinator(DataUpdateCoordinator[DeskData]):
    """Coordinator polling position, movement state and limits."""

    config_entry: DeskConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: DeskConfigEntry,
        client: DeskApiClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client
        self._limits: DeskLimits | None = None

    async def _async_setup(self) -> None:
        """Fetch limits once at setup."""
        try:
            self._limits = await self.client.async_get_limits()
        except DeskApiError as err:
            raise UpdateFailed(f"Could not read desk limits: {err}") from err

    async def _async_update_data(self) -> DeskData:
        """Fetch the latest desk status."""
        try:
            status: DeskStatus = await self.client.async_get_status()
        except DeskApiError as err:
            raise UpdateFailed(f"Error communicating with desk: {err}") from err

        if self._limits is None:
            try:
                self._limits = await self.client.async_get_limits()
            except DeskApiError as err:
                raise UpdateFailed(f"Error reading desk limits: {err}") from err

        return DeskData(
            position=status.position,
            movement=status.movement or STATE_NOT_MOVING,
            limits=self._limits,
        )

    async def async_refresh_limits(self) -> None:
        """Force a re-read of the configured limits and refresh listeners."""
        try:
            self._limits = await self.client.async_get_limits()
        except DeskApiError as err:
            raise UpdateFailed(f"Error reading desk limits: {err}") from err
        await self.async_request_refresh()
