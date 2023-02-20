from typing import Any

from .fit import GoogleFit
from .utils import minimal_point_data_sourse, upgrade_point_data_sourse


class GoogleFitApi:
    def __init__(self, token: str) -> None:
        self.fit = GoogleFit(token)

    async def get_sleeps_and_phases_by_time(
        self, start_data_time: int, end_data_time: int
    ) -> list[dict[str, Any]]:
        """
        Get data about the user's sleep and sleep phase.

        Args:
            start_data_time (int): Sleep start time to search
            start_data_time (int): Sleep end time to search

        Returns:
            list: dict of data about the user's sleep and sleep phase.
        """
        sleep_sessions = await self.fit.get_sleeps()
        result: list[dict[str, Any]] = []
        for sleep in sleep_sessions:
            if (
                sleep["start_time"] >= start_data_time
                and sleep["end_time"] <= end_data_time
            ):
                sleep["phases"] = await self.fit.get_sleep_phases(
                    sleep["start_time"], sleep["end_time"]
                )
                result.append(sleep)
        return result

    async def get_steps_from_walks(
        self, duration: int = GoogleFit.google_types.duration_type["7days"]
    ) -> int:
        """
        Get number of steps for all walks
        Args:
            duration (int): Walking range

        Returns:
            int:Number of steps for all walks

        """
        result = 0
        walk_sessions = await self.fit.get_walks()
        for walk in walk_sessions:
            walk["steps"] = await self.fit.get_steps(
                walk["start_time"], walk["end_time"], duration
            )
            result += int(walk["steps"][0]["value"])
        return result

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
        return result
