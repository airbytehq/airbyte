import os
import random
import string
import json
import logging
import io
import csv
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import concurrent.futures
from datetime import datetime, date, time as dt_time, timedelta
from pathlib import Path

import pytz
from google.cloud import storage
from google.cloud.storage.blob import Blob

# -------------------------------
# LOGGING SETUP
# -------------------------------
logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# -------------------------------
# CONFIGURATION
# -------------------------------
@dataclass
class GeneratorConfig:
    """Configuration for the CSV generator."""
    project_id: str
    bucket_name: str
    target_size_mb: int
    duplicate_pct: int = 20
    chunk_size_mb: int = 100  # Reduced from 500MB to 100MB for faster uploads
    log_frequency: int = 100_000  # Reduced from 1M to 100K for more frequent updates
    start_date: datetime = datetime(2025, 1, 1, 12, 0, 0)
    cursor_increment: timedelta = timedelta(minutes=1)
    cache_size: int = 10_000

    @property
    def chunk_size_bytes(self) -> int:
        return self.chunk_size_mb * 1024 * 1024

    @property
    def target_size_bytes(self) -> int:
        return self.target_size_mb * 1024 * 1024

# -------------------------------
# DATA GENERATION
# -------------------------------
class RandomDataGenerator:
    """Handles generation of random data with caching."""
    
    def __init__(self, cache_size: int = 10_000):
        self.cached_strings = [
            ''.join(random.choices(string.ascii_letters, k=8))
            for _ in range(cache_size)
        ]
        self.timezones = list(pytz.all_timezones)  # Cache timezone list

    def random_string(self) -> str:
        return random.choice(self.cached_strings)

    def random_bool(self) -> bool:
        return random.choice([True, False])

    def random_int(self, min_val: int = 0, max_val: int = 1000) -> int:
        return random.randint(min_val, max_val)

    def random_float(self, min_val: float = 0, max_val: float = 1000) -> float:
        return round(random.uniform(min_val, max_val), 2)

    def random_date(self, start_year: int = 2020, end_year: int = 2025) -> date:
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return start_date + timedelta(days=random_days)

    def random_datetime_tz(self, start_year: int = 2020, end_year: int = 2025) -> datetime:
        naive_dt = self._random_datetime(start_year, end_year)
        timezone = random.choice(self.timezones)
        return pytz.timezone(timezone).localize(naive_dt)

    def _random_datetime(self, start_year: int = 2020, end_year: int = 2025) -> datetime:
        start_dt = datetime(start_year, 1, 1)
        end_dt = datetime(end_year, 12, 31, 23, 59, 59)
        delta = end_dt - start_dt
        random_sec = random.randint(0, int(delta.total_seconds()))
        return start_dt + timedelta(seconds=random_sec)

    def random_time_with_timezone(self) -> str:
        dt_with_tz = self.random_datetime_tz()
        return dt_with_tz.isoformat().split("T")[1]

    def random_array(self, max_length: int = 5) -> List[Any]:
        arr_length = random.randint(1, max_length)
        return [
            self.random_int(0, 50) if self.random_bool() else self.random_string()
            for _ in range(arr_length)
        ]

    def random_json_object(self) -> Dict[str, Any]:
        return {
            "id": self.random_int(1, 9999),
            "name": self.random_string(),
            "active": self.random_bool(),
            "score": self.random_float(0, 100)
        }

class CSVGenerator:
    """Handles CSV file generation and upload to GCS."""

    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.data_generator = RandomDataGenerator(config.cache_size)
        self.storage_client = storage.Client(project=config.project_id)
        self.bucket = self.storage_client.bucket(config.bucket_name)
        
    def generate_row(self, pk: int, cursor_time: datetime) -> List[Any]:
        """Generate a single row of data."""
        return [
            pk,
            cursor_time.isoformat(),
            self.data_generator.random_string(),
            self.data_generator.random_bool(),
            self.data_generator.random_int(),
            self.data_generator.random_float(),
            self.data_generator.random_date().isoformat(),
            self.data_generator.random_datetime_tz().isoformat(),
            self.data_generator._random_datetime().isoformat(),
            self.data_generator.random_time_with_timezone(),
            dt_time(
                random.randint(0, 23),
                random.randint(0, 59),
                random.randint(0, 59)
            ).isoformat(),
            json.dumps(self.data_generator.random_array()),
            json.dumps(self.data_generator.random_json_object()),
        ]

    def _compose_chunks(self, final_blob_name: str, chunk_blobs: List[Blob]) -> None:
        """
        Compose chunks into final blob with multi-level composition.
        Handles >32 blobs by composing in a tree structure: chunks -> intermediate -> final.
        """
        if not chunk_blobs:
            raise ValueError("No chunks to compose")

        logger.info(f"Starting composition of {len(chunk_blobs)} chunks into {final_blob_name}")

        def compose_group(blobs: List[Blob], level_prefix: str) -> Blob:
            """Compose a group of up to 32 blobs into a single blob."""
            if len(blobs) == 0:
                raise ValueError("Empty blob group")
            if len(blobs) == 1:
                return blobs[0]
            if len(blobs) > 32:
                raise ValueError(f"Too many blobs for single compose: {len(blobs)}")

            composed_name = f"{final_blob_name}.{level_prefix}"
            composed_blob = self.bucket.blob(composed_name)
            composed_blob.compose(blobs)
            
            # Clean up source blobs after successful composition
            for blob in blobs:
                try:
                    blob.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete source blob {blob.name}: {e}")
            
            return composed_blob

        # If 32 or fewer chunks, compose directly
        if len(chunk_blobs) <= 32:
            final_blob = self.bucket.blob(final_blob_name)
            final_blob.compose(chunk_blobs)
            for blob in chunk_blobs:
                blob.delete()
            return

        # Otherwise, do hierarchical composition
        current_level_blobs = chunk_blobs
        level = 0

        while len(current_level_blobs) > 32:
            next_level_blobs = []
            
            # Process groups of up to 32 blobs
            for i in range(0, len(current_level_blobs), 32):
                group = current_level_blobs[i:i + 32]
                composed_blob = compose_group(
                    group, 
                    f"level_{level}_{i//32:03d}"
                )
                next_level_blobs.append(composed_blob)
            
            logger.info(
                f"Composed level {level}: {len(current_level_blobs)} blobs -> "
                f"{len(next_level_blobs)} intermediate blobs"
            )
            
            current_level_blobs = next_level_blobs
            level += 1

        # Final composition
        final_blob = self.bucket.blob(final_blob_name)
        final_blob.compose(current_level_blobs)
        
        # Clean up any remaining intermediate blobs
        for blob in current_level_blobs:
            try:
                blob.delete()
            except Exception as e:
                logger.warning(f"Failed to delete intermediate blob {blob.name}: {e}")

        logger.info(f"Successfully completed {level+1}-level composition into {final_blob_name}")

    def generate_csv(self, file_index: Optional[int] = None) -> str:
        """Generate and upload CSV file to GCS."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        index_suffix = f"_{file_index:03d}" if file_index is not None else ""
        final_blob_name = (
            f"data_export_{self.config.target_size_mb}MB_{timestamp}{index_suffix}.csv"
        )
        
        # Delete existing blob if it exists
        final_blob = self.bucket.blob(final_blob_name)
        if final_blob.exists():
            logger.info(f"Deleting existing blob: {final_blob_name}")
            final_blob.delete()

        start_time = time.time()
        row_buffer = io.StringIO()
        csv_writer = csv.writer(row_buffer, quoting=csv.QUOTE_MINIMAL)

        used_pks: List[int] = []
        row_count = 0
        current_pk = 1
        total_bytes_written = 0
        chunk_blobs: List[Blob] = []
        current_chunk_index = 0
        rows_in_current_chunk = 0

        def flush_buffer() -> None:
            """
            Upload current buffer as a chunk to GCS with retry logic.
            """
            nonlocal current_chunk_index, rows_in_current_chunk
            
            data = row_buffer.getvalue()
            if not data:
                return

            part_name = f"{final_blob_name}.part_{current_chunk_index:05d}"  # Zero-padded for ordering
            chunk_blob = self.bucket.blob(part_name)
            
            encoded_data = data.encode("utf-8")
            chunk_size_mb = len(encoded_data) / (1024 * 1024)
            
            logger.info(
                f"Uploading chunk #{current_chunk_index:05d} "
                f"({rows_in_current_chunk:,} rows, {chunk_size_mb:.2f} MB)"
            )

            # Simple retry logic
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    chunk_blob.upload_from_string(
                        data,
                        content_type="text/csv",
                        timeout=120  # Reduced timeout to 2 minutes since chunks are smaller
                    )
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        raise Exception(f"Failed to upload chunk after {max_retries} attempts") from e
                    logger.warning(f"Chunk upload failed, attempt {retry_count} of {max_retries}: {str(e)}")
                    time.sleep(2 ** retry_count)  # Exponential backoff
            
            chunk_blobs.append(chunk_blob)
            logger.info(f"Successfully uploaded chunk #{current_chunk_index:05d}")
            
            # Clear the buffer
            current_chunk_index += 1
            rows_in_current_chunk = 0
            row_buffer.seek(0)
            row_buffer.truncate()
            
            # Add a small sleep to prevent overwhelming GCS
            time.sleep(0.1)

        logger.info(f"Beginning generation of {final_blob_name}")
        prev_buffer_pos = 0

        cursor_time = self.config.start_date
        while total_bytes_written < self.config.target_size_bytes:
            # Determine if we should reuse a PK
            if used_pks and random.random() < (self.config.duplicate_pct / 100):
                row_pk = random.choice(used_pks)
            else:
                row_pk = current_pk
                used_pks.append(row_pk)
                current_pk += 1

            row_data = self.generate_row(row_pk, cursor_time)
            csv_writer.writerow(row_data)
            
            cursor_time += self.config.cursor_increment
            row_count += 1
            rows_in_current_chunk += 1

            # Measure new bytes written
            new_buffer_pos = row_buffer.tell()
            total_bytes_written += (new_buffer_pos - prev_buffer_pos)
            prev_buffer_pos = new_buffer_pos

            # Progress logging
            if row_count % self.config.log_frequency == 0:
                progress = (total_bytes_written / self.config.target_size_bytes) * 100
                logger.info(
                    f"Generated {row_count:,} rows, {total_bytes_written / 1024 / 1024:.2f} MB "
                    f"({progress:.1f}%)"
                )

            # Flush if chunk size exceeded
            if new_buffer_pos >= self.config.chunk_size_bytes:
                flush_buffer()
                prev_buffer_pos = 0

        # Flush any remaining data
        if rows_in_current_chunk > 0:
            flush_buffer()

        # Compose final file
        self._compose_chunks(final_blob_name, chunk_blobs)

        duration = time.time() - start_time
        mb_written = total_bytes_written / (1024 * 1024)
        speed_mbps = mb_written / duration if duration > 0 else 0

        summary = (
            f"Generated {final_blob_name}: {row_count:,} rows, "
            f"{mb_written:.2f} MB in {duration:.2f}s ({speed_mbps:.2f} MB/s)"
        )
        logger.info(summary)
        return summary

def main() -> None:
    """Generate multiple CSV files in parallel."""
    base_config = GeneratorConfig(
        project_id="dataline-integration-testing",
        bucket_name="no_raw_tables",
        target_size_mb=20_000,
    )

    # Generate 5 files of 20GB each in parallel
    num_files = 5
    max_workers = min(num_files, os.cpu_count() or 4)

    logger.info(f"Starting {num_files} parallel CSV generation tasks...")
    results = []

    def generate_with_index(index: int) -> str:
        """Generate a CSV file with a unique index."""
        config_dict = base_config.__dict__.copy()
        # Modify the start_date in the copied dictionary
        config_dict['start_date'] = base_config.start_date + timedelta(days=index)
        unique_config = GeneratorConfig(**config_dict)
        generator = CSVGenerator(unique_config)
        return generator.generate_csv(file_index=index)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(generate_with_index, i)
            for i in range(num_files)
        ]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                logger.info(f"Completed generation: {result}")
            except Exception as exc:
                logger.error("Generation failed", exc_info=exc)

    logger.info("All parallel tasks complete.")
    for result in results:
        logger.info(f"Final result: {result}")

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                logger.info(f"Completed generation: {result}")
            except Exception as exc:
                logger.error("Generation failed", exc_info=exc)

    logger.info("All parallel tasks complete.")
    for result in results:
        logger.info(f"Final result: {result}")

if __name__ == "__main__":
    main()