from .device_mode import SmartSpeakerCommand
from .light_mode import LightManager
from .ml_components import SleepModel


class PhyHugiyeneApi:
    @staticmethod
    def get_smart_speaker_cmd(text: str) -> SmartSpeakerCommand:
        return SmartSpeakerCommand(text)

    @staticmethod
    def get_light_manager() -> LightManager:
        return LightManager

    @staticmethod
    def get_sleep_model() -> SleepModel:
        return SleepModel()
