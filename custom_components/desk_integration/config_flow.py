"""Config flow for the Desk integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DeskApiClient, DeskApiError
from .const import DOMAIN, LOGGER

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class DeskConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a Desk config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            client = DeskApiClient(
                host=host, session=async_get_clientsession(self.hass)
            )

            try:
                await client.async_get_position()
            except DeskApiError as err:
                LOGGER.warning("Cannot connect to desk %s: %s", host, err)
                errors["base"] = "cannot_connect"
            except Exception:  # noqa: BLE001
                LOGGER.exception("Unexpected error connecting to desk %s", host)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(client.base_url)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Desk ({host})",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
