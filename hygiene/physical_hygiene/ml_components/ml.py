import pickle
from datetime import datetime, timedelta

import pandas as pd


# This class implements work with models for predicting sleep and the light phase in a person's sleep
class SleepModel:
    def __init__(self):

        self.model_sleep = pickle.load(open("model_sleep.pkl", "rb"))
        self.columns_transform_sleep = pickle.load(
            open("columns_transform_sleep.pkl", "rb")
        )

        self.model_phases = pickle.load(open("model_phases.pkl", "rb"))
        self.columns_transform_phases = pickle.load(
            open("columns_transform_phases.p", "rb")
        )

    # check_time_of_day - return time of day by hour
    def check_time_of_day(self, hour):
        return (
            "night"
            if hour in [0, 1, 2, 3, 4, 5]
            else (
                "morning"
                if hour in [6, 7, 8, 9, 10, 11, 12]
                else ("evening" if hour in [18, 19, 20, 21, 22, 23] else "day")
            )
        )

    # predict_sleep - predict sleeping
    # args: pulse - mean pulse in last 5 minutes
    #       spo2 - mean spo2 in last 5 minutes
    #       datetime (type datetime!)- datetime of getting pulse and spo2
    # returns: class 1 or 0 - pearson sleeps ot doesn't sleep in this time
    def predict_sleep(self, pulse, spo2, date_time):

        row = {
            "month": date_time.month,
            "hour": date_time.hour,
            "minute": date_time.minute,
            "dayofweek": date_time.weekday(),
            "time_of_day": self.check_time_of_day(date_time.hour),
            "heartRate": pulse,
            "spo": spo2,
        }

        row = self.columns_transform_sleep.transform(
            pd.DataFrame(row, index=[0])
        )

        return self.model_sleep.predict(row)

    def create_dataframe_by_minutes(self, time_start, total_minutes):

        df = pd.DataFrame()
        start_min = time_start.minute
        hour = time_start.hour
        month = time_start.month
        dayofweek = time_start.weekday()

        for i in range(total_minutes):

            row = {
                "hour": hour,
                "dayofweek": dayofweek,
                "time_of_day": self.check_time_of_day(hour),
                "month": month,
                "abs_min": i,
            }

            df = df.append(row, ignore_index=True)

            if (start_min + i) % 60 == 0 and (start_min + i != 0):
                hour += 1
            if hour == 24:
                hour = 0
                dayofweek = (dayofweek + 1) if dayofweek < 6 else 0

        return df

    # predict_phases - predict dream phases
    # args: time_start (type datetime!) - the start sleep time
    #       time_end (type datetime!) - the end sleep time
    # returns: phrases for every minute
    def predict_phases(self, time_start, time_end):

        total_minutes = int(abs((time_start - time_end).total_seconds()) / 60)

        df = self.create_dataframe_by_minutes(time_start, total_minutes)
        df_scaled = self.columns_transform_phases.transform(
            pd.DataFrame(df, index=[0])
        )

        return self.model_phases.predict(df_scaled)

    # find_time_waking_up - find the time for waking up
    # args: sleep_start (type datetime!) - the start sleep time
    #       sleep_end (type datetime!)- the end sleep time
    #       interval_start (type datetime!)-the start of the user's awakening interval
    #       interval_end (type datetime!)-the end of the user's awakening interval
    # returns: time for waking up (type datetime!)
    def find_time_waking_up(
        self, sleep_start, sleep_end, interval_start, interval_end
    ):

        ending = sleep_end if sleep_end >= interval_end else interval_end

        # find phases in every minutes
        phases = self.predict_phases(sleep_start, ending)

        label_encode = pickle.load(open("LabelEncoderPhases.p", "rb"))
        index_phases = label_encode.classes_.index("Light sleep")

        interval = int((abs(ending - interval_start)).total_seconds() / 60)
        count_minute = 0

        while count_minute != interval:
            if phases[-count_minute] == index_phases:
                break
            count_minute += 1

        if (count_minute == interval) and (
            phases[-count_minute] != index_phases
        ):
            return ending
        else:
            return ending - timedelta(minutes=count_minute)
