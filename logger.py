# import logging
# from logging.handlers import TimedRotatingFileHandler
# from datetime import datetime, timedelta
# import pytz

# # Set up logging
# logging.basicConfig(
#     level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
# )

# # Set IST timezone
# ist_timezone = pytz.timezone("Asia/Kolkata")

# # Create a TimedRotatingFileHandler to rotate logs daily
# handler = TimedRotatingFileHandler(
#     "app.log", when="midnight", interval=1, backupCount=7, encoding="utf-8"
# )
# handler.suffix = "%Y%m%d.log"
# handler.setFormatter(
#     logging.Formatter(
#         "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
#     )
# )
# handler.rolloverAt = datetime.now(ist_timezone) + timedelta(
#     seconds=1
# )  # Ensure the first rollover happens at midnight IST

# # Add the handler to the logger
# logger = logging.getLogger(__name__)
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)

# if __name__ == "__main__":
#     logger.debug("Logging initialized.")



import logging
from datetime import datetime
import pytz

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Set IST timezone
ist_timezone = pytz.timezone("Asia/Kolkata")

# Create a formatter for console logging
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

# Create a handler for console logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

# Add the console handler to the logger
logger = logging.getLogger(__name__)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

# Function to set IST timezone for the timestamp
def ist_time(*args):
    utc_time = datetime.utcnow()
    utc_time = pytz.utc.localize(utc_time)
    ist_time = utc_time.astimezone(ist_timezone)
    return ist_time.timetuple()

# Set the custom timestamp function for the formatter
console_formatter.converter = ist_time

if __name__ == "__main__":
    logger.info("Google search successful.")
