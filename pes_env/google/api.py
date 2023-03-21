from typing import Any
from typing import Tuple

from .fit import GoogleFit
from .utils import minimal_point_data_sourse, upgrade_point_data_sourse


class GoogleFitApi:
    def __init__(self, token: str) -> None:
        self.fit = GoogleFit(token)

    async def get_sleeps_and_phases_by_time(
            self, start_data_time: int, end_data_time: int
    ) -> dict[str, Any]:
        """
        Get data about the user's sleep and sleep phase.
        Args:
            start_data_time (int): Sleep start time to search
            end_data_time (int): Sleep end time to search
        Returns:
            dict: data about the user's sleep and sleep phase.
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

    async def get_steps_from_walks(
            self, duration: int = GoogleFit.google_types.duration_type["7days"]
    ) -> int:
        """
        Get number of steps for all walks
        Args:
            duration (int): Walking range
        Returns:
            int: Number of steps for all walks
        """
        result = 0
        walk_sessions = await self._get_walks()
        for walk in walk_sessions.values():
            walk['step'] = await self._get_steps(walk['start_time'], walk['end_time'], duration)
            if walk['step'] == None:
                continue
            result = result + walk['step']['value']
        return result

    async def get_heart_points_by_time(self, start_time: int, end_time: int) -> dict[str, Any]:
        """
        Get heartbeat points for a certain period
        Args:
            start_time (int): Heartbeat start time to search
            end_time (int): Heartbeat end time to search
        Returns:
            Dict: dict of user's Heartbeat recordings
        """
        data_sources = await self._get_data_sources()
        data_sources_heart = await self._get_data_sources_filter(data_sources, 'com.google.heart_minutes')
        data_sources_heart_points = await self._get_data_sources_and_data_point_changes(data_sources_heart)
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

    async def get_pulses_by_time(self, start_time: int, end_time: int) -> Tuple[dict[str, Any], float]:
        """
        Get all heart rate values for a certain period
        Args:
            start_time (int): Pulse start time to search
            end_time (int): Pulse end time to search
        Returns:
            Dict: dict of user's Last pulse recordings
        """
        data_sources = await self._get_data_sources()
        data_sources_heart_rate = await self._get_data_sources_filter(data_sources, 'com.google.heart_rate.bpm')
        data_sources_heart_rate_points = await self._get_data_sources_and_data_point_changes(data_sources_heart_rate)
        pulse = {}
        index = 0
        for record in data_sources_heart_rate_points.values():
            for point in record['Points'].values():
                if (start_time <= point['start_time']) and (end_time >= point['start_time']):
                    index = index + 1
                    point.update(value=point['value'][0]['fpVal'])
                    pulse.update({index: point})
        result = dict(sorted(pulse.items(), key=lambda x: x[1].get("start_time")))

        if len(result) != 0:
            average = await self._get_average_by_pulses(result)
            return result, average
        else:
            return result, 0

    async def get_pulse_by_time(self, start_time: int, end_time: int) -> dict[str, Any]:
        """
        Get all heart rate values for a certain period
        Args:
            start_time (int): Pulse start time to search
            end_time (int): Pulse end time to search
        Returns:
            Dict: dict of user's Last pulse recording
        """
        pulse, average = await self.get_pulses_by_time(start_time, end_time)
        return pulse.popitem()

    async def get_pulses_by_time_with_duration(self, start_time: int, end_time: int,
                                               duration: int) -> Tuple[dict[str, Any], float]:
        """
        Get all heart rate values for a certain period,
        taking into account the additional range
        Args:
            start_time (int): Pulse start time to search
            end_time (int): Pulse end time to search
            duration (int): duration to search
        Returns:
            Dict: dict of user's Last pulse recordings
        """
        pulse, average = await self.get_pulses_by_time(start_time, end_time)
        if len(pulse) == 0:
            pulse, average = await self.get_pulses_by_time(start_time - duration, end_time)
            return pulse, average
        else:
            return pulse, average

    async def get_pulse_by_time_with_duration(self, start_time: int, end_time: int,
                                              duration: int) -> dict[str, Any]:
        """
        Get the nearest pulse value for a certain period,
        taking into account the additional range
        Args:
            start_time (int): Pulse start time to search
            end_time (int): Pulse end time to search
            duration (int): duration to search
        Returns:
            Dict: dict of user's Last pulse recording
        """
        pulse, average = await self.get_pulses_by_time(start_time, end_time)
        if len(pulse) == 0:
            pulse = await self.get_pulses_by_time(start_time - duration, end_time)
        return pulse.popitem()

    async def get_heights(self) -> list[dict[str, Any]]:
        """
        Get a list of the user's height
        Args:
            None
        Returns:
            list: dict of user's height in different records
        """
        result = []
        dataSources = await self.fit.get_data_sources()
        heights = await self.fit.get_data_sources_filter(
            dataSources, self.fit.google_types.data_types["рост"]
        )
        for height in heights:
            height["Points"] = await self.fit.get_data_point_changes(
                height["dataStreamId"]
            )
            for point in height["Points"]["insertedDataPoint"]:
                upgrade_point_data_sourse(point)
                minimal_point_data_sourse(point)
                point.update(value=int(point["value"][0]["fpVal"] * 100))
                result.append(point)
        return result

    async def get_weights(self) -> list[dict[str, Any]]:
        """
        Get a list of the user's weight
        Args:
            None
        Returns:
            list: dict of user's weight in different records
        """
        result = []
        dataSources = await self.fit.get_data_sources()
        weights = await self.fit.get_data_sources_filter(
            dataSources, self.fit.google_types.data_types["вес"]
        )
        for weight in weights:
            weight["Points"] = await self.fit.get_data_point_changes(
                weight["dataStreamId"]
            )
            for point in weight["Points"]["insertedDataPoint"]:
                upgrade_point_data_sourse(point)
                minimal_point_data_sourse(point)
                point.update(value=int(point["value"][0]["fpVal"]))
                result.append(point)
        return
