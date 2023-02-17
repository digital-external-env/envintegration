import asyncio
import re
from typing import Any

import aiohttp
import requests


class YandexSession:
    quasar_url = "https://iot.quasar.yandex.ru/m/user"
    music_url = "https://api.music.yandex.net"
    session = requests.session()
    csrf_token = None
    music_uid = 0
    login = ""
    password = ""  # nosec B105

    def __init__(self, login: str, password: str, station_id: str) -> None:
        self.login = login
        self.password = password
        self.station_id = station_id
        self.session.headers.update(
            {"User-Agent": "Chrome", "Host": "passport.yandex.ru"}
        )

        resp_app_platform = self.session.get(
            "https://passport.yandex.ru/am?app_platform=android"
        )
        m = re.search(r'"csrf_token" value="([^"]+)"', resp_app_platform.text)
        auth_payload = {"csrf_token": m[1] if m else ""}
        self.csrf_token = m[1] if m else ""

        resp_auth = self.session.post(
            "https://passport.yandex.ru/registration-validations/auth/multi_step/start",
            {**auth_payload, "login": login},
        ).json()

        auth_payload["track_id"] = resp_auth["track_id"]

        self.session.post(
            "https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password",
            {
                **auth_payload,
                "password": password,
                "retpath": "https://passport.yandex.ru/am/finish?status=ok&from=Login",
            },
        )

    def _update_csrf(self) -> None:
        raw = self.session.get("https://yandex.ru/quasar").text
        m = re.search('"csrfToken2":"(.+?)"', raw)
        self.csrf_token = m[1] if m else ""

    def get_scenarios(self) -> Any:
        return self.session.get(self.quasar_url + "/scenarios").json()[
            "scenarios"
        ]

    def get_speakers(self) -> Any:
        return self.session.get(self.quasar_url + "/devices").json()["speakers"]

    def add_scenario(
        self,
        scenario_name: str,
        activation_command: str,
        instance: str,
        value: str,
    ) -> Any:
        """
        instance: 'text_action' or 'phrase_action'
        """
        logic = {
            "type": "devices.capabilities.quasar.server_action",
            "state": {
                "instance": instance,
                "value": value,
            },
        }
        payload = self.create_scenario(
            scenario_name=scenario_name,
            activation_command=activation_command,
            logic=logic,
        )
        self._update_csrf()
        return self.session.post(
            self.quasar_url + "/scenarios",
            json=payload,
            headers={"x-csrf-token": self.csrf_token},
        ).json()

    def update_scenario(
        self,
        scenario_id: str,
        scenario_name: str,
        activation_command: str,
        instance: str,
        value: str,
    ) -> None:
        logic = {
            "type": "devices.capabilities.quasar.server_action",
            "state": {
                "instance": instance,
                "value": value,
            },
        }
        payload = self.create_scenario(
            scenario_name=scenario_name,
            activation_command=activation_command,
            logic=logic,
        )
        self._update_csrf()
        self.session.put(
            self.quasar_url + "/scenarios/" + scenario_id,
            json=payload,
            headers={"x-csrf-token": self.csrf_token},
        )

    def delete_scenario(self, scenario_id: str) -> None:
        self._update_csrf()
        self.session.delete(
            self.quasar_url + "/scenarios/" + scenario_id,
            headers={"x-csrf-token": self.csrf_token},
        )

    def exec_scenario(self, scenario_id: str) -> Any:
        self._update_csrf()
        return self.session.post(
            self.quasar_url + "/scenarios/" + scenario_id + "/actions",
            headers={"x-csrf-token": self.csrf_token},
        ).json()

    def create_scenario(
        self, scenario_name: str, activation_command: str, logic: dict[Any, Any]
    ) -> dict[str, Any]:
        return {
            "name": scenario_name,
            "icon": "home",
            "triggers": [
                {"type": "scenario.trigger.voice", "value": activation_command}
            ],
            "steps": [
                {
                    "type": "scenarios.steps.actions",
                    "parameters": {
                        "requested_speaker_capabilities": [],
                        "launch_devices": [
                            {"id": self.station_id, "capabilities": [logic]}
                        ],
                    },
                }
            ],
        }


class YandexSessionAsync:
    quasar_url = "https://iot.quasar.yandex.ru/m/user"
    music_url = "https://api.music.yandex.net"
    csrf_token = None
    music_uid = 0
    login = ""
    password = ""  # nosec B105

    def __init__(self, login: str, password: str, station_id: str) -> None:
        self.login = login
        self.password = password
        self.station_id = station_id
        self.headers = {"User-Agent": "Chrome", "Host": "passport.yandex.ru"}

        self.loop = asyncio.get_event_loop_policy().get_event_loop()
        self.session = self.loop.run_until_complete(self.init_session())

    async def init_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(loop=self.loop)

    async def close_session(self) -> None:
        await self.session.close()

    def __del__(self) -> None:
        self.loop.run_until_complete(self.close_session())

    async def authorize(self) -> None:
        resp_app_platform = await self.session.get(
            url="https://passport.yandex.ru/am?app_platform=android"
        )
        resp_text = await resp_app_platform.text()
        m = re.search(r'"csrf_token" value="([^"]+)"', resp_text)

        auth_payload = {"csrf_token": m[1] if m else ""}
        self.csrf_token = m[1] if m else ""

        resp_auth = await self.session.post(
            "https://passport.yandex.ru/registration-validations/auth/multi_step/start",
            data={"csrf_token": self.csrf_token, "login": self.login},
        )
        resp_auth_json = await resp_auth.json()
        auth_payload["track_id"] = resp_auth_json["track_id"]

        await self.session.post(
            "https://passport.yandex.ru/registration-validations/auth/multi_step/commit_password",
            data={
                "csrf_token": self.csrf_token,
                "track_id": auth_payload.get("track_id"),
                "password": self.password,
                "retpath": "https://passport.yandex.ru/am/finish?status=ok&from=Login",
            },
        )

    async def _update_csrf(self) -> None:
        response = await self.session.get("https://yandex.ru/quasar")
        raw = await response.text()
        m = re.search('"csrfToken2":"(.+?)"', raw)
        self.csrf_token = m[1] if m else ""

    async def get_scenarios(self) -> Any:
        response = await self.session.get(self.quasar_url + "/scenarios")
        resp = await response.json()
        scenarios = resp.get("scenarios")
        return scenarios

    async def get_speakers(self) -> Any:
        response = await self.session.get(self.quasar_url + "/devices")
        resp = await response.json()
        speakers = resp.get("speakers")
        return speakers

    async def add_scenario(
        self,
        scenario_name: str,
        activation_command: str,
        instance: str,
        value: str,
    ) -> str:
        """
        instance: 'text_action' or 'phrase_action'
        """
        logic = {
            "type": "devices.capabilities.quasar.server_action",
            "state": {
                "instance": instance,
                "value": value,
            },
        }
        payload = await self.create_scenario(
            scenario_name=scenario_name,
            activation_command=activation_command,
            logic=logic,
        )
        await self._update_csrf()
        response = await self.session.post(
            self.quasar_url + "/scenarios",
            json=payload,
            headers={"x-csrf-token": self.csrf_token},
        )
        return await response.text()

    async def update_scenario(
        self,
        scenario_id: str,
        scenario_name: str,
        activation_command: str,
        instance: str,
        value: str,
    ) -> str:
        logic = {
            "type": "devices.capabilities.quasar.server_action",
            "state": {
                "instance": instance,
                "value": value,
            },
        }
        payload = await self.create_scenario(
            scenario_name=scenario_name,
            activation_command=activation_command,
            logic=logic,
        )
        await self._update_csrf()
        response = await self.session.put(
            self.quasar_url + "/scenarios/" + scenario_id,
            json=payload,
            headers={"x-csrf-token": self.csrf_token},
        )
        return await response.text()

    async def delete_scenario(self, scenario_id: str) -> Any:
        await self._update_csrf()
        response = await self.session.delete(
            self.quasar_url + "/scenarios/" + scenario_id,
            headers={"x-csrf-token": self.csrf_token},
        )
        return await response.json()

    async def exec_scenario(self, scenario_id: str) -> Any:
        await self._update_csrf()
        response = await self.session.post(
            self.quasar_url + "/scenarios/" + scenario_id + "/actions",
            headers={"x-csrf-token": self.csrf_token},
        )
        return await response.json()

    async def create_scenario(
        self, scenario_name: str, activation_command: str, logic: dict[Any, Any]
    ) -> dict[str, Any]:
        return {
            "name": scenario_name,
            "icon": "home",
            "triggers": [
                {"type": "scenario.trigger.voice", "value": activation_command}
            ],
            "steps": [
                {
                    "type": "scenarios.steps.actions",
                    "parameters": {
                        "requested_speaker_capabilities": [],
                        "launch_devices": [
                            {"id": self.station_id, "capabilities": [logic]}
                        ],
                    },
                }
            ],
        }
