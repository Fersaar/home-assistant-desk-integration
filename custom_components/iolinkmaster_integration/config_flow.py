"""Adds config flow for Blueprint."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .IoLinkMasterDataProvider import (
    IntegrationBlueprintApiClientAuthenticationError,
    IntegrationBlueprintApiClientCommunicationError,
    IntegrationBlueprintApiClientError,
    IoLinkMasterDataProvider,
)
from . import const


class BlueprintFlowHandler(config_entries.ConfigFlow, domain=const.DOMAIN):
    """Config flow for Blueprint."""

    VERSION = 1

    STEP_USER_DATA_SCHEMA = vol.Schema(
        {
            vol.Required(const.IP): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.URL),
            ),
            vol.Required(const.USERNAME): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
            ),
            vol.Required(const.PASSWORD): selector.TextSelector(
                selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD),
            ),
        }
    )

    async def validate_input(self, user_input: dict) -> [str, str]:
        """Validate data."""
        url = user_input[const.IP]
        username = user_input[const.USERNAME]
        password = user_input[const.PASSWORD]
        client = IoLinkMasterDataProvider(
            url=url,
            username=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.pingDevice()
        config = await client.getMasterConfig()
        return config | user_input

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> config_entries.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                config = await self.validate_input(user_input)
            except IntegrationBlueprintApiClientAuthenticationError as exception:
                const.LOGGER.warning(exception)
                _errors["base"] = "auth"
            except IntegrationBlueprintApiClientCommunicationError as exception:
                const.LOGGER.error(exception)
                _errors["base"] = "connection"
            except IntegrationBlueprintApiClientError as exception:
                const.LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=config["ident"]["productName"],
                    data=config,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.STEP_USER_DATA_SCHEMA,
            errors=_errors,
        )
