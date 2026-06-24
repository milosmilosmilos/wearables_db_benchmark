import csv
import random

from datetime import datetime, timedelta

from generator_code.states import STATES
from generator_code.states import get_next_state
from generator_code.states import get_state_duration


class DataGenerator:

    def __init__(self, anomaly_rate):
        self.anomaly_rate = anomaly_rate

    def generate_row(self, timestamp, user_id, state):

        cfg = STATES[state]

        heart_rate = random.gauss(*cfg["heart_rate"])
        temperature = random.gauss(*cfg["temperature"])

        accel_mean, accel_std = cfg["accel"]

        accel_x = random.gauss(accel_mean, accel_std)
        accel_y = random.gauss(accel_mean, accel_std)
        accel_z = random.gauss(accel_mean, accel_std)

        is_anomaly = 0

        if random.random() < self.anomaly_rate:

            t = random.randint(1, 3)

            if t == 1:
                heart_rate = 155
                accel_x = accel_y = accel_z = 0.01

            elif t == 2:
                heart_rate = 42
                accel_x = accel_y = accel_z = 1.6

            else:
                temperature = 38.7

            is_anomaly = 1

        return [
            timestamp.isoformat(),
            user_id,
            state,
            round(heart_rate),
            round(temperature, 2),
            round(accel_x, 3),
            round(accel_y, 3),
            round(accel_z, 3),
            is_anomaly
        ]

    def generate(self, users, days, interval_seconds, output_file):

        start_time = datetime.now()

        user_states = {
            user_id: {
                "state": "resting",
                "remaining": get_state_duration("resting")
            }
            for user_id in range(1, users + 1)
        }

        total_steps = int((days * 24 * 60 * 60) / interval_seconds)

        with open(output_file, "w", newline="") as f:

            writer = csv.writer(f)

            writer.writerow([
                "timestamp",
                "user_id",
                "state",
                "heart_rate",
                "temperature",
                "accel_x",
                "accel_y",
                "accel_z",
                "is_anomaly"
            ])

            for step in range(total_steps):

                current_time = start_time + timedelta(
                    seconds=step * interval_seconds
                )

                for user_id in range(1, users + 1):

                    info = user_states[user_id]
                    state = info["state"]

                    writer.writerow(
                        self.generate_row(
                            current_time,
                            user_id,
                            state
                        )
                    )

                    info["remaining"] -= interval_seconds

                    if info["remaining"] <= 0:
                        new_state = get_next_state(state)
                        info["state"] = new_state
                        info["remaining"] = get_state_duration(new_state)