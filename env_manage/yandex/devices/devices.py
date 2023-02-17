from typing import TYPE_CHECKING, Any

from ..capabilities import (
    ColorFunctions,
    ColorSetting,
    Mode,
    ModeFunctions,
    OnOff,
    Range,
    RangeFunctions,
    Toggle,
    ToggleFunctions,
)


if TYPE_CHECKING:
    from ..api import YandexApi


class BaseDevice:
    def __init__(self, api: "YandexApi"):
        self.api = api

    def set_id(self, device_id: str) -> "BaseDevice":
        self.device_id = device_id
        return self

    async def info(self) -> dict[Any, Any]:
        print(self.device_id)
        info = await self.api.get_device_info(device_id=self.device_id)
        return info

    async def get_properties(self) -> Any | None:
        info = await self.api.get_device_info(device_id=self.device_id)
        properties = info.get("properties")
        return properties

    async def get_capabilities(self) -> Any | None:
        info = await self.api.get_device_info(device_id=self.device_id)
        properties = info.get("capabilities")
        return properties

    def __call__(self) -> "BaseDevice":
        return self


class Purifer(BaseDevice):
    async def on_off(self, value: bool) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[OnOff(type="on_off", value=value)()],
        )


class VacuumCleaner(BaseDevice):
    async def on_off(self, value: bool) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[OnOff(type="on_off", value=value)()],
        )

    async def mode(self, value: str) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                Mode(
                    type="mode",
                    instance=ModeFunctions.work_speed.value,
                    value=value,
                )()
            ],
        )

    async def toggle(self, value: bool) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                Toggle(
                    type="toggle",
                    instance=ToggleFunctions.pause.value,
                    value=value,
                )()
            ],
        )


class Light(BaseDevice):
    async def on_off(self, value: bool) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[OnOff(type="on_off", value=value)()],
        )

    async def toggle(self, value: bool) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                Toggle(
                    type="toggle",
                    instance=ToggleFunctions.backlight.value,
                    value=value,
                )()
            ],
        )

    async def range(self, value: float) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                Range(
                    type="range",
                    instance=RangeFunctions.brightness.value,
                    value=value,
                )()
            ],
        )

    async def color_setting_hsv(self, value: dict[Any, Any]) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                ColorSetting(
                    type="color_setting",
                    instance=ColorFunctions.hsv.value,
                    value=value,
                )()
            ],
        )

    async def color_setting_rgb(self, value: int) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                ColorSetting(
                    type="color_setting",
                    instance=ColorFunctions.rgb.value,
                    value=value,
                )()
            ],
        )

    async def color_setting_temp(self, value: int) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                ColorSetting(
                    type="color_setting",
                    instance=ColorFunctions.temperature_k.value,
                    value=value,
                )()
            ],
        )

    async def color_setting_scene(self, value: str) -> dict[Any, Any]:
        return await self.api.devices_action(
            device_id=self.device_id,
            actions=[
                ColorSetting(
                    type="color_setting",
                    instance=ColorFunctions.scene.value,
                    value=value,
                )()
            ],
        )


class Tvoc(BaseDevice):
    pass
