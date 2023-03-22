import asyncio
import aiohttp


from typing import List, Dict

from dict import activityType, sleepStages, dataTypes, durationType
from handlers import _upgrade_session, _minimal_session, _upgrade_point, _minimal_point

class GoogleFitApi():
    token = ""
    google_fit_url =                'https://fitness.googleapis.com/fitness/v1/users/me'
    google_fit_session_url =        'https://fitness.googleapis.com/fitness/v1/users/me/sessions'
    google_fit_data_sources_url =    'https://www.googleapis.com/fitness/v1/users/me/dataSources/'

    def __init__(self, token):
        self.token = token
        self.response = None
        self.headers= {'Authorization': f"Bearer {self.token}"}
        self.loop = asyncio.get_event_loop_policy().get_event_loop()
        self.session = self.loop.run_until_complete(self.init_session())

    async def init_session(self):
        return aiohttp.ClientSession(loop=self.loop, headers=self.headers)

    async def close_session(self):
        await self.session.close()

    def __del__(self):
        self.loop.run_until_complete(self.close_session())

    async def _get_sessions(self):
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
            self.response = await self.session.get(self.google_fit_session_url + "/?pageToken=" + next_page_token)
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

    async def _get_sessions_by_type(self, type):
        sessions = await self._get_sessions()
        result = {}
        index = 0
        for session in sessions.values():
            if session['activityType'] == type:
                result.update({index: session})
                index += 1
        return result

    #получить к определенному сну его фазы сна
    async def _get_sleep_phases(self, start_time, end_time):
        start_time = start_time * 1000
        end_time = end_time * 1000
        data = {
            "aggregateBy": [
                {
                    "dataTypeName": "com.google.sleep.segment"
                }
            ],
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

    #получит все сны
    async def _get_sleeps(self):
        return await self._get_sessions_by_type(activityType['Сон'])

    #получить все сны и фазы
    async def _get_sleeps_and_phases(self):
        sleep_sessions = await self._get_sleeps()
        for sleep in sleep_sessions.values():
            sleep['phases'] = await self._get_sleep_phases(sleep['start_time'], sleep['end_time'])
        return sleep_sessions

    #получить сон и его фазы для конктреной unix эпохи
    async def get_sleeps_and_phases_by_time(self, start_data_time:int, end_data_time:int) -> Dict[int, Dict]:
        """
        Get data about the user's sleep and sleep phase.

        Args:
            start_data_time (int): Sleep start time to search
            start_data_time (int): Sleep end time to search

        Returns:
            Dict: dict of data about the user's sleep and sleep phase.
        """
        sleep_sessions = await self._get_sleeps()
        result = {}
        index = 0
        for sleep in sleep_sessions.values():
            if sleep['start_time'] >= start_data_time and sleep['end_time'] <= end_data_time:
                sleep['phases'] = await self._get_sleep_phases(sleep['start_time'], sleep['end_time'])
                result.update({index: sleep})
                index += 1
        return result

    #для удобства пользователю, получить фазы к определенным снам
    async def _get_sleeps_phases_for(self, sleep_sessions):
        #TODO: Сделать проверки типов данных
        if not (type(sleep_sessions) is dict):
            return "Invalid type of input data"
        for sleep in sleep_sessions.values():
            sleep['phases'] = await self._get_sleep_phases(sleep['start_time'], sleep['end_time'])
        return sleep_sessions

    async def _get_steps(self, start_time, end_time, duration=durationType['7days']):
        start_time = start_time * 1000
        end_time = end_time * 1000
        data = {
            "aggregateBy": [{
                   "dataTypeName": "com.google.step_count.delta",
                   "dataSourceId": "derived:com.google.step_count.delta:com.google.android.gms:estimated_steps"
                }],
            "bucketByTime": {"durationMillis": duration},
            "startTimeMillis": start_time,
            "endTimeMillis": end_time
        }
        self.response = await self.session.post(self.google_fit_url + '/dataset:aggregate', data=json.dumps(data))

        step = await self.response.json()
        points_step = step['bucket'][0]['dataset'][0]['point']
        if len(points_step):
            point_step = points_step[0]
            point_step = _upgrade_point(point_step)
            point_step = _minimal_point(point_step)
            point_step.update(value=point_step['value'][0]['intVal'])
            return point_step
        else:
            return None

    async def _get_walks(self):
        sessions = await self._get_sessions()
        result = {}
        index = 0
        for session in sessions.values():
            if session['activityType'] == activityType['Ходьба'] or session['activityType'] == activityType['Другая активность']:
                result.update({index: session})
                index += 1
        return result

    async def _get_walks_and_steps(self, duration=durationType['7days']):
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

    async def get_steps_from_walks(self, duration=durationType['7days']) -> int:
        """
            Get number of steps for all walks
            Args:
                duration (int): Walking range

            Returns:
                int:Number of steps for all walks

        """
        result = 0
        walk_sessions = await self._get_walks()
        for walk in walk_sessions.values():
            walk['step'] = await self._get_steps(walk['start_time'], walk['end_time'], duration)
            if walk['step'] == None:
                continue
            result = result + walk['step']['value']
        return result

    #получить к определенному dataSources все Pointers
    async def _get_data_point_changes(self, data_sources_id):
        self.response = await self.session.get(self.google_fit_data_sources_url + data_sources_id +  '/dataPointChanges')
        result = await self.response.json()
        next_page_token = result['nextPageToken']
        real_result = {}
        index = 0
        for point in result['insertedDataPoint']:
            point = _upgrade_point(point)
            point = _minimal_point(point)
            real_result.update({ index : point})
            index+= 1

        while (next_page_token):
            self.response = await self.session.get(self.google_fit_data_sources_url + data_sources_id + '/dataPointChanges' + "/?pageToken=" + next_page_token)
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

    #получить все dataSources
    async def _get_dataSources(self):
        self.response = await self.session.get(self.google_fit_data_sources_url)
        dataSourses = await self.response.json()
        result = {}
        index = 0
        for dataSource in dataSourses['dataSource']:
            result.update({index : dataSource})
            index+=1
        return result

    #получить все dataSources и все Pointers
    async def _get_dataSources_and_dataPointChanges(self, data_sources_filters):
        for data_source in data_sources_filters.values():
            data_source['Points'] = await self._get_data_point_changes(data_source['dataStreamId'])
        return data_sources_filters

    #получить отфильтрованные dataSources по нескольким filterNames
    async def _get_dataSources_filter(self, data_sources, filter_names):
        #если пришла строка, отсев идет изначальных данных
        if type(filter_names) is str:
            filter_data_sources = {}
            index = 0
            for data_source in data_sources.values():
                if data_source['dataType']['name'] == filter_names:
                    filter_data_sources.update({index: data_source})
                    index += 1
            return filter_data_sources

        #если пришел список строк, создаем вложенные списки с набором нужных dataSourse
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

    async def get_heart_points_by_time(self, start_time, end_time):
        data_sources = await self._get_dataSources()
        data_sources_heart = await self._get_dataSources_filter(data_sources, 'com.google.heart_minutes')
        data_sources_heart_points = await self._get_dataSources_and_dataPointChanges(data_sources_heart)
        pulse = {}
        index = 0
        for record in data_sources_heart_points.values():
            for point in record['Points'].values():
                if (start_time <= point['start_time']) and (end_time >= point['start_time']):
                    index = index + 1
                    point.update(value=point['value'][0]['fpVal'])
                    pulse.update({index: point})
        result = dict(sorted(pulse.items(), key=lambda x: x[1].get("start_time")))
        return result

    #получить средний пульс за записи о нем
    async def _get_average_by_pulses(self, pulses):
        S = 0
        for pulse in pulses.values():
            S = S + pulse['value']
        if S > 1:
            return S / len(pulses)
        else:
            return S

    #получить все значения пульса за определенный период
    async def get_pulses_by_time(self, start_time, end_time):
        data_sources = await self._get_dataSources()
        data_sources_heart_rate = await self._get_dataSources_filter(data_sources, 'com.google.heart_rate.bpm')
        data_sources_heart_rate_points = await self._get_dataSources_and_dataPointChanges(data_sources_heart_rate)
        pulse = {}
        index = 0
        for record in data_sources_heart_rate_points.values():
            for point in record['Points'].values():
                if (start_time <= point['start_time']) and (end_time >= point['start_time']):
                    index = index + 1
                    point.update(value=point['value'][0]['fpVal'])
                    pulse.update({index:point})
        result = dict(sorted(pulse.items(), key=lambda x: x[1].get("start_time")))

        if len(result) != 0:
            average = await self._get_average_by_pulses(result)
            return result, average
        else:
            return result, 0

    #получить ближайшее значение пульса за определенный период
    async def get_pulse_by_time(self, start_time, end_time):
        pulse, sr_zhach = await self.get_pulses_by_time(start_time, end_time)
        return pulse.popitem()

    #получить все значения пульса за определенный период с учетом дополнительного диапазона
    async def get_pulses_by_time_with_duration(self, start_time, end_time, duration):
        pulse, sr_zhach = await self.get_pulses_by_time(start_time, end_time)
        if len(pulse) == 0:
            pulse, average = await self.get_pulses_by_time(start_time - duration, end_time)
            return pulse, average
        else:
            return pulse, sr_zhach

    #получить ближайшее значение пульса за определенный период с учетом дополнительного диапазона
    async def get_pulse_by_time_with_duration(self, start_time, end_time, duration):
        pulse, sr_zhach = await self.get_pulses_by_time(start_time, end_time)
        if len(pulse) == 0:
            pulse = await self.get_pulses_by_time(start_time - duration, end_time)
        return pulse.popitem()

    async def get_heights(self) -> List[Dict]:
        """
        Get a list of the user's height

        Args:
            None

        Returns:
            list: dict of user's height in different records
        """
        result = []
        dataSources = await self._get_dataSources()
        heights = await self._get_dataSources_filter(dataSources, dataTypes['рост'])
        for height in heights.values():
            height['Points'] = await self._get_data_point_changes(height['dataStreamId'])
            for point in height['Points'].values():
                point.update(value =  int(point['value'][0]['fpVal']*100))
                result.append(point)
        return result

    async def get_weights(self) -> List[Dict]:
        """
        Get a list of the user's weight

        Args:
            None

        Returns:
            list: dict of user's weight in different records
        """
        result = []
        dataSources = await self._get_dataSources()
        weights = await self._get_dataSources_filter(dataSources, dataTypes['вес'])
        for weight in weights.values():
            weight['Points'] = await self._get_data_point_changes(weight['dataStreamId'])
            for point in weight['Points'].values():
                point.update(value =  int(point['value'][0]['fpVal']))
                result.append(point)
        return result