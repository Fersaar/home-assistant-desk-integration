"""Sample API Client."""
from __future__ import annotations

import asyncio
import socket

import aiohttp
import async_timeout


class IntegrationBlueprintApiClientError(Exception):
    """Exception to indicate a general API error."""


class IntegrationBlueprintApiClientCommunicationError(
    IntegrationBlueprintApiClientError
):
    """Exception to indicate a communication error."""


class IntegrationBlueprintApiClientAuthenticationError(
    IntegrationBlueprintApiClientError
):
    """Exception to indicate an authentication error."""


class IoLinkMasterDataProvider:
    """Sample API Client."""

    url_ = ""
    masterNr = ""
    config = {"inputOutputs": {}, "ident": {}}
    url_ = ""
    username_ = ""
    password_ = ""
    session_ = None
    authHeader = ""

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Sample API Client."""
        self.url_ = "http://" + url
        self.username_ = username
        self.password_ = password
        self.session_ = session

    async def pingDevice(self):
        return True

    async def getMasterConfig(self):
        # mastersList = await self.request_wrapper(
        #     method="get", url=self.url_ + "/masters"
        # )
        self.masterNr = 1  # mastersList[0]["masterNumber"]

        url = f"{self.url_}/iolink/v1/masters/{self.masterNr}/identification"
        self.config["ident"] = await self.request_wrapper(method="get", url=url)

        url = f"{self.url_}/iolink/v1/masters/{self.masterNr}/ports"
        ports = await self.request_wrapper(method="get", url=url)
        portNumbers = []
        for port in ports:
            portNumbers.append(port["portNumber"])

        for number in portNumbers:
            url = f"{self.url_}/iolink/v1/masters/{self.masterNr}/ports/{number}/configuration"
            portConfig = await self.request_wrapper(method="get", url=url)
            ioConfig = {
                "cq": {"mode": "", "value": False},
                "iq": {"mode": "", "value": False},
            }
            match portConfig["mode"]:
                case "DIGITAL_INPUT":
                    ioConfig["cq"]["mode"] = "input"
                case "DIGITAL_OUTPUT":
                    ioConfig["cq"]["mode"] = "output"
            match portConfig["iqConfiguration"]:
                case "DIGITAL_INPUT":
                    ioConfig["iq"]["mode"] = "input"
                case "DIGITAL_OUTPUT":
                    ioConfig["iq"]["mode"] = "output"
            self.config["inputOutputs"][portConfig["deviceAlias"]] = ioConfig
        return self.config

    async def async_get_data(self):
        if self.config["inputOutputs"] == {}:
            await self.getMasterConfig()
        for deviceAlias, io in self.config["inputOutputs"].items():
            url = f"{self.url_}/iolink/v1/devices/{deviceAlias}/processdata/value?format=byteArray"
            processdata = await self.request_wrapper(method="get", url=url)
            match io["cq"]["mode"]:
                case "input":
                    io["cq"]["value"] = processdata.get("getData", {}).get(
                        "cqValue", False
                    )
                case "output":
                    io["cq"]["value"] = processdata.get("setData", {}).get(
                        "cqValue", False
                    )
            match io["iq"]["mode"]:
                case "input":
                    io["iq"]["value"] = processdata.get("getData", {}).get(
                        "iqValue", False
                    )
                case "output":
                    io["iq"]["value"] = processdata.get("setData", {}).get(
                        "iqValue", False
                    )
        return self.config["inputOutputs"]

    async def login(self):
        self.session_.cookie_jar.clear()
        url = self.url_ + "/api/balluff/v1/users/login"
        data = {"username": self.username_, "password": self.password_}
        async with async_timeout.timeout(100000):
            resp = await self.session_.request(
                method="post",
                url=url,
                json=data,
            )
            if resp.status == 403:
                raise IntegrationBlueprintApiClientAuthenticationError(
                    "Invalid credentials/ missing user rights",
                )
            resp.raise_for_status()
            jsonResp = await resp.json()
            self.session_.cookie_jar.update_cookies(resp.cookies)
            self.authHeader = {"Authorization": f"Bearer {jsonResp['Bearer']}"}
            return True

    async def request_wrapper(
        self,
        method: str,
        url: str,
        data: dict | None = None,
    ) -> any:
        try:
            async with async_timeout.timeout(100000):
                response = await self.session_.request(
                    method=method,
                    url=url,
                    headers=self.authHeader,
                    json=data,
                )
            if response.status == 401:
                await self.login()
                # retry
                async with async_timeout.timeout(100000):
                    response = await self.session_.request(
                        method=method, url=url, headers=self.authHeader, json=data
                    )
            response.raise_for_status()
            return await response.json()
        except asyncio.TimeoutError as exception:
            raise IntegrationBlueprintApiClientCommunicationError(
                "Timeout error fetching information",
            ) from exception
        except (
            aiohttp.ClientError,
            socket.gaierror,
            aiohttp.ClientResponseError,
        ) as exception:
            raise IntegrationBlueprintApiClientCommunicationError(
                "Error fetching information",
            ) from exception
        except Exception as exception:  # pylint: disable=broad-except
            raise IntegrationBlueprintApiClientError(
                "Something really wrong happened!"
            ) from exception
