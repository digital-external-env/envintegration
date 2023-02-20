from datetime import datetime
from typing import Any


# TODO: добавить проверки вида if key in dic: del dic['key']


def _clean_dict(dict_: dict[str, Any], keys: list[str]) -> None:
    for key in keys:
        if dict_.get(key):
            del dict_[key]


def upgrade_session(session: dict[str, Any]) -> None:
    session["time"] = (
        (int(session["endTimeMillis"]) - int(session["startTimeMillis"]))
        / 1000
        / 60
        / 60
    )
    session["start_time"] = int(int(session["startTimeMillis"]) / 1000)
    session["end_time"] = int(int(session["endTimeMillis"]) / 1000)
    session["data_start"] = datetime.fromtimestamp(session["start_time"])
    session["data_end"] = datetime.fromtimestamp(session["end_time"])


def upgrade_point(point: dict[str, Any]) -> None:
    point["start_time"] = int(int(point["startTimeNanos"]) / 1000 / 1000 / 1000)
    point["end_time"] = int(int(point["endTimeNanos"]) / 1000 / 1000 / 1000)
    point["time"] = int((point["end_time"] - point["start_time"]) / 60)
    point["data_start"] = datetime.fromtimestamp(point["start_time"])
    point["data_end"] = datetime.fromtimestamp(point["end_time"])


def upgrade_point_data_sourse(point: dict[str, Any]) -> None:
    point["time"] = int(int(point["startTimeNanos"]) / 1000 / 1000 / 1000)
    point["data"] = datetime.fromtimestamp(point["time"])


def minimal_session(session: dict[str, Any]) -> None:
    extra_keys = [
        "id",
        "name",
        "description",
        "startTimeMillis",
        "endTimeMillis",
        "modifiedTimeMillis",
        "application",
        "activityType",
    ]
    _clean_dict(session, extra_keys)


def minimal_point(point: dict[str, Any]) -> None:
    extra_keys = [
        "startTimeNanos",
        "endTimeNanos",
        "modifiedTimeMillis",
        "dataTypeName",
        "originDataSourceId",
    ]
    _clean_dict(point, extra_keys)


def minimal_point_data_sourse(point: dict[str, Any]) -> None:
    extra_keys = [
        "startTimeNanos",
        "endTimeNanos",
        "modifiedTimeMillis",
        "dataTypeName",
        "originDataSourceId",
    ]
    _clean_dict(point, extra_keys)
