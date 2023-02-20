from dataclasses import dataclass


# TODO: определить, какие другие активности влияют на записи шагов. Так как 'Другая активность' и 'Ходьба' дают 60% шагов


@dataclass
class GoogleTypes:
    activity_type = {
        "Сон": 72,
        "Другая активность": 108,
        "Ходьба": 7,
    }
    data_types = {
        "рост": "com.google.height",
        "вес": "com.google.weight",
    }
    filter_types = {
        "com.google.active_minutes",
        "com.google.activity.segment",
        "com.google.calories.bmr",
        "com.google.calories.expended",
        "com.google.distance.delta",
        "com.google.heart_minutes",
        "com.google.heart_rate.bpm",
        "com.google.height",
        "com.google.sleep.segment",
        "com.google.speed",
        "com.google.step_count.delta",
        "com.google.weight",
        "com.google.step_count.cumulative",
    }
    duration_type = {"7days": 604800000, "1day": 86400000, "1hour": 36000}
    sleep_stages = {
        1: "Пробуждение (во время сна)",
        2: "Спать",
        3: "Из кровати",
        4: "Легкий сон",
        5: "Глубокий сон",
        6: "РЭМ",
    }
