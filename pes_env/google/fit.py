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
    google_fit_url = 'https://fitness.googleapis.com/fitness/v1/users/me'
    google_fit_session_url = 'https://fitness.googleapis.com/fitness/v1/users/me/sessions'
    google_fit_data_sources_url = 'https://www.googleapis.com/fitness/v1/users/me/dataSources/'
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

    async def _get_sessions(self) -> Dict[str, Any]:
        self.response = await self.session.get(self.google_fit_session_url)
        result = await self.response.json()
        next_page_token = result['nextPageToken']
        real_result = {}
        index = 0
        for session in result['session']:
            session = _upgrade_session(session)
            session = _minimal_session(session)
            real_result.update({index: session})
            index += 1

        while (next_page_token):
            self.response = await self.session.get(
                self.google_fit_session_url
                + "/?pageToken="
                + next_page_token)
            if self.response.status != 400:
                temp_result = await self.response.json()
                if not len(temp_result['session']):
                    break
                next_page_token = temp_result['nextPageToken']
                for session in temp_result['session']:
                    session = _upgrade_session(session)
                    session = _minimal_session(session)
                    real_result.update({index: session})
                    index += 1
            else:
                break

        return real_result

    async def _get_sessions_by_type(self, type: int) -> Dict[str, Any]:
        sessions = await self._get_sessions()
        result = {}
        index = 0
        for session in sessions.values():
            if session['activityType'] == type:
                result.update({index: session})
                index += 1
        return result

    async def _get_sleeps(self) -> Dict[str, Any]:
        return await self._get_sessions_by_type(activityType['Сон'])

    async def _get_sleep_phases(self, start_time: int, end_time: int) -> Dict[str, Any]:
        start_time = start_time * 1000
        end_time = end_time * 1000
        data = {
            "aggregateBy": [{"dataTypeName": "com.google.sleep.segment"}],
            "endTimeMillis": end_time,
            "startTimeMillis": start_time
        }
        self.response = await self.session.post(self.google_fit_url + '/dataset:aggregate', data=json.dumps(data))

        result = await self.response.json()
        for phase in result['bucket'][0]['dataset'][0]['point']:
            phase = _upgrade_point(phase)
            phase = _minimal_point(phase)
            phase.update(value=sleepStages[phase['value'][0]['intVal']])
        return result['bucket'][0]['dataset'][0]['point']

    async def _get_sleeps_and_phases(self) -> Dict[str, Any]:
        sleep_sessions = await self._get_sleeps()
        for sleep in sleep_sessions.values():
            sleep['phases'] = await self._get_sleep_phases(sleep['start_time'], sleep['end_time'])
        return sleep_sessions

    async def get_sleeps_and_phases_by_time(self, start_data_time: int, end_data_time: int) -> Dict[str, Any]:
        sleep_sessions = await self._get_sleeps()
        result = {}
        index = 0
        for sleep in sleep_sessions.values():
            if sleep['start_time'] >= start_data_time and sleep['end_time'] <= end_data_time:
                sleep['phases'] = await self._get_sleep_phases(sleep['start_time'], sleep['end_time'])
                result.update({index: sleep})
                index += 1
        return result

    async def _get_sleeps_phases_for(
            self, sleep_sessions: dict[str, Any]
    ) -> dict[str, Any]:
        if not (type(sleep_sessions) is dict):
            return "Invalid type of input data"
        for sleep in sleep_sessions.values():
            sleep['phases'] = await self._get_sleep_phases(sleep['start_time'], sleep['end_time'])
        return sleep_sessions

    async def _get_walks(self) -> dict[str, Any]:
        sessions = await self._get_sessions()
        result = {}
        index = 0
        for session in sessions.values():
            if session['activityType'] == activityType['Ходьба']\
                    or session['activityType'] == activityType['Другая активность']:
                result.update({index: session})
                index += 1
        return result
    
    async def _get_walks_and_steps(
            self, duration: int = google_types.duration_type["7days"]
    ) -> dict[str, Any]:
        walk_sessions = await self._get_walks()
        result = {}
        index = 0
        for walk in walk_sessions.values():
            walk['step'] = await self._get_steps(walk['start_time'], walk['end_time'], duration)
            if walk['step'] == None:
                continue
            result.update({index: walk['step']})
            index += 1
        return result

    async def _get_data_point_changes(self, data_sources_id: str) -> dict[str, Any]:
        self.response = await self.session.get(
            self.google_fit_data_sources_url
            + data_sources_id
            + '/dataPointChanges')
        result = await self.response.json()
        next_page_token = result['nextPageToken']
        real_result = {}
        index = 0
        for point in result['insertedDataPoint']:
            point = _upgrade_point(point)
            point = _minimal_point(point)
            real_result.update({index: point})
            index += 1

        while (next_page_token):
            self.response = await self.session.get(
                self.google_fit_data_sources_url
                + data_sources_id
                + '/dataPointChanges'
                + "/?pageToken="
                + next_page_token)
            if self.response.status != 400:
                temp_result = await self.response.json()
                next_page_token = temp_result['nextPageToken']
                for point in temp_result['insertedDataPoint']:
                    point = _upgrade_point(point)
                    point = _minimal_point(point)
                    real_result.update({index: point})
                    index += 1
            else:
                break

        return real_result
    
    async def _get_data_sources(self) -> dict[str, Any]:
        self.response = await self.session.get(self.google_fit_data_sources_url)
        data_sources = await self.response.json()
        result = {}
        index = 0
        for data_source in data_sources['dataSource']:
            result.update({index: data_source})
            index += 1
        return result
    
    async def _get_data_sources_and_data_point_changes(
            self, data_sources: dict[str, Any]
    ) -> dict[str, Any]:
        for data_source in data_sources.values():
            data_source['Points'] = await self._get_data_point_changes(data_source['dataStreamId'])
        return data_sources

    async def _get_data_sources_filters(
            self, data_sources: dict[str, Any], filter_names: list[str]
    ) -> dict[str, Any]:
        if type(filter_names) is str:
            filter_data_sources = {}
            index = 0
            for data_source in data_sources.values():
                if data_source['dataType']['name'] == filter_names:
                    filter_data_sources.update({index: data_source})
                    index += 1
            return filter_data_sources

        if type(filter_names) is set:
            sort_data_source = {}
            for name in filter_names:
                sort_data_source[name] = {'lenght': 0}
            for data_source in data_sources.values():
                index = data_source['dataType']['name']
                if index in sort_data_source:
                    sort_data_source[index].update({sort_data_source[index]['lenght']: data_source})
                    sort_data_source[index].update({'lenght': sort_data_source[index]['lenght'] + 1})
            return sort_data_source

    async def _get_sr_znach_by_pulses(self, pulses: dict[str, Any]) -> Float:
        S = 0
        for pulse in pulses.values():
            S = S + pulse['value']
        if S > 1:
            return S / len(pulses)
        else:
            return S
