import json
from abc import ABC
from typing import Any

import aiohttp

from .devices import DeviceCategories


class ABCAPI(DeviceCategories, ABC):
    @property
    def api_instance(self) -> "ABCAPI":  # type: ignore
        return self


class YandexApi(ABCAPI):
    def __init__(
        self,
        client_token: str,
        host: str = "https://api.iot.yandex.net",
        version: str = "/v1.0",
    ) -> None:
        self.client_token = client_token
        self.host = host
        self.headers = {"Authorization": "Bearer {}".format(client_token)}
        self.version = version

    async def get_smart_home_info(
        self, resource: str = "/user/info"
    ) -> dict[Any, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.host}{self.version}{resource}"
            ) as response:
                result: dict[Any, Any] = await response.json()
                return result

    async def get_device_info(
        self, device_id: str, resource: str = "/devices/"
    ) -> dict[Any, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.host}{self.version}{resource}{device_id}"
            ) as response:
                result: dict[Any, Any] = await response.json()
                return result

    async def get_group_info(
        self, group_id: str, resource: str = "/groups/"
    ) -> dict[Any, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(
                f"{self.host}{self.version}{resource}{group_id}"
            ) as response:
                result: dict[Any, Any] = await response.json()
                return result

    async def delete_device(
        self, device_id: str, resource: str = "/devices/"
    ) -> dict[Any, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.delete(
                f"{self.host}{self.version}{resource}{device_id}"
            ) as response:
                result: dict[Any, Any] = await response.json()
                return result

    async def devices_action(
        self,
        device_id: str,
        actions: list[dict[Any, Any]],
        resource: str = "/devices/actions",
    ) -> dict[Any, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            data = {"devices": [{"id": f"{device_id}", "actions": actions}]}

            async with session.post(
                f"{self.host}{self.version}{resource}", data=json.dumps(data)
            ) as response:
                result: dict[Any, Any] = await response.json()
                return result

    async def group_action(
        self, group_id: str, data: dict[Any, Any], resource: str = "/groups/"
    ) -> dict[Any, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.host}{self.version}{resource}{group_id}/actions",
                data=json.dumps(data),
            ) as response:
                result: dict[Any, Any] = await response.json()
                return result

    async def scenario_action(
        self, scenario_id: str, resource: str = "/scenarios/"
    ) -> dict[Any, Any]:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(
                f"{self.host}{self.version}{resource}{scenario_id}/actions"
            ) as response:
                result: dict[Any, Any] = await response.json()
                return result
