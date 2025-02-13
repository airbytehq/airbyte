import os
import random
import string
import json
import logging
import io
import csv
import time
from datetime import datetime, date, time as dt_time, timedelta

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
    """Generate a random time (HH:MM:SS)."""
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return dt_time(hour, minute, second)

def random_time_with_offset():
    """
    Generate a random time HH:MM:SS and append ±H offset.
    Example: "09:25:13+5"
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
def generate_csv(
    project_id: str,
    bucket_name: str,
    target_size_mb: int,
    duplicate_pct: int = 20,
    chunk_size: int = 1 * 1024 * 1024,
    log_frequency: int = 100_000
):
    """
    Generate and upload one CSV file of size ~target_size_mb MB to GCS.
    - project_id: GCP project
    - bucket_name: GCS bucket
    - target_size_mb: approximate MB size
    - duplicate_pct: % chance to reuse PK
    - chunk_size: GCS upload chunk size
    - log_frequency: rows between progress logs
    """

    start_cursor = datetime(2025, 1, 1, 12, 0, 0)
    cursor_increment = timedelta(minutes=1)

    target_size_bytes = target_size_mb * 1024 * 1024
    blob_name = f"massive_data_{target_size_mb}MB.csv"

    logger.info("Starting CSV generation. Target size: %d MB", target_size_mb)
    logger.info("Project: %s, Bucket: %s, Blob: %s", project_id, bucket_name, blob_name)

    # Setup GCS
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Delete existing blob if any
    if blob.exists():
        logger.info(f"Blob {blob_name} already exists. Deleting it...")
        blob.delete()
        logger.info("Deleted existing blob.")

    start_time = time.time()

    with blob.open("wb", chunk_size=chunk_size) as gcs_file:
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

        row_buffer = io.StringIO()
        csv_writer = csv.writer(row_buffer, quoting=csv.QUOTE_MINIMAL)

        # Write header
        row_buffer.seek(0)
        row_buffer.truncate(0)
        csv_writer.writerow(headers)
        row_text = row_buffer.getvalue()
        row_bytes = row_text.encode("utf-8")
        gcs_file.write(row_bytes)
        total_bytes_written += len(row_bytes)

        # Generate rows until target size reached
        while total_bytes_written < target_size_bytes:
            # Duplicate PK logic
            if used_pks and (random.random() < (duplicate_pct / 100.0)):
                row_pk = random.choice(used_pks)
            else:
                row_pk = current_pk
                used_pks.append(row_pk)
                current_pk += 1

            # Cursor
            row_cursor_time = start_cursor + (cursor_increment * row_count)
            row_cursor_str = row_cursor_time.isoformat()

            # Random data
            row_string = random_string()
            row_bool = random_bool()
            row_integer = random_int()
            row_float_val = random_float()
            row_date_str = random_date().isoformat()

            ts_with_tz = random_datetime_with_offset()
            ts_no_tz = random_datetime().isoformat()
            t_with_tz = random_time_with_offset()
            t_no_tz = random_time_naive().isoformat()

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

            # Write row to CSV
            row_buffer.seek(0)
            row_buffer.truncate(0)
            csv_writer.writerow(row_data)
            row_text = row_buffer.getvalue()

            # Encode + write
            row_bytes = row_text.encode("utf-8")
            gcs_file.write(row_bytes)
            total_bytes_written += len(row_bytes)
            row_count += 1

            # Progress log
            if row_count % log_frequency == 0:
                percent_complete = (total_bytes_written / target_size_bytes) * 100
                logger.info(
                    f"Progress for {blob_name}: {row_count:,} rows, "
                    f"{total_bytes_written / (1024 * 1024):,.2f} MB written "
                    f"({percent_complete:.2f}% complete)."
                )

    # Calc speed
    end_time = time.time()
    duration_seconds = end_time - start_time
    mb_written = total_bytes_written / (1024 * 1024)
    speed_mbps = mb_written / duration_seconds if duration_seconds > 0 else 0.0

    logger.info(
        f"File {blob_name} done! {total_bytes_written:,} bytes, {row_count:,} rows, "
        f"elapsed time {duration_seconds:.2f} s, speed {speed_mbps:.2f} MB/s."
    )


def main():
    """
    Demonstrates generating multiple files of different sizes,
    each with random CSV data in GCS.
    """
    PROJECT_ID = "dataline-integration-testing"
    BUCKET_NAME = "no_raw_tables"

    # List of file sizes in MB (adjust as needed)
    sizes_mb = [10, 100, 1000, 10000]

    for size in sizes_mb:
        generate_csv(
            project_id=PROJECT_ID,
            bucket_name=BUCKET_NAME,
            target_size_mb=size
        )


if __name__ == "__main__":
    main()