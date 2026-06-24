from generator_code.config import USERS
from generator_code.config import DAYS
from generator_code.config import INTERVAL_SECONDS
from generator_code.config import ANOMALY_RATE
from generator_code.config import OUTPUT_FILE

from generator_code.generator import DataGenerator


generator = DataGenerator(
    anomaly_rate=ANOMALY_RATE
)

generator.generate(
    users=USERS,
    days=DAYS,
    interval_seconds=INTERVAL_SECONDS,
    output_file=OUTPUT_FILE
)

print("Done")