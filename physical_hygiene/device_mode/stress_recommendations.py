from dataclasses import dataclass


@dataclass
class SmartSpeakerCommand:
    text: str

def stress_recommendations(stress_index: int) -> SmartSpeakerCommand:
    if stress_index > 50:
        return SmartSpeakerCommand(text='включи расслабляющую музыку')

