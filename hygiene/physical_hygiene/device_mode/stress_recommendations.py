from dataclasses import dataclass


@dataclass
class Recommendation:
    text: str


class SmartSpeakerCommand:
    def __init__(self, text: str) -> None:
        self.text = text

    def stress_recommendations(self, stress_index: int) -> Recommendation:
        if stress_index > 50:
            return Recommendation(text="включи расслабляющую музыку")
