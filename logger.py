import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime, timedelta
import pytz

# Set up logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Set IST timezone
ist_timezone = pytz.timezone("Asia/Kolkata")

# Create a TimedRotatingFileHandler to rotate logs daily
handler = TimedRotatingFileHandler(
    "app.log", when="midnight", interval=1, backupCount=7, encoding="utf-8"
)
handler.suffix = "%Y%m%d.log"
handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)
handler.rolloverAt = datetime.now(ist_timezone) + timedelta(
    seconds=1
)  # Ensure the first rollover happens at midnight IST

# Add the handler to the logger
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    logger.debug("Logging initialized.")
