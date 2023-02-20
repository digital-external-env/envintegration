import asyncio
import json
from typing import Any

import aiohttp

from .types import GoogleTypes
from .utils import (
    minimal_point,
    minimal_session,
    upgrade_point,
    upgrade_session,
)


class GoogleFit:
    google_fit_url = "https://fitness.googleapis.com/fitness/v1/users/me"
    google_types = GoogleTypes()

    def __init__(self, token: str) -> None:
        self.token = token
        self.response: aiohttp.ClientResponse
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.loop = asyncio.get_event_loop_policy().get_event_loop()
        self.session = self.loop.run_until_complete(self._init_session())

    def __del__(self) -> None:
        self.loop.run_until_complete(self._close_session())

    async def _init_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(loop=self.loop, headers=self.headers)

    async def _close_session(self) -> None:
        await self.session.close()

    async def _get_sessions(self) -> Any:
        self.response = await self.session.get(
            self.google_fit_url + "/sessions"
        )
        return await self.response.json()

    async def _get_sessions_by_type(self, type: int) -> list[dict[str, Any]]:
        sessions = await self._get_sessions()
        result: list[dict[str, Any]] = []
        for session in sessions["session"]:
            if session["activityType"] == type:
                upgrade_session(session)
                minimal_session(session)
                result.append(session)
        return result

    async def _get_sleeps_and_phases(self) -> list[dict[str, Any]]:
        """Get all the dreams and phases"""
        sleep_sessions = await self.get_sleeps()
        for sleep in sleep_sessions:
            sleep["phases"] = await self.get_sleep_phases(
                sleep["start_time"], sleep["end_time"]
            )
        return sleep_sessions

    async def _get_sleeps_phases_for(
        self, sleep_sessions: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """For the convenience of the user, get access to certain dreams"""
        for sleep in sleep_sessions:
            sleep["phases"] = await self.get_sleep_phases(
                sleep["start_time"], sleep["end_time"]
            )
        return sleep_sessions

    async def _get_walks_and_steps(
        self, duration: int = google_types.duration_type["7days"]
    ) -> list[Any]:
        result: list[Any] = []
        walk_sessions = await self.get_walks()
        for walk in walk_sessions:
            walk["steps"] = await self.get_steps(
                walk["start_time"], walk["end_time"], duration
            )
            result.append(walk["steps"][0])
        return result

    async def _get_data_sources_and_data_point_changes(
        self, data_sources: dict[str, Any]
    ) -> dict[str, Any]:
        """Get all data_sources and all Pointers"""
        for data_source in data_sources["dataSource"]:
            data_source["Points"] = await self.get_data_point_changes(
                data_source["dataStreamId"]
            )
        return data_sources

    async def _get_data_sources_filters(
        self, data_sources: dict[str, Any], filter_names: list[str]
    ) -> dict[str, Any]:
        """Get specific data_sources by the data_source_names list"""
        sort_data_source: dict[str, Any] = {}
        for name in filter_names:
            sort_data_source[name] = {"lenght": 0}
        for data_source in data_sources["dataSource"]:
            index = data_source["dataType"]["name"]
            sort_data_source[index].update(
                {sort_data_source[index]["lenght"]: data_source}
            )
            sort_data_source[index].update(
                {"lenght": sort_data_source[index]["lenght"] + 1}
            )
        return sort_data_source

    async def get_sleep_phases(self, start_time: int, end_time: int) -> Any:
        """Get to a certain dream of its sleep phase"""
        start_time = start_time * 1000
        end_time = end_time * 1000
        data = {
            "aggregateBy": [{"dataTypeName": "com.google.sleep.segment"}],
            "endTimeMillis": end_time,
            "startTimeMillis": start_time,
        }
        self.response = await self.session.post(
            self.google_fit_url + "/dataset:aggregate", data=json.dumps(data)
        )

        result: dict[str, Any] = await self.response.json()
        for phase in result["bucket"][0]["dataset"][0]["point"]:
            upgrade_point(phase)
            minimal_point(phase)
            phase.update(
                value=self.google_types.sleep_stages[
                    phase["value"][0]["intVal"]
                ]
            )
        return result["bucket"][0]["dataset"][0]["point"]

    async def get_sleeps(self) -> list[dict[str, Any]]:
        """Will get all the dreams"""
        return await self._get_sessions_by_type(
            self.google_types.activity_type["Сон"]
        )

    async def get_steps(
        self,
        start_time: int,
        end_time: int,
        duration: int = google_types.duration_type["7days"],
    ) -> Any:
        start_time = start_time * 1000
        end_time = end_time * 1000
        data = {
            "aggregateBy": [
                {
                    "dataTypeName": "com.google.step_count.delta",
                    "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps",
                }
            ],
            "bucketByTime": {"durationMillis": duration},
            "startTimeMillis": start_time,
            "endTimeMillis": end_time,
        }
        self.response = await self.session.post(
            self.google_fit_url + "/dataset:aggregate", data=json.dumps(data)
        )

        result: dict[str, Any] = await self.response.json()
        for step in result["bucket"][0]["dataset"][0]["point"]:
            upgrade_point(step)
            minimal_point(step)
            step.update(value=step["value"][0]["intVal"])
        return result["bucket"][0]["dataset"][0]["point"]

    async def get_walks(self) -> list[dict[str, Any]]:
        sessions = await self._get_sessions()
        result: list[dict[str, Any]] = []
        for session in sessions["session"]:
            if (
                session["activityType"]
                == self.google_types.activity_type["Ходьба"]
                or session["activityType"]
                == self.google_types.activity_type["Другая активность"]
            ):
                upgrade_session(session)
                minimal_session(session)
                result.append(session)
        return result

    async def get_data_sources(self) -> Any:
        """Get all data_sources"""
        self.response = await self.session.get(
            self.google_fit_url + "/dataSources"
        )
        return await self.response.json()

    async def get_data_sources_filter(
        self, data_sources: dict[str, Any], data_sourse_name: str
    ) -> list[Any]:
        """Get specific data_sources by one data_sourse_name"""
        filter_data_sources: list[Any] = []
        for _, data_source in enumerate(data_sources["dataSource"]):
            if data_source["dataType"]["name"] == data_sourse_name:
                filter_data_sources.append(data_source)
        return filter_data_sources

    async def get_data_point_changes(self, data_sources_id: str) -> Any:
        """Get to a specific data_sources all Pointers"""
        self.response = await self.session.get(
            self.google_fit_url
            + "/dataSources/"
            + data_sources_id
            + "/dataPointChanges"
        )
        return await self.response.json()
