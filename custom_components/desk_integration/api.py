"""HTTP API client for the Desk firmware."""

from __future__ import annotations

import asyncio
import json
import socket
from dataclasses import dataclass

import aiohttp

from .const import (
    REQUEST_TIMEOUT,
    STATE_MOVING_DOWN,
    STATE_MOVING_UP,
    STATE_NOT_MOVING,
)


class DeskApiError(Exception):
    """Generic Desk API error."""


class DeskApiCommunicationError(DeskApiError):
    """Communication error with the Desk."""


@dataclass(slots=True)
class DeskLimits:
    """Configured movement limits."""

    lower: int
    upper: int


@dataclass(slots=True)
class DeskStatus:
    """Snapshot of desk runtime state."""

    position: int
    movement: str  # one of STATE_MOVING_UP, STATE_MOVING_DOWN, STATE_NOT_MOVING


class DeskApiClient:
    """Async HTTP client for the desk firmware described in openapi.yaml."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        """
        Initialize the client.

        ``host`` may be a bare IP/hostname or a full ``http(s)://...`` URL.
        """
        host = host.strip().rstrip("/")
        if not host.startswith(("http://", "https://")):
            host = f"http://{host}"
        self._base_url = host
        self._session = session

    @property
    def base_url(self) -> str:
        """Return the configured base URL."""
        return self._base_url

    # ---- Movement -----------------------------------------------------

    async def async_move_up(self) -> None:
        """Start moving the desk up."""
        await self._request("GET", "/move", params={"direction": "UP"})

    async def async_move_down(self) -> None:
        """Start moving the desk down."""
        await self._request("GET", "/move", params={"direction": "DOWN"})

    async def async_stop(self) -> None:
        """Stop any active movement."""
        await self._request("GET", "/move", params={"direction": "STOP"})

    async def async_move_to(self, target: int) -> None:
        """Move the desk to the given absolute target position."""
        await self._request("POST", "/position", data={"target": str(int(target))})

    # ---- Status -------------------------------------------------------

    async def async_get_position(self) -> int:
        """Return the current absolute position."""
        text = await self._request_text("GET", "/position")
        try:
            return int(text.strip())
        except ValueError as err:
            msg = f"Unexpected position payload: {text!r}"
            raise DeskApiCommunicationError(msg) from err

    async def async_get_movement_state(self) -> str:
        """Return the current movement state string."""
        text = (await self._request_text("GET", "/state")).strip().lower()
        if text not in (STATE_MOVING_UP, STATE_MOVING_DOWN, STATE_NOT_MOVING):
            return STATE_NOT_MOVING
        return text

    async def async_get_status(self) -> DeskStatus:
        """Return position and movement state in a single call."""
        position, movement = await asyncio.gather(
            self.async_get_position(),
            self.async_get_movement_state(),
        )
        return DeskStatus(position=position, movement=movement)

    # ---- Limits / calibration ----------------------------------------

    async def async_get_limits(self) -> DeskLimits:
        """Return the configured movement limits."""
        text = await self._request_text("GET", "/limits")
        try:
            payload = json.loads(text)
            return DeskLimits(
                lower=int(payload["lowerLimit"]),
                upper=int(payload["upperLimit"]),
            )
        except (ValueError, KeyError, TypeError) as err:
            msg = f"Unexpected limits payload: {text!r}"
            raise DeskApiCommunicationError(msg) from err

    async def async_set_limits(
        self,
        lower: int | None = None,
        upper: int | None = None,
    ) -> None:
        """
        Update the lower and/or upper movement limits.

        The firmware always returns 400 from this endpoint regardless of
        success, so the response status is ignored.
        """
        if lower is None and upper is None:
            return
        data: dict[str, str] = {}
        if lower is not None:
            data["lower"] = str(int(lower))
        if upper is not None:
            data["upper"] = str(int(upper))
        await self._request("POST", "/limits", data=data, ignore_status=True)

    async def async_calibrate(
        self,
        pos1: int | None = None,
        pos2: int | None = None,
    ) -> None:
        """Update one or both calibration points."""
        data: dict[str, str] = {}
        if pos1 is not None:
            data["pos1"] = str(int(pos1))
        if pos2 is not None:
            data["pos2"] = str(int(pos2))
        if not data:
            return
        await self._request("POST", "/calibrate", data=data)

    async def async_auto_calibrate(self) -> None:
        """Run the firmware's automatic calibration routine."""
        # Auto calibration physically moves the desk end-to-end and may
        # take a long time; use a generous timeout.
        await self._request("POST", "/autoCalibrate", timeout=120)

    # ---- HTTP helpers -------------------------------------------------

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        timeout: float | None = None,
        ignore_status: bool = False,
    ) -> aiohttp.ClientResponse:
        url = f"{self._base_url}{path}"
        try:
            async with asyncio.timeout(timeout or REQUEST_TIMEOUT):
                response = await self._session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                )
                if not ignore_status:
                    response.raise_for_status()
                return response
        except TimeoutError as err:
            msg = f"Timeout calling {method} {url}"
            raise DeskApiCommunicationError(msg) from err
        except (aiohttp.ClientError, socket.gaierror) as err:
            msg_0 = f"Error calling {method} {url}: {err}"
            raise DeskApiCommunicationError(msg_0) from err

    async def _request_text(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
    ) -> str:
        response = await self._request(method, path, params=params)
        return await response.text()
