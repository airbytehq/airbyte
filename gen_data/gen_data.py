import os
import random
import string
import json
import logging
import io
import csv
from datetime import datetime, date, time, timedelta

# pip install pytz google-cloud-storage if not already installed
import pytz  
from google.cloud import storage


# -------------------------------
# LOGGING SETUP
# -------------------------------
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def random_string(length=8):
    """Generate a random string."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def random_bool():
    """Generate a random boolean."""
    return random.choice([True, False])

def random_int(min_val=0, max_val=1000):
    """Generate a random integer."""
    return random.randint(min_val, max_val)

def random_float(min_val=0, max_val=1000):
    """Generate a random float."""
    return round(random.uniform(min_val, max_val), 2)

def random_date(start_year=2000, end_year=2025):
    """Generate a random date between two years."""
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_datetime(start_year=2000, end_year=2025):
    """Generate a random naive datetime (no timezone)."""
    start_dt = datetime(start_year, 1, 1)
    end_dt = datetime(end_year, 12, 31, 23, 59, 59)
    delta = end_dt - start_dt
    random_sec = random.randint(0, int(delta.total_seconds()))
    return start_dt + timedelta(seconds=random_sec)

def random_offset_str():
    """
    Return a random offset in the format +H or -H (e.g. +5, -3, +0).
    Range: -12 to +12
    """
    offset_hours = random.randint(-12, 12)
    # If offset_hours >= 0, explicitly include the plus sign
    if offset_hours >= 0:
        return f"+{offset_hours}"
    else:
        return str(offset_hours)  # e.g. "-5"

def random_datetime_with_offset(start_year=2000, end_year=2025):
    """
    Generate a random datetime (naive) then append an offset in ±H format.
    Example: 2024-10-11T09:12:37+5
    """
    dt_naive = random_datetime(start_year, end_year)
    return dt_naive.isoformat() + random_offset_str()

def random_time_naive():
    """
    Generate a random time without timezone, e.g. HH:MM:SS.
    """
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return time(hour, minute, second)

def random_time_with_offset():
    """
    Generate a random time HH:MM:SS and append ±H offset.
    Example: 09:25:13+5
    """
    t = random_time_naive()
    return t.isoformat() + random_offset_str()

def random_array(max_length=5):
    """Generate a random list with random integers or strings."""
    arr_length = random.randint(1, max_length)
    arr = []
    for _ in range(arr_length):
        if random_bool():
            arr.append(random_int(0, 50))
        else:
            arr.append(random_string(5))
    return arr

def random_json_object():
    """Generate a random JSON object."""
    obj = {
        "id": random_int(1, 9999),
        "name": random_string(6),
        "active": random_bool(),
        "score": random_float(0, 100)
    }
    return obj


# -------------------------------
# MAIN
# -------------------------------
def main():
    """
    Generates a CSV file in GCS of ~10 MB (by default).
    Deletes any existing file with the same name beforehand.
    Has columns for times/timestamps with random ±H offsets (e.g. +5, -3).
    Logs progress, uses integer PK with duplicates, etc.
    """
    # ------------------------------------
    # CONFIGURATIONS
    # ------------------------------------
    PROJECT_ID = "dataline-integration-testing"
    BUCKET_NAME = "no_raw_tables"
    
    TARGET_SIZE_MB = 10  # Adjust as needed
    TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024
    
    # The file name in GCS depends on MB
    BLOB_NAME = f"massive_data_{TARGET_SIZE_MB}MB.csv"

    # Probability that a row reuses an existing PK (for duplicates)
    DUPLICATE_PCT = 20  # 20%

    # Start time for the 'cursor' column
    START_CURSOR = datetime(2025, 1, 1, 12, 0, 0)
    CURSOR_INCREMENT = timedelta(minutes=1)

    # For ~10 MB, 1 MB chunk is fine. Increase for bigger files.
    CHUNK_SIZE = 1 * 1024 * 1024

    # Logging frequency
    LOG_FREQUENCY = 100_000

    logger.info(f"Starting CSV generation. Target size: {TARGET_SIZE_MB} MB.")
    logger.info("Project: %s, Bucket: %s, Blob: %s", PROJECT_ID, BUCKET_NAME, BLOB_NAME)

    # ------------------------------------
    # CREATE GCS CLIENT & BLOB
    # ------------------------------------
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(BLOB_NAME)

    # Delete the file if it already exists
    if blob.exists():
        logger.info(f"Blob {BLOB_NAME} already exists in bucket {BUCKET_NAME}. Deleting it...")
        blob.delete()
        logger.info("Deleted existing blob.")

    # Open the new blob in binary mode for streaming
    with blob.open("wb", chunk_size=CHUNK_SIZE) as gcs_file:
        # CSV headers
        headers = [
            "primary_key",
            "cursor",
            "string",
            "bool",
            "integer",
            "float",
            "date",
            "ts_with_tz",
            "ts_no_tz",
            "time_with_tz",
            "time_no_tz",
            "array",
            "json_object",
        ]

        used_pks = []
        row_count = 0
        current_pk = 1
        total_bytes_written = 0

        # We'll use csv.writer on a StringIO buffer to handle quoting
        row_buffer = io.StringIO()
        csv_writer = csv.writer(row_buffer, quoting=csv.QUOTE_MINIMAL)

        # Write the header row
        row_buffer.seek(0)
        row_buffer.truncate(0)
        csv_writer.writerow(headers)
        row_text = row_buffer.getvalue()
        row_bytes = row_text.encode("utf-8")
        gcs_file.write(row_bytes)
        total_bytes_written += len(row_bytes)

        # Generate data until we exceed the target size
        while total_bytes_written < TARGET_SIZE_BYTES:
            # Decide if we reuse a PK or create a new one
            if used_pks and (random.random() < (DUPLICATE_PCT / 100.0)):
                row_pk = random.choice(used_pks)
            else:
                row_pk = current_pk
                used_pks.append(row_pk)
                current_pk += 1

            # Cursor increments by 1 minute for each row
            row_cursor_time = START_CURSOR + (CURSOR_INCREMENT * row_count)
            row_cursor_str = row_cursor_time.isoformat()

            # Random fields
            row_string = random_string()
            row_bool = random_bool()
            row_integer = random_int()
            row_float_val = random_float()
            row_date_str = random_date().isoformat()

            # Timestamps with random ±H offset
            ts_with_tz = random_datetime_with_offset()  # e.g. "2024-10-11T09:12:37+5"
            ts_no_tz = random_datetime().isoformat()

            # Times with random ±H offset
            t_with_tz = random_time_with_offset()       # e.g. "09:25:13-2"
            t_no_tz = random_time_naive().isoformat()   # e.g. "09:25:13"

            arr_val = random_array()
            obj_val = random_json_object()

            row_data = [
                row_pk,
                row_cursor_str,
                row_string,
                row_bool,
                row_integer,
                row_float_val,
                row_date_str,
                ts_with_tz,
                ts_no_tz,
                t_with_tz,
                t_no_tz,
                json.dumps(arr_val),
                json.dumps(obj_val),
            ]

            # Write to CSV (StringIO)
            row_buffer.seek(0)
            row_buffer.truncate(0)
            csv_writer.writerow(row_data)
            row_text = row_buffer.getvalue()

            # Encode and write to GCS
            row_bytes = row_text.encode("utf-8")
            gcs_file.write(row_bytes)
            total_bytes_written += len(row_bytes)
            row_count += 1

            # Log progress occasionally
            if row_count % LOG_FREQUENCY == 0:
                percent_complete = (total_bytes_written / TARGET_SIZE_BYTES) * 100
                logger.info(
                    f"Progress: {row_count:,} rows, "
                    f"{total_bytes_written / (1024 * 1024):,.2f} MB written "
                    f"({percent_complete:.2f}% complete)."
                )

    logger.info(
        f"Done! Wrote ~{total_bytes_written:,} bytes in {row_count:,} rows "
        f"to gs://{BUCKET_NAME}/{BLOB_NAME}."
    )
    logger.info(f"Approx. {DUPLICATE_PCT}% of rows have duplicate primary keys.")
    logger.info(
        "For bigger datasets, consider parallel or distributed generation for better performance."
    )


if __name__ == "__main__":
    main()