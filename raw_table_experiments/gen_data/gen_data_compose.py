import os
import random
import string
import json
import logging
import io
import csv
import time
import concurrent.futures
from datetime import datetime, date, time as dt_time, timedelta

import pytz  # pip install pytz
from google.cloud import storage  # pip install google-cloud-storage


logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def random_string(length=8):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def random_bool():
    return random.choice([True, False])

def random_int(min_val=0, max_val=1000):
    return random.randint(min_val, max_val)

def random_float(min_val=0, max_val=1000):
    return round(random.uniform(min_val, max_val), 2)

def random_date(start_year=2000, end_year=2025):
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def random_datetime(start_year=2000, end_year=2025):
    start_dt = datetime(start_year, 1, 1)
    end_dt = datetime(end_year, 12, 31, 23, 59, 59)
    delta = end_dt - start_dt
    random_sec = random.randint(0, int(delta.total_seconds()))
    return start_dt + timedelta(seconds=random_sec)

def random_offset_str():
    offset_hours = random.randint(-12, 12)
    return f"+{offset_hours}" if offset_hours >= 0 else str(offset_hours)

def random_datetime_with_offset():
    dt_naive = random_datetime()
    return dt_naive.isoformat() + random_offset_str()

def random_time_naive():
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return dt_time(hour, minute, second)

def random_time_with_offset():
    t = random_time_naive()
    return t.isoformat() + random_offset_str()

def random_array(max_length=5):
    arr_length = random.randint(1, max_length)
    arr = []
    for _ in range(arr_length):
        if random_bool():
            arr.append(random_int(0, 50))
        else:
            arr.append(random_string(5))
    return arr

def random_json_object():
    return {
        "id": random_int(1, 9999),
        "name": random_string(6),
        "active": random_bool(),
        "score": random_float(0, 100)
    }


def generate_csv_part(
    project_id: str,
    bucket_name: str,
    blob_name: str,
    target_size_mb: int,
    duplicate_pct: int = 20,
    chunk_size: int = 100 * 1024 * 1024,
    log_frequency: int = 100_000
):
    """
    Generates one CSV "part" of ~target_size_mb MB in GCS under blob_name.
    Re-uses the random data logic, including duplicates and random ±H timezones.
    """

    # We'll have a 'cursor' column that increments by 1 min/row
    START_CURSOR = datetime(2025, 1, 1, 12, 0, 0)
    CURSOR_INCREMENT = timedelta(minutes=1)

    target_size_bytes = target_size_mb * 1024 * 1024

    logger.info(f"Generating part '{blob_name}', target ~{target_size_mb} MB")

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    # Delete if exists
    if blob.exists():
        logger.info(f"Blob {blob_name} exists. Deleting...")
        blob.delete()

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

        # Write header for each part
        row_buffer.seek(0)
        row_buffer.truncate(0)
        csv_writer.writerow(headers)
        row_text = row_buffer.getvalue()
        row_bytes = row_text.encode("utf-8")
        gcs_file.write(row_bytes)
        total_bytes_written += len(row_bytes)

        # Generate rows until we exceed target size
        while total_bytes_written < target_size_bytes:
            # Randomly reuse PK
            if used_pks and (random.random() < (duplicate_pct / 100.0)):
                row_pk = random.choice(used_pks)
            else:
                row_pk = current_pk
                used_pks.append(row_pk)
                current_pk += 1

            row_cursor_time = START_CURSOR + (CURSOR_INCREMENT * row_count)
            row_cursor_str = row_cursor_time.isoformat()

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

            row_buffer.seek(0)
            row_buffer.truncate(0)
            csv_writer.writerow(row_data)
            row_text = row_buffer.getvalue()

            row_bytes = row_text.encode("utf-8")
            gcs_file.write(row_bytes)
            total_bytes_written += len(row_bytes)
            row_count += 1

            if row_count % log_frequency == 0:
                percent_complete = (total_bytes_written / target_size_bytes) * 100
                logger.info(
                    f"[{blob_name}] rows={row_count:,}, "
                    f"{total_bytes_written / (1024 * 1024):,.2f} MB, "
                    f"{percent_complete:.2f}% complete"
                )

    end_time = time.time()
    duration_s = end_time - start_time
    speed_mb_s = (total_bytes_written / 1024 / 1024) / duration_s if duration_s > 0 else 0
    logger.info(
        f"[{blob_name}] Done. {row_count:,} rows, "
        f"{total_bytes_written:,} bytes in {duration_s:.2f}s, "
        f"{speed_mb_s:.2f} MB/s"
    )


def compose_final(
    project_id: str,
    bucket_name: str,
    final_blob_name: str,
    part_names: list
):
    """
    Use GCS Compose to merge multiple part objects in order
    into a single final blob (final_blob_name).
    Up to 32 parts can be composed at a time.
    """
    logger.info(f"Composing final object '{final_blob_name}' from parts: {part_names}")
    client = storage.Client(project=project_id)
    bucket = client.bucket(bucket_name)

    final_blob = bucket.blob(final_blob_name)
    if final_blob.exists():
        logger.info(f"Final blob {final_blob_name} exists. Deleting first...")
        final_blob.delete()

    # Make list of blob objects from the part names
    part_blobs = [bucket.blob(name) for name in part_names]

    # If you have more than 32 parts, you'd do a multi-step compose
    final_blob.compose(part_blobs)

    logger.info(f"Composed {final_blob_name} from {len(part_names)} parts.")


def main():
    """
    Example for creating ONE 100GB final CSV via 5 parallel parts of 20GB each.
    """
    PROJECT_ID = "dataline-integration-testing"
    BUCKET_NAME = "no_raw_tables"

    # We'll create 5 parts, each ~20 GB => total ~100 GB
    PART_SIZES_MB = [10_000, 10_000, 10_000, 10_000, 10_000, 10_000, 10_000, 10_000, 10_000, 10_000]
    PART_NAMES = [f"mydata_part_{i}.csv" for i in range(len(PART_SIZES_MB))]
    FINAL_NAME = "mydata_final_100GB.csv"

    # 1) Generate each part in parallel
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for i, size_mb in enumerate(PART_SIZES_MB):
            part_name = PART_NAMES[i]
            fut = executor.submit(
                generate_csv_part,
                project_id=PROJECT_ID,
                bucket_name=BUCKET_NAME,
                blob_name=part_name,
                target_size_mb=size_mb
            )
            futures.append(fut)

        # Wait for all parts to finish
        for fut in concurrent.futures.as_completed(futures):
            fut.result()  # propagate any exceptions

    # 2) Compose them into final
    compose_final(
        project_id=PROJECT_ID,
        bucket_name=BUCKET_NAME,
        final_blob_name=FINAL_NAME,
        part_names=PART_NAMES
    )
    end_time = time.time()

    total_duration = end_time - start_time
    logger.info(f"All done! Single final CSV is {FINAL_NAME}, took {total_duration:.2f} seconds.")


if __name__ == "__main__":
    main()