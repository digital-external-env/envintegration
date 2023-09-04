from .digital_hygiene import DigHugieneApi
from .physical_hygiene import PhyHugiyeneApi


class HugyieneApi:
    @staticmethod
    def get_phy_hugyiene() -> PhyHugiyeneApi:
        return PhyHugiyeneApi

    @staticmethod
    def get_dig_hugyiene() -> DigHugieneApi:
        return DigHugieneApi
