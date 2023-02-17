from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .devices import Light, Purifer, Tvoc, VacuumCleaner


if TYPE_CHECKING:
    from ..api import YandexApi


class DeviceCategories(ABC):
    @property
    def purifer(self) -> Purifer:
        return Purifer(self.api_instance)

    @property
    def vacuum_cleaner(self) -> VacuumCleaner:
        return VacuumCleaner(self.api_instance)

    @property
    def light(self) -> Light:
        return Light(self.api_instance)

    @property
    def tvoc(self) -> Tvoc:
        return Tvoc(self.api_instance)

    @property
    @abstractmethod
    def api_instance(self) -> "YandexApi":
        pass
