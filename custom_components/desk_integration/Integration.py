"""Example integration using DataUpdateCoordinator."""

from datetime import timedelta
import logging

import async_timeout

import homeassistant.components.cover as cover
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from typing import Any
from aiohttp.client import ClientSession

from .const import DOMAIN
from homeassistant.const import CONF_ADDRESS

_LOGGER = logging.getLogger(__name__)


class MyCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(
        self, hass: HomeAssistant, configData: dict, session: ClientSession
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=5),
        )
        self._configData = configData
        self._session = session
        self._url = "http://" + configData[CONF_ADDRESS]
        self._position = 0
        self._connected = False
        self._lowerLimit = 500
        self._upperLimit = 1000

    async def move_up(self):
        resp = await self._session.get(f"{self._url}/move?direction=UP")
        resp.raise_for_status()
        pass

    async def move_down(self):
        resp = await self._session.get(f"{self._url}/move?direction=DOWN")
        resp.raise_for_status()
        pass

    async def stop(self):
        resp = await self._session.get(f"{self._url}/move?direction=STOP")
        resp.raise_for_status()
        pass

    async def move_to(self, value: int):
        target = self._lowerLimit + (self._upperLimit - self._lowerLimit) * (
            value / 100
        )
        resp = await self._session.post(f"{self._url}/position?target={target}")
        resp.raise_for_status()
        pass

    @property
    def lower_limit(self) -> bool:
        return self._lowerLimit

    @property
    def position(self) -> bool:
        percentage = (self._position - self._lowerLimit) / (
            self._upperLimit - self._lowerLimit
        )
        return percentage * 100

    @property
    def is_connected(self) -> bool:
        return self._connected

    async def _async_setup(self) -> None:
        resp = await self._session.get(f"{self._url}/limits")
        self._lowerLimit = resp.json()["lowerLimit"]
        self._upperLimit = resp.json()["lowerLimit"]

    async def _async_update_data(self):
        """update data"""
        print("coordinator _async_update_data called")
        try:
            async with async_timeout.timeout(3):
                response = await self._session.get(f"{self._url}/position")
                self._position = int(await response.text())
        except:
            self._position = 0
            raise UpdateFailed(f"Error communicating with IP: {self._url}")
