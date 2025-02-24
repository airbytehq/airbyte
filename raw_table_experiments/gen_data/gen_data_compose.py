import os
import random
import string
import json
import logging
import io
import csv
import time
import psutil
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import concurrent.futures
from datetime import datetime, date, time as dt_time, timedelta
from pathlib import Path
import argparse
import gc

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


def calculate_optimal_file_split(total_size_mb: int, max_files: int = 0) -> Tuple[int, int]:
    """
    Calculate the optimal number of files and size per file based on total target size.
    
    Args:
        total_size_mb: Total size to generate across all files in MB
        max_files: Maximum number of files to create (0 for auto-determine)
        
    Returns:
        Tuple of (number of files, size per file in MB)
    """
    # Available CPU cores (for parallel processing)
    available_cores = os.cpu_count() or 4
    
    # Get available memory (in MB)
    # Use 50% of available memory as our target working limit
    try:
        available_memory_mb = psutil.virtual_memory().available // (1024 * 1024) // 2
    except:
        # If psutil is not available, assume a conservative 2GB
        available_memory_mb = 2 * 1024
    
    logger.info(f"Available memory for processing: {available_memory_mb} MB")
    logger.info(f"Available CPU cores: {available_cores}")
    
    # For very small sizes (< 100MB), just create one file
    if total_size_mb < 100:
        return 1, total_size_mb
        
    # For testing sizes (< 1GB), use available cores as the number of files
    if total_size_mb < 1024:
        num_files = min(available_cores, 4)  # Use up to 4 files for small test data
        size_per_file = (total_size_mb + num_files - 1) // num_files
        return num_files, size_per_file
    
    # For small-medium sizes (1GB-10GB), use all available cores
    if total_size_mb < 10 * 1024:
        # Split based on available cores
        num_files = available_cores
        size_per_file = (total_size_mb + num_files - 1) // num_files
        return num_files, size_per_file
        
    # For large sizes (>10GB), optimize for parallelism
    # Target file size of 2GB per file to balance memory and speed
    target_size_per_file = 2 * 1024  # 2GB per file
    num_files = (total_size_mb + target_size_per_file - 1) // target_size_per_file
    
    # Cap number of files to 2x available cores for efficiency
    max_suggested_files = available_cores * 2
    
    if max_files > 0:
        # User specified max files
        num_files = min(num_files, max_files)
    else:
        # Auto determine, but cap at 2x available cores
        num_files = min(num_files, max_suggested_files)
    
    # Recalculate size per file
    size_per_file = (total_size_mb + num_files - 1) // num_files
    
    # Ensure we use at least one file
    num_files = max(1, num_files)
    
    return num_files, size_per_file

def calculate_chunk_level_parallelism(target_size_mb: int, chunk_size_mb: int, max_parallel_chunks: int = None) -> int:
    """
    Calculate how many chunks to generate in parallel based on system resources.
    
    Args:
        target_size_mb: Target file size in MB
        chunk_size_mb: Chunk size in MB
        max_parallel_chunks: Maximum parallel chunks (defaults to CPU count)
        
    Returns:
        Number of chunks to generate in parallel
    """
    if max_parallel_chunks is None:
        max_parallel_chunks = os.cpu_count() or 4
    
    # Calculate estimated total chunks
    total_chunks = (target_size_mb + chunk_size_mb - 1) // chunk_size_mb
    
    # For very small files with few chunks, limit parallelism
    if total_chunks < 4:
        return min(total_chunks, max_parallel_chunks)
    
    # For medium files, use available cores
    if total_chunks < 16:
        return min(total_chunks, max_parallel_chunks)
    
    # For large files with many chunks, increase parallelism
    return max_parallel_chunks

def calculate_optimal_chunk_size(target_size_mb: int) -> int:
    """
    Calculate optimal chunk size based on target file size to minimize composition levels.
    
    Args:
        target_size_mb: Target file size in MB
        
    Returns:
        Optimal chunk size in MB
    """
    # GCS compose limit is 32 objects
    max_objects_per_composition = 32
    
    # For very small files (< 32 MB), use a minimum chunk size
    if target_size_mb < 32:
        return max(1, target_size_mb // 2)  # Use at most 2 chunks for tiny files
    
    # For small files (< 32 GB), we can use a single level of composition
    if target_size_mb < max_objects_per_composition * 1024:  # If target < 32 GB
        # Aim for one level of composition with equal sized chunks
        return max(100, target_size_mb // max_objects_per_composition)
    
    # For larger files, we need multiple levels of composition
    # Calculate how many chunks we'd need at different levels
    
    # For a balanced tree, we want each node to have close to max_objects_per_composition children
    # Level 1: max_objects_per_composition chunks
    # Level 2: max_objects_per_composition^2 chunks
    # Level 3: max_objects_per_composition^3 chunks
    
    # Calculate optimal chunk size to have a balanced tree with minimum levels
    level_1_max = max_objects_per_composition
    level_2_max = level_1_max * max_objects_per_composition
    level_3_max = level_2_max * max_objects_per_composition
    
    if target_size_mb < level_2_max * 1024:  # If we can fit in 2 levels
        # Aim for 2 levels with balanced tree
        total_chunks = (target_size_mb + 1023) // 1024  # Ceiling division to get min chunks of 1GB
        chunk_size_mb = max(100, (target_size_mb + total_chunks - 1) // total_chunks)
    else:  # 3 or more levels
        # For very large files, use fixed 1GB chunks for predictability
        chunk_size_mb = 1024
    
    # Never go below minimum chunk size for performance reasons
    return max(10, chunk_size_mb)  # Allow smaller chunks for testing

def calculate_composition_stats(target_size_mb: int, chunk_size_mb: int) -> dict:
    """
    Calculate statistics about the composition process.
    
    Args:
        target_size_mb: Target file size in MB
        chunk_size_mb: Chunk size in MB
        
    Returns:
        Dictionary with composition statistics
    """
    max_objects_per_composition = 32
    
    # Calculate total number of chunks
    total_chunks = (target_size_mb + chunk_size_mb - 1) // chunk_size_mb
    
    # Calculate number of intermediate compositions needed
    if total_chunks <= max_objects_per_composition:
        levels = 1
        intermediate_blobs = 0
    else:
        # Calculate levels needed
        level_chunks = total_chunks
        level = 0
        intermediate_count = 0
        
        while level_chunks > max_objects_per_composition:
            level += 1
            groups = (level_chunks + max_objects_per_composition - 1) // max_objects_per_composition
            intermediate_count += groups
            level_chunks = groups
        
        levels = level + 1
        intermediate_blobs = intermediate_count
    
    return {
        "total_chunks": total_chunks,
        "composition_levels": levels,
        "intermediate_blobs": intermediate_blobs,
        "final_compositions": 1
    }

def calculate_optimal_file_split(total_size_mb: int, max_files: int = 0) -> Tuple[int, int]:
    """
    Calculate the optimal number of files and size per file based on total target size.
    
    Args:
        total_size_mb: Total size to generate across all files in MB
        max_files: Maximum number of files to create (0 for auto-determine)
        
    Returns:
        Tuple of (number of files, size per file in MB)
    """
    # Available CPU cores (for parallel processing)
    available_cores = os.cpu_count() or 4
    
    # Get available memory (in MB)
    # Use 50% of available memory as our target working limit
    try:
        available_memory_mb = psutil.virtual_memory().available // (1024 * 1024) // 2
    except:
        # If psutil is not available, assume a conservative 2GB
        available_memory_mb = 2 * 1024
    
    logger.info(f"Available memory for processing: {available_memory_mb} MB")
    
    # For very small sizes (< 100MB), just create one file
    if total_size_mb < 100:
        return 1, total_size_mb
        
    # For testing sizes (< 1GB), use 1 file
    if total_size_mb < 1024:
        return 1, total_size_mb
    
    # For small-medium sizes (1GB-10GB), check available memory
    if total_size_mb < 10 * 1024:
        # Split based on available memory (max 2GB per process)
        size_per_file = min(2 * 1024, available_memory_mb)
        num_files = (total_size_mb + size_per_file - 1) // size_per_file
        return min(num_files, available_cores), size_per_file
        
    # For large sizes (>10GB), balance memory usage vs parallelism
    # Limit size per file to avoid memory issues
    max_size_per_file = min(10 * 1024, available_memory_mb)  # Max 10GB per file
    min_size_per_file = 1 * 1024  # Min 1GB per file for efficiency
    
    if max_files > 0:
        # User specified max files
        num_files = max_files
        size_per_file = (total_size_mb + num_files - 1) // num_files
        
        # Adjust if size per file is too large for memory
        if size_per_file > max_size_per_file:
            size_per_file = max_size_per_file
            num_files = (total_size_mb + size_per_file - 1) // size_per_file
    else:
        # Auto determine based on memory constraints
        num_files = (total_size_mb + max_size_per_file - 1) // max_size_per_file
        size_per_file = (total_size_mb + num_files - 1) // num_files
        
        # Limit to available cores
        if num_files > available_cores:
            # Since we'll be running sequentially beyond cores, can make each job bigger
            num_files = available_cores
            size_per_file = (total_size_mb + num_files - 1) // num_files
    
    # Ensure we use at least one file
    num_files = max(1, num_files)
    
    return num_files, size_per_file

@dataclass
class GeneratorConfig:
    """Configuration for the CSV generator."""
    project_id: str
    bucket_name: str
    target_size_mb: int
    duplicate_pct: int = 20
    chunk_size_mb: Optional[int] = None  # Now optional, will be calculated if None
    log_frequency: Optional[int] = None  # Will be determined based on file size
    start_date: datetime = datetime(2025, 1, 1, 12, 0, 0)
    cursor_increment: timedelta = timedelta(minutes=1)
    cache_size: int = 10_000
    parallel_chunks: int = None  # Number of chunks to generate in parallel

    def __post_init__(self):
        # Auto-calculate optimal chunk size if not provided
        if self.chunk_size_mb is None:
            self.chunk_size_mb = calculate_optimal_chunk_size(self.target_size_mb)
            
        # Adjust log frequency based on target size
        if self.log_frequency is None:
            if self.target_size_mb < 100:  # < 100MB
                self.log_frequency = 1_000
            elif self.target_size_mb < 1024:  # < 1GB
                self.log_frequency = 10_000
            elif self.target_size_mb < 10 * 1024:  # < 10GB
                self.log_frequency = 100_000
            else:  # >= 10GB
                self.log_frequency = 1_000_000
        
        # Calculate parallel chunks if not provided
        if self.parallel_chunks is None:
            self.parallel_chunks = calculate_chunk_level_parallelism(
                self.target_size_mb, self.chunk_size_mb
            )
            
        # Print configuration details
        stats = calculate_composition_stats(self.target_size_mb, self.chunk_size_mb)
        logger.info(f"Target size: {self.target_size_mb} MB ({self.target_size_mb/1024:.2f} GB)")
        logger.info(f"Chunk size: {self.chunk_size_mb} MB")
        logger.info(f"Expected chunks: {stats['total_chunks']}")
        logger.info(f"Parallel chunk generation: {self.parallel_chunks}")
        logger.info(f"Composition levels: {stats['composition_levels']}")
        logger.info(f"Intermediate blobs: {stats['intermediate_blobs']}")
        logger.info(f"Log frequency: Every {self.log_frequency:,} rows")

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
            for _ in range(min(cache_size, 1000))  # Limit cache size for memory savings
        ]
        # Use a smaller sample of timezones to save memory
        all_timezones = list(pytz.all_timezones)
        self.timezones = random.sample(all_timezones, min(len(all_timezones), 50))

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
        self.data_generator = RandomDataGenerator(min(config.cache_size, 1000))  # Reduce cache size
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
    
    def _generate_chunk(self, chunk_index: int, start_row: int, start_pk: int, start_cursor: datetime) -> Tuple[str, int, int]:
        """
        Generate a single chunk of data and upload to GCS.
        
        Args:
            chunk_index: Index of this chunk
            start_row: Row number to start at
            start_pk: Primary key to start at
            start_cursor: Cursor time to start at
            
        Returns:
            Tuple of (blob_name, rows_generated, end_pk)
        """
        final_blob_name = self._get_final_blob_name(chunk_index)
        chunk_blob_name = f"{final_blob_name}.part_{chunk_index:05d}"
        
        buffer = io.StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        
        row_count = 0
        current_pk = start_pk
        cursor = start_cursor
        used_pks = []
        # For memory efficiency, limit the cache size
        max_pk_cache = min(1000, 10_000_000 // self.config.target_size_mb)
        
        # Fill the chunk
        while buffer.tell() < self.config.chunk_size_bytes:
            # Determine whether to use an existing PK or generate a new one
            if len(used_pks) > max_pk_cache and random.random() < (self.config.duplicate_pct / 100):
                row_pk = random.choice(used_pks)
            else:
                row_pk = current_pk
                used_pks.append(row_pk)
                current_pk += 1
            
            # Generate row data
            row_data = self.generate_row(row_pk, cursor)
            writer.writerow(row_data)
            
            # Update counters
            cursor += self.config.cursor_increment
            row_count += 1
            
            # Log progress occasionally
            if row_count % self.config.log_frequency == 0:
                logger.info(f"Chunk #{chunk_index}: Generated {row_count:,} rows")
        
        # Get final data
        data = buffer.getvalue()
        
        # Upload to GCS
        chunk_blob = self.bucket.blob(chunk_blob_name)
        encoded_data = data.encode("utf-8")
        chunk_size_mb = len(encoded_data) / (1024 * 1024)
        
        logger.info(f"Uploading chunk #{chunk_index:05d} ({row_count:,} rows, {chunk_size_mb:.2f} MB)")
        
        # Upload with retry
        max_retries = 3
        for retry in range(max_retries):
            try:
                chunk_blob.upload_from_string(
                    data,
                    content_type="text/csv",
                    timeout=300  # 5 minute timeout
                )
                break
            except Exception as e:
                if retry == max_retries - 1:
                    raise
                logger.warning(f"Upload failed, retry {retry+1}/{max_retries}: {e}")
                time.sleep(2 ** retry)  # Exponential backoff
        
        logger.info(f"Successfully uploaded chunk #{chunk_index:05d}")
        
        return chunk_blob_name, row_count, current_pk

    def _get_final_blob_name(self, file_index: Optional[int] = None) -> str:
        """Get the final blob name based on configuration."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        index_suffix = f"_{file_index:03d}" if file_index is not None else ""
        return f"data_export_{self.config.target_size_mb}MB_{timestamp}{index_suffix}.csv"

    def _clean_up_blobs(self, blob_names: List[str], batch_size: int = 20) -> None:
        """
        Clean up temporary blobs in batches to manage memory.
        
        Args:
            blob_names: List of blob names to delete
            batch_size: Batch size for deletion
        """
        if not blob_names:
            return
            
        total = len(blob_names)
        logger.info(f"Cleaning up {total} temporary blobs")
        
        for i in range(0, total, batch_size):
            batch = blob_names[i:i+batch_size]
            
            for name in batch:
                try:
                    blob = self.bucket.blob(name)
                    blob.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete {name}: {e}")
            
            if i + batch_size < total:
                logger.info(f"Deleted {i+batch_size}/{total} temporary blobs")
                
            # Small sleep to prevent overwhelming GCS and allow other processes to run
            time.sleep(0.05)
            
            # Force garbage collection after each batch for large jobs
            if total > 100:
                gc.collect()

    def _compose_chunks(self, final_blob_name: str, chunk_names: List[str]) -> None:
        """
        Compose chunks into final blob with multi-level composition.
        Memory-efficient version that works with blob names instead of blob objects.
        
        Args:
            final_blob_name: Name of the final output blob
            chunk_names: List of blob names to compose
        """
        if not chunk_names:
            raise ValueError("No chunks to compose")

        logger.info(f"Starting server-side composition of {len(chunk_names)} chunks into {final_blob_name}")

        # For laptop use, use a streaming approach to reduce memory consumption
        max_objects_per_composition = 32
        level = 0
        
        # Handle the case where we can compose directly
        if len(chunk_names) <= max_objects_per_composition:
            final_blob = self.bucket.blob(final_blob_name)
            source_blobs = [self.bucket.blob(name) for name in chunk_names]
            
            logger.info(f"Direct composition with {len(source_blobs)} blobs")
            final_blob.compose(source_blobs)
            
            # Clean up source blobs (by name to save memory)
            del source_blobs
            self._clean_up_blobs(chunk_names)
            
            final_blob.reload()
            final_size_gb = final_blob.size / (1024 * 1024 * 1024)
            logger.info(f"Successfully composed {final_blob_name} ({final_size_gb:.2f} GB)")
            return
        
        # Multi-level composition required - process level by level to save memory
        current_level_names = chunk_names.copy()
        intermediate_names = []
        
        while len(current_level_names) > max_objects_per_composition:
            level += 1
            logger.info(f"Processing composition level {level} with {len(current_level_names)} source blobs")
            
            # Calculate batches for this level
            groups = [current_level_names[i:i+max_objects_per_composition] 
                     for i in range(0, len(current_level_names), max_objects_per_composition)]
            
            next_level_names = []
            logger.info(f"Level {level}: Creating {len(groups)} intermediate blobs")
            
            # Process each group
            for i, group_names in enumerate(groups):
                # Create source blob objects (only when needed)
                group_blobs = [self.bucket.blob(name) for name in group_names]
                
                # Create intermediate blob
                intermediate_name = f"{final_blob_name}.L{level}_G{i:03d}"
                intermediate_blob = self.bucket.blob(intermediate_name)
                
                # Compose this group
                logger.info(f"Composing group {i+1}/{len(groups)} with {len(group_blobs)} blobs")
                intermediate_blob.compose(group_blobs)
                
                # Add to next level names
                next_level_names.append(intermediate_name)
                intermediate_names.append(intermediate_name)
                
                # Clean up this group's source blobs if they're not original chunks
                if level > 1:
                    self._clean_up_blobs(group_names)
                
                # Delete references to free memory
                del group_blobs
                
                # Force garbage collection for large jobs
                if len(groups) > 10:
                    gc.collect()
            
            # Move to next level
            current_level_names = next_level_names
            
            # Force garbage collection
            gc.collect()
        
        # Final composition (guaranteed ≤ 32 blobs)
        logger.info(f"Performing final composition with {len(current_level_names)} blobs")
        final_blob = self.bucket.blob(final_blob_name)
        final_level_blobs = [self.bucket.blob(name) for name in current_level_names]
        final_blob.compose(final_level_blobs)
        
        # Clean up the last level of intermediate blobs
        self._clean_up_blobs(current_level_names)
        del final_level_blobs
        
        # Clean up original chunks if we haven't already (level 1)
        if level == 1:
            logger.info("Cleaning up original chunk blobs")
            self._clean_up_blobs(chunk_names)
        
        # Get final size
        final_blob.reload()
        final_size_gb = final_blob.size / (1024 * 1024 * 1024)
        logger.info(f"Successfully composed {final_blob_name} ({final_size_gb:.2f} GB)")
        
        # Force garbage collection again
        gc.collect()
        
        logger.info(f"Composition complete: {final_blob_name} ({final_size_gb:.2f} GB)")

    def generate_csv(self, file_index: Optional[int] = None) -> str:
        """Generate and upload CSV file to GCS with parallel chunk generation."""
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
        
        # Calculate total number of chunks needed
        total_chunks = (self.config.target_size_bytes + self.config.chunk_size_bytes - 1) // self.config.chunk_size_bytes
        estimated_bytes_per_row = 200  # Rough estimation
        estimated_rows_per_chunk = self.config.chunk_size_bytes // estimated_bytes_per_row
        
        logger.info(f"Preparing to generate {total_chunks} chunks with approximately {estimated_rows_per_chunk:,} rows each")
        
        # Use parallel chunk generation
        chunk_names = []
        total_rows = 0
        
        # Process chunks in batches to avoid overwhelming the system
        chunk_batch_size = self.config.parallel_chunks
        
        for batch_start in range(0, total_chunks, chunk_batch_size):
            batch_end = min(batch_start + chunk_batch_size, total_chunks)
            batch_indices = list(range(batch_start, batch_end))
            
            logger.info(f"Processing chunk batch {batch_start}-{batch_end-1} ({len(batch_indices)} chunks)")
            
            # Function for chunk generation (for parallel execution)
            def generate_chunk_task(chunk_idx):
                """Function to generate a single chunk (for use with ThreadPoolExecutor)"""
                # Each chunk gets its own PK range and cursor range
                chunk_start_row = chunk_idx * estimated_rows_per_chunk
                chunk_start_cursor = self.config.start_date + self.config.cursor_increment * chunk_start_row
                
                # Generate an appropriate starting PK based on chunk index
                # Use a large offset to prevent overlaps between chunks
                chunk_start_pk = 1 + chunk_idx * (estimated_rows_per_chunk * 2)
                
                logger.info(f"Starting chunk #{chunk_idx:05d} generation")
                
                try:
                    buffer = io.StringIO()
                    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
                    
                    row_count = 0
                    current_pk = chunk_start_pk
                    cursor = chunk_start_cursor
                    
                    # For memory efficiency, use a smaller PK cache for large files
                    max_pk_cache = min(1000, 1_000_000 // self.config.target_size_mb)
                    used_pks = []
                    
                    # Log progress more frequently
                    progress_log_interval = min(100_000, self.config.log_frequency // 10)
                    last_log_size = 0
                    start_time = time.time()
                    
                    # Fill the chunk
                    while buffer.tell() < self.config.chunk_size_bytes:
                        # Determine whether to use an existing PK or generate a new one
                        if used_pks and random.random() < (self.config.duplicate_pct / 100):
                            row_pk = random.choice(used_pks)
                        else:
                            row_pk = current_pk
                            if len(used_pks) < max_pk_cache:
                                used_pks.append(row_pk)
                            current_pk += 1
                        
                        # Generate row data
                        row_data = self.generate_row(row_pk, cursor)
                        writer.writerow(row_data)
                        
                        # Update counters
                        cursor += self.config.cursor_increment
                        row_count += 1
                        
                        # Log progress more frequently with size information
                        if row_count % progress_log_interval == 0:
                            current_size = buffer.tell()
                            size_mb = current_size / (1024 * 1024)
                            mb_since_last = (current_size - last_log_size) / (1024 * 1024)
                            percent_complete = (size_mb / self.config.chunk_size_mb) * 100
                            elapsed = time.time() - start_time
                            speed = mb_since_last / (elapsed if elapsed > 0 else 1)
                            
                            logger.info(
                                f"Chunk #{chunk_idx:05d}: {row_count:,} rows, "
                                f"{size_mb:.2f} MB ({percent_complete:.1f}%), "
                                f"generating at {speed:.2f} MB/s"
                            )
                            
                            # Reset for next interval
                            last_log_size = current_size
                            start_time = time.time()
                    
                    # Get final data
                    data = buffer.getvalue()
                    encoded_data = data.encode("utf-8")
                    chunk_size_mb = len(encoded_data) / (1024 * 1024)
                    
                    logger.info(
                        f"Chunk #{chunk_idx:05d} generation complete: "
                        f"{row_count:,} rows, {chunk_size_mb:.2f} MB"
                    )
                    
                    # Upload to GCS
                    chunk_blob_name = f"{final_blob_name}.part_{chunk_idx:05d}"
                    chunk_blob = self.bucket.blob(chunk_blob_name)
                    
                    logger.info(f"Uploading chunk #{chunk_idx:05d} to GCS...")
                    
                    # Upload with retry
                    max_retries = 3
                    for retry in range(max_retries):
                        try:
                            upload_start = time.time()
                            chunk_blob.upload_from_string(
                                data,
                                content_type="text/csv",
                                timeout=300  # 5 minute timeout
                            )
                            upload_duration = time.time() - upload_start
                            upload_speed = chunk_size_mb / upload_duration if upload_duration > 0 else 0
                            
                            logger.info(
                                f"Successfully uploaded chunk #{chunk_idx:05d} "
                                f"({chunk_size_mb:.2f} MB at {upload_speed:.2f} MB/s)"
                            )
                            break
                        except Exception as e:
                            if retry == max_retries - 1:
                                raise
                            logger.warning(f"Upload failed for chunk #{chunk_idx:05d}, retry {retry+1}/{max_retries}: {e}")
                            time.sleep(2 ** retry)  # Exponential backoff
                    
                    return chunk_blob_name, row_count
                except Exception as e:
                    logger.error(f"Error generating chunk #{chunk_idx:05d}: {str(e)}")
                    raise
            
            # Use thread pool for parallel chunk generation
            batch_chunk_names = []
            batch_rows = 0
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch_indices)) as executor:
                # Submit all tasks
                futures = {
                    executor.submit(generate_chunk_task, idx): idx 
                    for idx in batch_indices
                }
                
                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    chunk_idx = futures[future]
                    try:
                        chunk_name, rows = future.result()
                        batch_chunk_names.append(chunk_name)
                        batch_rows += rows
                    except Exception as e:
                        logger.error(f"Chunk #{chunk_idx} failed: {str(e)}")
            
            # Add batch results to overall results
            chunk_names.extend(batch_chunk_names)
            total_rows += batch_rows
            
            logger.info(f"Completed batch {batch_start}-{batch_end-1}: {batch_rows:,} rows generated")
            
            # Clean up between batches
            gc.collect()
        
        # Sort chunk names to ensure proper order
        chunk_names.sort()
        
        # Compose chunks into final file
        self._compose_chunks(final_blob_name, chunk_names)
        
        # Calculate statistics
        duration = time.time() - start_time
        mb_written = (self.config.target_size_bytes) / (1024 * 1024)
        speed_mbps = mb_written / duration if duration > 0 else 0
        
        summary = (
            f"Generated {final_blob_name}: {total_rows:,} rows, "
            f"{mb_written:.2f} MB in {duration:.2f}s ({speed_mbps:.2f} MB/s)"
        )
        logger.info(summary)
        
        return summary

def main(total_size_mb: int, max_files: int = 0, project_id: str = "dataline-integration-testing", 
         bucket_name: str = "no_raw_tables", parallel_chunks: int = None) -> None:
    """
    Generate CSV file(s) with a total size of specified MB.
    Optimized for VM environments with multiple CPUs.
    
    Args:
        total_size_mb: Total size to generate in MB
        max_files: Maximum number of files to create (0 for auto-determine)
        project_id: GCS project ID
        bucket_name: GCS bucket name
        parallel_chunks: Number of chunks to generate in parallel (None for auto-determine)
    """
    # Available CPU cores for logging
    available_cores = os.cpu_count() or 4
    
    # If parallel_chunks is None, set it based on CPU count
    if parallel_chunks is None:
        parallel_chunks = available_cores
    
    logger.info(f"Generating {total_size_mb} MB total data")
    logger.info(f"Available CPU cores: {available_cores}")
    logger.info(f"Using {parallel_chunks} parallel chunk generators")
    
    # Create a single file with optimized parallel chunk generation
    config = GeneratorConfig(
        project_id=project_id,
        bucket_name=bucket_name,
        target_size_mb=total_size_mb,
        parallel_chunks=parallel_chunks
    )
    
    # Create a single generator instance
    generator = CSVGenerator(config)
    
    # Generate the file
    result = generator.generate_csv()
    
    logger.info(f"Completed generation: {result}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Generate CSV files of specified total size with parallel processing')
    parser.add_argument('--size', type=int, default=1024, help='Total size to generate in MB (default: 1024 MB)')
    parser.add_argument('--project', type=str, default="dataline-integration-testing", 
                        help='GCS project ID')
    parser.add_argument('--bucket', type=str, default="no_raw_tables", 
                        help='GCS bucket name')
    parser.add_argument('--parallel-chunks', type=int, default=None,
                        help='Number of chunks to generate in parallel (default: CPU count)')
    
    args = parser.parse_args()
    
    # Generate file
    main(
        total_size_mb=args.size,
        project_id=args.project,
        bucket_name=args.bucket,
        parallel_chunks=args.parallel_chunks
    )