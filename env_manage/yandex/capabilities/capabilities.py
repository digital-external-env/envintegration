from dataclasses import dataclass
from enum import Enum
from typing import Any


@dataclass
class BaseCapability:
    type: str

    @property
    def _type(self) -> str:
        return f"devices.capabilities.{self.type}"


@dataclass
class OnOff(BaseCapability):
    value: bool
    instance: str = "on"

    @property
    def state(self) -> dict[str, Any]:
        return {"instance": self.instance, "value": self.value}

    def __call__(self) -> dict[str, Any]:
        return {"type": self._type, "state": self.state}


class ModeFunctions(str, Enum):
    cleanup_mode = "cleanup_mode"
    coffee_mode = "coffee_mode"
    dishwashing = "dishwashing"
    fan_speed = "fan_speed"
    heat = "heat"
    input_source = "input_source"
    program = "program"
    swing = "swing"
    tea_mode = "tea_mode"
    thermostat = "thermostat"
    work_speed = "work_speed"


@dataclass
class Mode(BaseCapability):
    value: str
    instance: str

    @property
    def state(self) -> dict[str, Any]:
        return {"instance": self.instance, "value": self.value}

    def __call__(self) -> dict[str, Any]:
        return {"type": self._type, "state": self.state}


class ToggleFunctions(str, Enum):
    backlight = "backlight"
    controls_locked = "controls_locked"
    ionization = "ionization"
    keep_warm = "keep_warm"
    mute = "mute"
    oscillation = "oscillation"
    pause = "pause"


@dataclass
class Toggle(BaseCapability):
    value: bool
    instance: str

    @property
    def state(self) -> dict[str, Any]:
        return {"instance": self.instance, "value": self.value}

    def __call__(self) -> dict[str, Any]:
        return {"type": self._type, "state": self.state}


class RangeFunctions(str, Enum):
    brightness = "brightness"
    channel = "channel"
    humidity = "humidity"
    open = "open"
    temperature = "temperature"
    volume = "volume"


@dataclass
class Range(BaseCapability):
    value: Any
    instance: str

    @property
    def state(self) -> dict[str, Any]:
        return {"instance": self.instance, "value": self.value}

    def __call__(self) -> dict[str, Any]:
        return {"type": self._type, "state": self.state}


class ColorFunctions(str, Enum):
    hsv = "hsv"
    rgb = "rgb"
    temperature_k = "temperature_k"
    scene = "scene"


@dataclass
class ColorSetting(BaseCapability):
    value: Any
    instance: str

    @property
    def state(self) -> dict[str, Any]:
        return {"instance": self.instance, "value": self.value}

    def __call__(self) -> dict[str, Any]:
        return {"type": self._type, "state": self.state}


@dataclass
class ServerAction(BaseCapability):
    value: Any
    istance: str = "text_action"

    @property
    def state(self) -> dict[str, Any]:
        return {"instance": self.istance, "value": self.value}

    def __call__(self) -> dict[str, Any]:
        return {"type": self._type, "state": self.state}
