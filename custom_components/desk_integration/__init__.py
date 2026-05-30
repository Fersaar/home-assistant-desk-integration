"""The Desk integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, Platform
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DeskApiClient, DeskApiError
from .coordinator import DeskDataUpdateCoordinator
from .data import DeskRuntimeData

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import DeskConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BUTTON,
    Platform.COVER,
    Platform.NUMBER,
    Platform.SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: DeskConfigEntry) -> bool:
    """Set up the Desk integration from a config entry."""
    client = DeskApiClient(
        host=entry.data[CONF_HOST],
        session=async_get_clientsession(hass),
    )
    coordinator = DeskDataUpdateCoordinator(hass=hass, entry=entry, client=client)

    try:
        await coordinator.async_config_entry_first_refresh()
    except DeskApiError as err:
        raise ConfigEntryNotReady(str(err)) from err

    entry.runtime_data = DeskRuntimeData(client=client, coordinator=coordinator)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DeskConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: DeskConfigEntry) -> None:
    """Reload a config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
