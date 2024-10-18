"""Config flow for Idasen Desk integration."""

from __future__ import annotations

import logging
from typing import Any

# from bluetooth_data_tools import human_readable_name
# from idasen_ha import Desk
# from idasen_ha.errors import AuthFailedError
import voluptuous as vol

from homeassistant import config_entries

from homeassistant.const import CONF_ADDRESS
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from . import const

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Handle a config flow for Idasen Desk integration."""

    VERSION = 1

    STEP_USER_DATA_SCHEMA = vol.Schema(
        {
            vol.Required(CONF_ADDRESS): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.URL),
            )
        }
    )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the user step to configure device."""
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="desk" + address, data={CONF_ADDRESS: address}
            )

        return self.async_show_form(
            step_id="user",
            data_schema=self.STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
