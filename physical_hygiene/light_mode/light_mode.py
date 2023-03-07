from dataclasses import dataclass
from datetime import time
from pprint import pprint
from typing import Union, List


@dataclass
class LightModes:
    step: int
    duration: Union[time, None]
    light_temperature: int
    light_intensity: int
    need_to_rest: bool = False


def light_mode_with_stress_index(stress_index: int, sleep_duration: time, current_time: time) -> List[LightModes]:
    if current_time < time(hour=10):
        step1 = LightModes(step=1,
                           duration=time(minute=15),
                           light_temperature=4000,
                           light_intensity=500)
        step2 = LightModes(step=2,
                           duration=time(minute=15),
                           light_temperature=7000,
                           light_intensity=1000)
        step3 = LightModes(step=3,
                           duration=None,
                           light_temperature=4000,
                           light_intensity=500)
        return [step1, step2, step3]

    elif time(hour=10) <= current_time < time(hour=15):
        if sleep_duration < time(hour=6):
            return [LightModes(step=1,
                               duration=None,
                               light_temperature=4000,
                               light_intensity=500)]
        else:
            if stress_index <= 39:
                step1 = LightModes(step=1,
                                   duration=time(minute=15),
                                   light_temperature=6000,
                                   light_intensity=750)
            elif 40 <= stress_index <= 59:
                return [LightModes(step=1,
                                   duration=None,
                                   light_temperature=4000,
                                   light_intensity=500)]
            elif 60 <= stress_index <= 79:
                step1 = LightModes(step=1,
                                   duration=time(minute=30),
                                   light_temperature=3500,
                                   light_intensity=350)
            elif 80 <= stress_index <= 100:
                step1 = LightModes(step=1,
                                   duration=time(minute=30),
                                   light_temperature=3500,
                                   light_intensity=350,
                                   need_to_rest=True)
            else:
                raise ValueError

            step2 = LightModes(step=2,
                               duration=None,
                               light_temperature=4000,
                               light_intensity=500)

            return [step1, step2]

    elif time(hour=15) <= current_time < time(hour=20):
        if sleep_duration < time(hour=6):
            return [LightModes(step=1,
                               duration=None,
                               light_temperature=4000,
                               light_intensity=500)]
        else:
            if stress_index <= 39:
                return [LightModes(step=1,
                                   duration=None,
                                   light_temperature=4000,
                                   light_intensity=500)]
            elif 40 <= stress_index <= 59:
                return [LightModes(step=1,
                                   duration=None,
                                   light_temperature=4000,
                                   light_intensity=500)]

            elif 60 <= stress_index <= 79:
                step1 = LightModes(step=1,
                                   duration=time(minute=30),
                                   light_temperature=3500,
                                   light_intensity=350)
            elif 80 <= stress_index <= 100:
                step1 = LightModes(step=1,
                                   duration=time(minute=15),
                                   light_temperature=2700,
                                   light_intensity=275,
                                   need_to_rest=True)
            else:
                raise ValueError

            step2 = LightModes(step=2,
                               duration=None,
                               light_temperature=4000,
                               light_intensity=500)

            return [step1, step2]

    elif time(hour=20) <= current_time < time(hour=21):
        return [LightModes(step=1,
                           duration=time(minute=20),
                           light_temperature=2700,
                           light_intensity=275)]


def light_mode_with_pai_and_hr(pai: int, sleep_duration: time, current_time: time, hr: int) -> List[LightModes]:
    if sleep_duration >= time(hour=6):
        return [LightModes(step=1,
                           duration=None,
                           light_temperature=4000,
                           light_intensity=500)]
    else:
        if pai >= 50 and hr >= 100:
            return [LightModes(step=1,
                               duration=time(minute=30),
                               light_temperature=2700,
                               light_intensity=275,
                               need_to_rest=True)]
        elif pai <= 50 and hr > 100:
            return [LightModes(step=1,
                               duration=time(minute=30),
                               light_temperature=3500,
                               light_intensity=350,
                               need_to_rest=True)]
        elif pai >= 50 and hr < 100:
            return [LightModes(step=1,
                               duration=time(minute=30),
                               light_temperature=3500,
                               light_intensity=350)]
        elif pai <= 50 and hr < 100:
            if current_time <= time(hour=16):
                return [LightModes(step=1,
                                   duration=time(minute=15),
                                   light_temperature=6000,
                                   light_intensity=750)]
            else:
                return [LightModes(step=1,
                                   duration=None,
                                   light_temperature=4000,
                                   light_intensity=500)]


result = light_mode_with_pai_and_hr(pai=50, current_time=time(18), hr=100, sleep_duration=time(hour=5))
pprint(result)
