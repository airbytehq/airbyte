# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import logging
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path


# Set up logging
logging.basicConfig(filename="airbyte_posts.log", level=logging.INFO, format="%(asctime)s - %(message)s")


def run_posts_generator():
    try:
        script_path = Path("/home/ubuntu/daily_airbyte_posts.sh")
        result = subprocess.run([str(script_path)], capture_output=True, text=True)
        logging.info("Posts generator executed")
        if result.stderr:
            logging.error(f"Error occurred: {result.stderr}")
        return True
    except Exception as e:
        logging.error(f"Failed to run posts generator: {e}")
        return False


def main():
    logging.info("Starting daily posts scheduler")

    while True:
        now = datetime.now()
        # Run at midnight UTC
        next_run = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

        # Calculate sleep duration
        sleep_seconds = (next_run - now).total_seconds()

        logging.info(f"Next run scheduled for: {next_run}")
        logging.info(f"Sleeping for {sleep_seconds} seconds")

        time.sleep(sleep_seconds)
        run_posts_generator()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
