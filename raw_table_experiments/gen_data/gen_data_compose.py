import os
import random
import string
import json
import logging
import io
import csv
import time
import psutil
import numpy as np
import sys
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple, Generator
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date, time as dt_time, timedelta
import argparse
import gc
import yaml

import pytz
from google.cloud import storage
from google.cloud.storage.blob import Blob

# -------------------------------
# LOGGING SETUP
# -------------------------------
def setup_logging(log_level=logging.INFO):
    """Set up structured logging with configurable level."""
    logging.basicConfig(
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        level=log_level,
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# -------------------------------
# CONFIGURATION UTILITIES
# -------------------------------
@dataclass
class GeneratorConfig:
    """Configuration for the data generator."""
    project_id: str
    bucket_name: str
    target_size_mb: int
    output_format: str = "csv"
    duplicate_pct: int = 20
    chunk_size_mb: Optional[int] = None  # Will be calculated if None
    log_frequency: Optional[int] = None  # Will be determined based on file size
    start_date: datetime = field(default_factory=lambda: datetime(2025, 1, 1, 12, 0, 0))
    cursor_increment: timedelta = field(default_factory=lambda: timedelta(minutes=1))
    cache_size: int = 10_000
    parallel_chunks: Optional[int] = None  # Number of chunks to generate in parallel
    retry_count: int = 5
    base_retry_delay: float = 1.0
    compression: Optional[str] = None  # None, 'gzip', etc.
    checkpoint_dir: Optional[str] = None
    schema_config: Optional[Dict[str, Any]] = None
    memory_threshold_mb: int = 1000  # Memory warning threshold
    upload_batch_size: int = 20  # Batch size for cleanup operations
    max_upload_timeout: int = 300  # Timeout for uploads in seconds

    def __post_init__(self):
        # Auto-calculate optimal chunk size if not provided
        if self.chunk_size_mb is None:
            self.chunk_size_mb = self._calculate_optimal_chunk_size()
            
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
            self.parallel_chunks = self._calculate_chunk_level_parallelism()
        
        # Create checkpoint directory if specified
        if self.checkpoint_dir:
            os.makedirs(self.checkpoint_dir, exist_ok=True)
            
        # Use default schema if none provided
        if self.schema_config is None:
            self.schema_config = self._default_schema()
            
        # Print configuration details
        stats = self._calculate_composition_stats()
        logger.info(f"Target size: {self.target_size_mb} MB ({self.target_size_mb/1024:.2f} GB)")
        logger.info(f"Chunk size: {self.chunk_size_mb} MB")
        logger.info(f"Expected chunks: {stats['total_chunks']}")
        logger.info(f"Parallel chunk generation: {self.parallel_chunks}")
        logger.info(f"Composition levels: {stats['composition_levels']}")
        logger.info(f"Intermediate blobs: {stats['intermediate_blobs']}")
        logger.info(f"Log frequency: Every {self.log_frequency:,} rows")
        logger.info(f"Output format: {self.output_format}" + 
                   (f" with {self.compression} compression" if self.compression else ""))

    def _default_schema(self) -> Dict[str, Dict[str, Any]]:
        """Create a default schema configuration for data generation."""
        return {
            "id": {"type": "int", "min": 1, "max": 9999999},
            "timestamp": {"type": "datetime", "format": "iso"},
            "name": {"type": "string", "length": 8},
            "active": {"type": "bool"},
            "count": {"type": "int", "min": 0, "max": 1000},
            "value": {"type": "float", "min": 0, "max": 1000, "precision": 2},
            "date": {"type": "date", "format": "iso"},
            "datetime_tz": {"type": "datetime_tz", "format": "iso"},
            "datetime": {"type": "datetime", "format": "iso"},
            "time_tz": {"type": "time_tz"},
            "time": {"type": "time"},
            "array_data": {"type": "array", "max_length": 5},
            "json_data": {"type": "json_object"},
        }

    def _calculate_optimal_chunk_size(self) -> int:
        """
        Calculate optimal chunk size based on target file size to minimize composition levels.
        
        Returns:
            Optimal chunk size in MB
        """
        # GCS compose limit is 32 objects
        max_objects_per_composition = 32
        
        # For very small files (< 32 MB), use a minimum chunk size
        if self.target_size_mb < 32:
            return max(1, self.target_size_mb // 2)  # Use at most 2 chunks for tiny files
        
        # For small files (< 32 GB), we can use a single level of composition
        if self.target_size_mb < max_objects_per_composition * 1024:  # If target < 32 GB
            # Aim for one level of composition with equal sized chunks
            return max(100, self.target_size_mb // max_objects_per_composition)
        
        # For larger files, we need multiple levels of composition
        # Calculate how many chunks we'd need at different levels
        
        # For a balanced tree, we want each node to have close to max_objects_per_composition children
        level_1_max = max_objects_per_composition
        level_2_max = level_1_max * max_objects_per_composition
        
        if self.target_size_mb < level_2_max * 1024:  # If we can fit in 2 levels
            # Aim for 2 levels with balanced tree
            total_chunks = (self.target_size_mb + 1023) // 1024  # Ceiling division to get min chunks of 1GB
            chunk_size_mb = max(100, (self.target_size_mb + total_chunks - 1) // total_chunks)
        else:  # 3 or more levels
            # For very large files, use fixed 1GB chunks for predictability
            chunk_size_mb = 1024
        
        # Never go below minimum chunk size for performance reasons
        return max(10, chunk_size_mb)

    def _calculate_chunk_level_parallelism(self) -> int:
        """
        Calculate how many chunks to generate in parallel based on system resources.
        
        Returns:
            Number of chunks to generate in parallel
        """
        max_parallel_chunks = os.cpu_count() or 4
        
        # Calculate estimated total chunks
        total_chunks = (self.target_size_mb + self.chunk_size_mb - 1) // self.chunk_size_mb
        
        # For very small files with few chunks, limit parallelism
        if total_chunks < 4:
            return min(total_chunks, max_parallel_chunks)
        
        # For medium files, use available cores
        if total_chunks < 16:
            return min(total_chunks, max_parallel_chunks)
        
        # For large files with many chunks, increase parallelism
        return max_parallel_chunks

    def _calculate_composition_stats(self) -> dict:
        """
        Calculate statistics about the composition process.
        
        Returns:
            Dictionary with composition statistics
        """
        max_objects_per_composition = 32
        
        # Calculate total number of chunks
        total_chunks = (self.target_size_mb + self.chunk_size_mb - 1) // self.chunk_size_mb
        
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

    @property
    def chunk_size_bytes(self) -> int:
        return self.chunk_size_mb * 1024 * 1024

    @property
    def target_size_bytes(self) -> int:
        return self.target_size_mb * 1024 * 1024
    
    @classmethod
    def from_file(cls, config_path: str) -> 'GeneratorConfig':
        """Load configuration from a file (YAML or JSON)."""
        with open(config_path, 'r') as f:
            if config_path.endswith('.yaml') or config_path.endswith('.yml'):
                config_data = yaml.safe_load(f)
            else:
                config_data = json.load(f)
                
        # Convert date strings to datetime objects if needed
        if 'start_date' in config_data and isinstance(config_data['start_date'], str):
            config_data['start_date'] = datetime.fromisoformat(config_data['start_date'])
            
        # Convert cursor_increment to timedelta if needed
        if 'cursor_increment' in config_data and isinstance(config_data['cursor_increment'], dict):
            increment = config_data['cursor_increment']
            config_data['cursor_increment'] = timedelta(**increment)
            
        return cls(**config_data)
    
    def save_to_file(self, file_path: str) -> None:
        """Save current configuration to a file."""
        # Convert special types to serializable format
        config_dict = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                config_dict[key] = value.isoformat()
            elif isinstance(value, timedelta):
                config_dict[key] = {
                    'days': value.days,
                    'seconds': value.seconds,
                    'microseconds': value.microseconds
                }
            else:
                config_dict[key] = value
                
        # Save to file
        with open(file_path, 'w') as f:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                yaml.dump(config_dict, f)
            else:
                json.dump(config_dict, f, indent=2)

# -------------------------------
# BASE GENERATOR CLASS
# -------------------------------
class BaseGenerator:
    """Base class for data generators with common functionality."""
    
    def __init__(self, config: GeneratorConfig):
        self.config = config
        self.storage_client = storage.Client(project=config.project_id)
        self.bucket = self.storage_client.bucket(config.bucket_name)
        self.job_id = f"job_{int(time.time())}"
        
    def check_memory_usage(self) -> float:
        """
        Monitor memory usage and log warnings if threshold exceeded.
        
        Returns:
            Current memory usage in MB
        """
        try:
            mem_usage = psutil.Process().memory_info().rss / (1024 * 1024)
            if mem_usage > self.config.memory_threshold_mb:
                logger.warning(f"High memory usage detected: {mem_usage:.2f} MB")
            return mem_usage
        except Exception as e:
            logger.warning(f"Failed to check memory usage: {e}")
            return 0
    
    def robust_upload(self, blob: Blob, data: str, content_type: str = "text/plain") -> bool:
        """
        More robust upload with exponential backoff and jitter.
        
        Args:
            blob: GCS blob to upload to
            data: Data to upload
            content_type: Content type of the data
            
        Returns:
            True if upload succeeded, raises exception otherwise
        """
        for attempt in range(self.config.retry_count):
            try:
                # Upload the data
                blob.upload_from_string(
                    data,
                    content_type=content_type,
                    timeout=self.config.max_upload_timeout
                )
                return True
            except Exception as e:
                if attempt == self.config.retry_count - 1:
                    raise
                
                # Calculate delay with exponential backoff and jitter
                delay = self.config.base_retry_delay * (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Upload failed (attempt {attempt+1}/{self.config.retry_count}): {str(e)}")
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
                
        # This shouldn't be reached due to the raise in the loop
        raise Exception(f"Failed to upload after {self.config.retry_count} attempts")
    
    def clean_up_blobs(self, blob_names: List[str]) -> None:
        """
        Clean up temporary blobs in batches to manage memory.
        
        Args:
            blob_names: List of blob names to delete
        """
        if not blob_names:
            return
            
        total = len(blob_names)
        logger.info(f"Cleaning up {total} temporary blobs")
        
        for i in range(0, total, self.config.upload_batch_size):
            batch = blob_names[i:i+self.config.upload_batch_size]
            
            for name in batch:
                try:
                    blob = self.bucket.blob(name)
                    blob.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete {name}: {e}")
            
            if i + self.config.upload_batch_size < total:
                logger.info(f"Deleted {i+self.config.upload_batch_size}/{total} temporary blobs")
                
            # Small sleep to prevent overwhelming GCS and allow other processes to run
            time.sleep(0.05)
            
            # Force garbage collection after each batch for large jobs
            if total > 100:
                gc.collect()
                
    def compose_chunks(self, final_blob_name: str, chunk_names: List[str]) -> None:
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
            self.clean_up_blobs(chunk_names)
            
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
                    self.clean_up_blobs(group_names)
                
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
        self.clean_up_blobs(current_level_names)
        del final_level_blobs
        
        # Clean up original chunks if we haven't already (level 1)
        if level == 1:
            logger.info("Cleaning up original chunk blobs")
            self.clean_up_blobs(chunk_names)
        
        # Get final size
        final_blob.reload()
        final_size_gb = final_blob.size / (1024 * 1024 * 1024)
        logger.info(f"Successfully composed {final_blob_name} ({final_size_gb:.2f} GB)")
        
        # Force garbage collection again
        gc.collect()
        
        logger.info(f"Composition complete: {final_blob_name} ({final_size_gb:.2f} GB)")
    
    def save_checkpoint(self, state: Dict[str, Any]) -> None:
        """
        Save current processing state to allow resume after failure.
        
        Args:
            state: Current processing state
        """
        if not self.config.checkpoint_dir:
            logger.warning("Checkpoint directory not configured, skipping checkpoint")
            return
            
        try:
            checkpoint_path = os.path.join(self.config.checkpoint_dir, f"checkpoint_{self.job_id}.json")
            with open(checkpoint_path, "w") as f:
                json.dump(state, f)
            logger.info(f"Saved checkpoint to {checkpoint_path}")
        except Exception as e:
            logger.warning(f"Failed to save checkpoint: {e}")
    
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent checkpoint if available.
        
        Returns:
            Checkpoint state if found, None otherwise
        """
        if not self.config.checkpoint_dir:
            return None
            
        try:
            checkpoints = []
            for f in os.listdir(self.config.checkpoint_dir):
                if f.startswith("checkpoint_") and f.endswith(".json"):
                    checkpoint_path = os.path.join(self.config.checkpoint_dir, f)
                    checkpoints.append((os.path.getmtime(checkpoint_path), checkpoint_path))
            
            if not checkpoints:
                return None
                
            # Get the most recent checkpoint
            _, latest_checkpoint = sorted(checkpoints, reverse=True)[0]
            
            with open(latest_checkpoint, "r") as f:
                state = json.load(f)
            
            logger.info(f"Loaded checkpoint from {latest_checkpoint}")
            return state
        except Exception as e:
            logger.warning(f"Failed to load checkpoint: {e}")
            return None
            
    def log_progress(self, current: int, total: int, start_time: float) -> None:
        """
        Log progress with ETA calculation.
        
        Args:
            current: Current progress value
            total: Total expected value
            start_time: Start time in seconds since epoch
        """
        elapsed = time.time() - start_time
        progress = current / total if total > 0 else 0
        
        # Avoid division by zero
        if progress > 0:
            eta = (elapsed / progress) - elapsed
        else:
            eta = 0
            
        logger.info({
            "progress": f"{progress:.1%}",
            "current": current,
            "total": total,
            "elapsed": f"{elapsed:.2f}s",
            "eta": f"{eta:.2f}s"
        })
    
    def get_final_blob_name(self, file_index: Optional[int] = None) -> str:
        """
        Get the final blob name based on configuration.
        
        Args:
            file_index: Optional file index for multi-file generation
            
        Returns:
            Blob name
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        index_suffix = f"_{file_index:03d}" if file_index is not None else ""
        extension = f".{self.config.output_format}"
        
        if self.config.compression:
            extension += f".{self.config.compression}"
            
        return f"data_export_{self.config.target_size_mb}MB_{timestamp}{index_suffix}{extension}"

# -------------------------------
# RANDOM DATA GENERATOR
# -------------------------------
class RandomDataGenerator:
    """Handles generation of random data with caching and pre-fetching."""
    
    def __init__(self, schema_config: Dict[str, Dict[str, Any]], cache_size: int = 10_000):
        self.schema_config = schema_config
        self.cache_size = min(cache_size, 10000)  # Limit cache size for memory savings
        
        # Initialize caches
        self._init_caches()
        
        # Pre-fetch common random data
        self._prefetch_random_data()
        
        # Use a smaller sample of timezones to save memory
        all_timezones = list(pytz.all_timezones)
        self.timezones = random.sample(all_timezones, min(len(all_timezones), 50))
        
        # Track cache hits/misses for optimization
        self.cache_hits = 0
        self.cache_misses = 0

    def _init_caches(self) -> None:
        """Initialize caches for different data types."""
        self.string_cache = {}
        self.int_cache = {}
        self.float_cache = {}
        self.bool_cache = [True, False]
        self.date_cache = []
        self.time_cache = []
        self.json_cache = []

    def _prefetch_random_data(self) -> None:
        """Pre-generate random data to reduce generation overhead."""
        # Pre-generate strings of different lengths
        for length in [8, 16, 32]:
            self.string_cache[length] = [
                ''.join(random.choices(string.ascii_letters, k=length))
                for _ in range(min(self.cache_size // 3, 1000))
            ]
            
        # Pre-generate integers for common ranges
        for min_val, max_val in [(0, 1000), (1, 9999)]:
            cache_key = f"{min_val}_{max_val}"
            self.int_cache[cache_key] = np.random.randint(
                min_val, max_val, size=min(self.cache_size, 1000)
            ).tolist()
            
        # Pre-generate floats
        self.float_cache[(0, 1000)] = np.random.uniform(
            0, 1000, size=min(self.cache_size, 1000)
        ).tolist()
        
        # Pre-generate dates (last 5 years)
        start_year = datetime.now().year - 5
        end_year = datetime.now().year
        
        base_date = date(start_year, 1, 1)
        days_range = (date(end_year, 12, 31) - base_date).days
        
        self.date_cache = [
            base_date + timedelta(days=random.randint(0, days_range))
            for _ in range(min(self.cache_size, 500))
        ]
        
        # Pre-generate times
        self.time_cache = [
            dt_time(
                random.randint(0, 23),
                random.randint(0, 59),
                random.randint(0, 59)
            )
            for _ in range(min(self.cache_size, 500))
        ]
        
        # Pre-generate some small JSON objects
        self.json_cache = [
            {
                "id": random.randint(1, 9999),
                "name": ''.join(random.choices(string.ascii_letters, k=8)),
                "active": random.choice([True, False]),
                "score": round(random.uniform(0, 100), 2)
            }
            for _ in range(min(self.cache_size // 10, 100))
        ]

    def random_string(self, length: int = 8) -> str:
        """Generate a random string of specified length."""
        if length in self.string_cache and self.string_cache[length]:
            self.cache_hits += 1
            return random.choice(self.string_cache[length])
        
        self.cache_misses += 1
        return ''.join(random.choices(string.ascii_letters, k=length))

    def random_bool(self) -> bool:
        """Generate a random boolean value."""
        return random.choice(self.bool_cache)

    def random_int(self, min_val: int = 0, max_val: int = 1000) -> int:
        """Generate a random integer in the specified range."""
        cache_key = f"{min_val}_{max_val}"
        
        if cache_key in self.int_cache and self.int_cache[cache_key]:
            self.cache_hits += 1
            return random.choice(self.int_cache[cache_key])
        
        self.cache_misses += 1
        return random.randint(min_val, max_val)

    def random_float(self, min_val: float = 0, max_val: float = 1000, precision: int = 2) -> float:
        """Generate a random float in the specified range with given precision."""
        cache_key = (min_val, max_val)
        
        if cache_key in self.float_cache and self.float_cache[cache_key]:
            self.cache_hits += 1
            value = random.choice(self.float_cache[cache_key])
            return round(value, precision)
        
        self.cache_misses += 1
        return round(random.uniform(min_val, max_val), precision)

    def random_date(self, start_year: int = 2020, end_year: int = 2025) -> date:
        """Generate a random date in the specified year range."""
        if self.date_cache:
            self.cache_hits += 1
            return random.choice(self.date_cache)
            
        self.cache_misses += 1
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        delta = end_date - start_date
        random_days = random.randint(0, delta.days)
        return start_date + timedelta(days=random_days)

    def random_datetime_tz(self, start_year: int = 2020, end_year: int = 2025) -> datetime:
        """Generate a random datetime with timezone in the specified year range."""
        naive_dt = self._random_datetime(start_year, end_year)
        timezone = random.choice(self.timezones)
        return pytz.timezone(timezone).localize(naive_dt)

    def _random_datetime(self, start_year: int = 2020, end_year: int = 2025) -> datetime:
        """Generate a random naive datetime in the specified year range."""
        start_dt = datetime(start_year, 1, 1)
        end_dt = datetime(end_year, 12, 31, 23, 59, 59)
        delta = end_dt - start_dt
        random_sec = random.randint(0, int(delta.total_seconds()))
        return start_dt + timedelta(seconds=random_sec)

    def random_time(self) -> dt_time:
        """Generate a random time."""
        if self.time_cache:
            self.cache_hits += 1
            return random.choice(self.time_cache)
            
        self.cache_misses += 1
        return dt_time(
            random.randint(0, 23),
            random.randint(0, 59),
            random.randint(0, 59)
        )

    def random_time_with_timezone(self) -> str:
        """Generate a random time string with timezone."""
        dt_with_tz = self.random_datetime_tz()
        return dt_with_tz.isoformat().split("T")[1]

    def random_array(self, max_length: int = 5) -> List[Any]:
        """Generate a random array with mixed types."""
        arr_length = random.randint(1, max_length)
        return [
            self.random_int(0, 50) if self.random_bool() else self.random_string()
            for _ in range(arr_length)
        ]

    def random_json_object(self) -> Dict[str, Any]:
        """Generate a random JSON object."""
        if self.json_cache:
            self.cache_hits += 1
            # Return a deep copy to avoid modifying the cache
            return json.loads(json.dumps(random.choice(self.json_cache)))
            
        self.cache_misses += 1
        return {
            "id": self.random_int(1, 9999),
            "name": self.random_string(),
            "active": self.random_bool(),
            "score": self.random_float(0, 100)
        }
        
    def generate_value(self, field_config: Dict[str, Any]) -> Any:
        """Generate a value based on field configuration."""
        field_type = field_config.get("type", "string")
        
        if field_type == "string":
            length = field_config.get("length", 8)
            return self.random_string(length)
            
        elif field_type == "int":
            min_val = field_config.get("min", 0)
            max_val = field_config.get("max", 1000)
            return self.random_int(min_val, max_val)
            
        elif field_type == "float":
            min_val = field_config.get("min", 0)
            max_val = field_config.get("max", 1000)
            precision = field_config.get("precision", 2)
            return self.random_float(min_val, max_val, precision)
            
        elif field_type == "bool":
            return self.random_bool()
            
        elif field_type == "date":
            start_year = field_config.get("start_year", 2020)
            end_year = field_config.get("end_year", 2025)
            date_value = self.random_date(start_year, end_year)
            
            if field_config.get("format") == "iso":
                return date_value.isoformat()
            return date_value
            
        elif field_type == "datetime":
            start_year = field_config.get("start_year", 2020)
            end_year = field_config.get("end_year", 2025)
            dt_value = self._random_datetime(start_year, end_year)
            
            if field_config.get("format") == "iso":
                return dt_value.isoformat()
            return dt_value
            
        elif field_type == "datetime_tz":
            start_year = field_config.get("start_year", 2020)
            end_year = field_config.get("end_year", 2025)
            dt_value = self.random_datetime_tz(start_year, end_year)
            
            if field_config.get("format") == "iso":
                return dt_value.isoformat()
            return dt_value
            
        elif field_type == "time":
            time_value = self.random_time()
            
            if field_config.get("format") == "iso":
                return time_value.isoformat()
            return time_value
            
        elif field_type == "time_tz":
            return self.random_time_with_timezone()
            
        elif field_type == "array":
            max_length = field_config.get("max_length", 5)
            array_value = self.random_array(max_length)
            
            # Always serialize arrays to JSON strings for database compatibility
            return json.dumps(array_value)
            
        elif field_type == "json_object":
            obj_value = self.random_json_object()
            
            # Always serialize JSON objects to strings for database compatibility
            return json.dumps(obj_value)
            
        # Default case
        return self.random_string()

# -------------------------------
# CSV GENERATOR
# -------------------------------
class CSVGenerator(BaseGenerator):
    """Handles CSV file generation and upload to GCS."""

    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        self.data_generator = RandomDataGenerator(config.schema_config, config.cache_size)
        
        # Create CSV-specific headers
        self.headers = list(config.schema_config.keys())
        
    def generate_row(self, pk: int, cursor_time: datetime) -> List[Any]:
        """
        Generate a single row of data.
        
        Args:
            pk: Primary key value
            cursor_time: Current cursor time
            
        Returns:
            List of values representing a row
        """
        row = []
        
        for field_name, field_config in self.config.schema_config.items():
            # Special handling for id and timestamp fields
            if field_name == "id":
                row.append(pk)
            elif field_name == "timestamp":
                row.append(cursor_time.isoformat())
            else:
                row.append(self.data_generator.generate_value(field_config))
                
        return row
    
    def generate_chunk_data(self, chunk_index: int, start_pk: int, start_cursor: datetime, 
                           used_pks: List[int]) -> Tuple[str, int, int, List[int]]:
        """
        Generate a single chunk of data.
        
        Args:
            chunk_index: Index of this chunk
            start_pk: Primary key to start at
            start_cursor: Cursor time to start at
            used_pks: List of already used primary keys
            
        Returns:
            Tuple of (data, rows_generated, end_pk, updated_used_pks)
        """
        buffer = io.StringIO()
        writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers for the first chunk
        if chunk_index == 0:
            writer.writerow(self.headers)
        
        row_count = 0
        current_pk = start_pk
        cursor = start_cursor
        
        # For memory efficiency, limit the cache size
        max_pk_cache = min(1000, 10_000_000 // self.config.target_size_mb)
        local_used_pks = used_pks.copy() if len(used_pks) <= max_pk_cache else []
        
        # Log start of generation
        logger.info(f"Starting generation of chunk #{chunk_index:05d} from PK={start_pk}")
        start_time = time.time()
        last_log_time = start_time
        
        # Fill the chunk
        while buffer.tell() < self.config.chunk_size_bytes:
            # Determine whether to use an existing PK or generate a new one
            if local_used_pks and random.random() < (self.config.duplicate_pct / 100):
                row_pk = random.choice(local_used_pks)
            else:
                row_pk = current_pk
                if len(local_used_pks) < max_pk_cache:
                    local_used_pks.append(row_pk)
                current_pk += 1
            
            # Generate row data
            row_data = self.generate_row(row_pk, cursor)
            writer.writerow(row_data)
            
            # Update counters
            cursor += self.config.cursor_increment
            row_count += 1
            
            # Log progress based on time rather than row count for large files
            current_time = time.time()
            if (row_count % self.config.log_frequency == 0 or 
                (current_time - last_log_time) > 60):  # Log at least every minute
                
                current_size = buffer.tell()
                size_mb = current_size / (1024 * 1024)
                elapsed = current_time - start_time
                rows_per_sec = row_count / elapsed if elapsed > 0 else 0
                
                logger.info(
                    f"Chunk #{chunk_index:05d}: {row_count:,} rows, "
                    f"{size_mb:.2f} MB ({size_mb/self.config.chunk_size_mb*100:.1f}%), "
                    f"rate: {rows_per_sec:.1f} rows/sec"
                )
                
                # Update log time
                last_log_time = current_time
                
                # Check memory usage occasionally
                self.check_memory_usage()
        
        # Get final data
        data = buffer.getvalue()
        
        # Calculate statistics
        chunk_size_mb = len(data.encode("utf-8")) / (1024 * 1024)
        elapsed = time.time() - start_time
        rows_per_sec = row_count / elapsed if elapsed > 0 else 0
        
        logger.info(
            f"Chunk #{chunk_index:05d} generated: {row_count:,} rows, "
            f"{chunk_size_mb:.2f} MB in {elapsed:.2f}s ({rows_per_sec:.1f} rows/sec)"
        )
        
        return data, row_count, current_pk, local_used_pks

    def upload_chunk(self, chunk_index: int, data: str, 
                    final_blob_name: str) -> str:
        """
        Upload a chunk to GCS.
        
        Args:
            chunk_index: Index of the chunk
            data: Data to upload
            final_blob_name: Name of the final blob
            
        Returns:
            Name of the uploaded chunk blob
        """
        chunk_blob_name = f"{final_blob_name}.part_{chunk_index:05d}"
        chunk_blob = self.bucket.blob(chunk_blob_name)
        
        # Get data size
        encoded_data = data.encode("utf-8")
        chunk_size_mb = len(encoded_data) / (1024 * 1024)
        
        logger.info(f"Uploading chunk #{chunk_index:05d} ({chunk_size_mb:.2f} MB)")
        
        start_time = time.time()
        
        try:
            # Use robust upload with retry
            self.robust_upload(chunk_blob, data, content_type="text/csv")
            
            # Log success with timing information
            elapsed = time.time() - start_time
            upload_speed = chunk_size_mb / elapsed if elapsed > 0 else 0
            
            logger.info(
                f"Successfully uploaded chunk #{chunk_index:05d} "
                f"({chunk_size_mb:.2f} MB at {upload_speed:.2f} MB/s)"
            )
            
            return chunk_blob_name
        except Exception as e:
            logger.error(f"Failed to upload chunk #{chunk_index:05d}: {str(e)}")
            raise

    def generate_chunk(self, chunk_index: int, start_row: int, start_pk: int, 
                     start_cursor: datetime, used_pks: List[int]) -> Tuple[str, int, int, List[int]]:
        """
        Generate and upload a single chunk.
        
        Args:
            chunk_index: Index of this chunk
            start_row: Row number to start at
            start_pk: Primary key to start at
            start_cursor: Cursor time to start at
            used_pks: List of used primary keys
            
        Returns:
            Tuple of (blob_name, rows_generated, end_pk, updated_used_pks)
        """
        final_blob_name = self.get_final_blob_name()
        
        # Generate data
        data, row_count, end_pk, updated_pks = self.generate_chunk_data(
            chunk_index, start_pk, start_cursor, used_pks
        )
        
        # Upload to GCS
        chunk_blob_name = self.upload_chunk(chunk_index, data, final_blob_name)
        
        # Save checkpoint to allow resuming if needed
        self.save_checkpoint({
            "chunk_index": chunk_index,
            "rows_generated": row_count,
            "end_pk": end_pk,
            "final_blob_name": final_blob_name,
            "chunk_blob_name": chunk_blob_name
        })
        
        return chunk_blob_name, row_count, end_pk, updated_pks

    def process_chunk_batch(self, batch_indices: List[int], 
                          base_pk: int, base_cursor: datetime) -> Tuple[List[str], int, int]:
        """
        Process a batch of chunks using parallel execution.
        
        Args:
            batch_indices: List of chunk indices to process
            base_pk: Base primary key to start from
            base_cursor: Base cursor time to start from
            
        Returns:
            Tuple of (chunk_names, total_rows, end_pk)
        """
        logger.info(f"Processing chunk batch {batch_indices[0]}-{batch_indices[-1]} ({len(batch_indices)} chunks)")
        
        # Estimated rows per chunk for initial spacing
        estimated_bytes_per_row = 200  # Rough estimation
        estimated_rows_per_chunk = self.config.chunk_size_bytes // estimated_bytes_per_row
        
        batch_chunk_names = []
        batch_rows = 0
        end_pk = base_pk
        
        # Function for chunk generation (for parallel execution)
        def generate_chunk_task(chunk_idx):
            """Function to generate a single chunk (for use with ThreadPoolExecutor)"""
            # Each chunk gets its own PK range and cursor range
            chunk_start_row = chunk_idx * estimated_rows_per_chunk
            chunk_start_cursor = self.config.start_date + self.config.cursor_increment * chunk_start_row
            
            # Generate an appropriate starting PK based on chunk index
            # Use a large offset to prevent overlaps between chunks
            chunk_start_pk = base_pk + (chunk_idx - batch_indices[0]) * (estimated_rows_per_chunk * 2)
            
            try:
                # Generate and upload chunk
                return self.generate_chunk(
                    chunk_idx, chunk_start_row, chunk_start_pk, chunk_start_cursor, []
                )
            except Exception as e:
                logger.error(f"Error generating chunk #{chunk_idx:05d}: {str(e)}")
                raise
        
        # Use thread pool for parallel chunk generation
        with ThreadPoolExecutor(max_workers=len(batch_indices)) as executor:
            # Submit all tasks
            futures = {
                executor.submit(generate_chunk_task, idx): idx 
                for idx in batch_indices
            }
            
            # Process results as they complete
            for future in concurrent.futures.as_completed(futures):
                chunk_idx = futures[future]
                try:
                    chunk_name, rows, chunk_end_pk, _ = future.result()
                    batch_chunk_names.append(chunk_name)
                    batch_rows += rows
                    end_pk = max(end_pk, chunk_end_pk)  # Track highest PK
                except Exception as e:
                    logger.error(f"Chunk #{chunk_idx} failed: {str(e)}")
        
        return batch_chunk_names, batch_rows, end_pk

    async def process_chunk_batch_async(self, batch_indices: List[int], 
                                      base_pk: int, base_cursor: datetime) -> Tuple[List[str], int, int]:
        """
        Process a batch of chunks using async execution.
        
        Args:
            batch_indices: List of chunk indices to process
            base_pk: Base primary key to start from
            base_cursor: Base cursor time to start from
            
        Returns:
            Tuple of (chunk_names, total_rows, end_pk)
        """
        # This is for future implementation with asyncio
        # Currently just a wrapper around the threaded version
        return self.process_chunk_batch(batch_indices, base_pk, base_cursor)

    def generate_csv(self, file_index: Optional[int] = None) -> str:
        """
        Generate and upload CSV file to GCS with parallel chunk generation.
        
        Args:
            file_index: Optional index for multi-file generation
            
        Returns:
            Summary string with generation statistics
        """
        final_blob_name = self.get_final_blob_name(file_index)
        
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
        
        # Try to load checkpoint if available
        checkpoint = self.load_checkpoint()
        if checkpoint:
            logger.info(f"Resuming from checkpoint with {checkpoint['chunk_index']} chunks already processed")
            # TODO: Implement resumable generation
        
        # Generate chunks in parallel batches
        chunk_names = []
        total_rows = 0
        current_pk = 1
        
        # Process chunks in batches to avoid overwhelming the system
        chunk_batch_size = self.config.parallel_chunks
        
        for batch_start in range(0, total_chunks, chunk_batch_size):
            batch_end = min(batch_start + chunk_batch_size, total_chunks)
            batch_indices = list(range(batch_start, batch_end))
            
            # Calculate cursor for this batch
            batch_cursor = self.config.start_date + self.config.cursor_increment * (batch_start * estimated_rows_per_chunk)
            
            # Process the batch
            batch_chunk_names, batch_rows, end_pk = self.process_chunk_batch(
                batch_indices, current_pk, batch_cursor
            )
            
            # Add batch results to overall results
            chunk_names.extend(batch_chunk_names)
            total_rows += batch_rows
            current_pk = end_pk
            
            logger.info(f"Completed batch {batch_start}-{batch_end-1}: {batch_rows:,} rows generated")
            
            # Update progress
            progress_pct = (batch_end / total_chunks) * 100
            logger.info(f"Overall progress: {progress_pct:.1f}% ({batch_end}/{total_chunks} chunks)")
            
            # Save global checkpoint
            self.save_checkpoint({
                "chunks_completed": batch_end,
                "total_chunks": total_chunks,
                "total_rows": total_rows,
                "current_pk": current_pk,
                "chunk_names": chunk_names,
                "final_blob_name": final_blob_name
            })
            
            # Clean up between batches
            gc.collect()
        
        # Sort chunk names to ensure proper order
        chunk_names.sort()
        
        # Compose chunks into final file
        self.compose_chunks(final_blob_name, chunk_names)
        
        # Calculate statistics
        duration = time.time() - start_time
        mb_written = (self.config.target_size_bytes) / (1024 * 1024)
        speed_mbps = mb_written / duration if duration > 0 else 0
        
        summary = (
            f"Generated {final_blob_name}: {total_rows:,} rows, "
            f"{mb_written:.2f} MB in {duration:.2f}s ({speed_mbps:.2f} MB/s)"
        )
        logger.info(summary)
        
        # Print cache statistics from data generator
        cache_total = self.data_generator.cache_hits + self.data_generator.cache_misses
        if cache_total > 0:
            cache_hit_rate = (self.data_generator.cache_hits / cache_total) * 100
            logger.info(f"Cache performance: {cache_hit_rate:.1f}% hit rate "
                       f"({self.data_generator.cache_hits:,} hits, {self.data_generator.cache_misses:,} misses)")
        
        return summary

# -------------------------------
# JSON GENERATOR
# -------------------------------
class JSONGenerator(BaseGenerator):
    """Handles JSON file generation and upload to GCS."""
    
    def __init__(self, config: GeneratorConfig):
        super().__init__(config)
        self.data_generator = RandomDataGenerator(config.schema_config, config.cache_size)
    
    def generate_json_object(self, pk: int, cursor_time: datetime) -> Dict[str, Any]:
        """
        Generate a single JSON object.
        
        Args:
            pk: Primary key value
            cursor_time: Current cursor time
            
        Returns:
            Dictionary representing a JSON object
        """
        obj = {}
        
        for field_name, field_config in self.config.schema_config.items():
            # Special handling for id and timestamp fields
            if field_name == "id":
                obj[field_name] = pk
            elif field_name == "timestamp":
                obj[field_name] = cursor_time.isoformat()
            else:
                obj[field_name] = self.data_generator.generate_value(field_config)
                
        return obj
    
    def generate_chunk_data(self, chunk_index: int, start_pk: int, start_cursor: datetime, 
                           used_pks: List[int]) -> Tuple[str, int, int, List[int]]:
        """
        Generate a single chunk of JSON data.
        
        Args:
            chunk_index: Index of this chunk
            start_pk: Primary key to start at
            start_cursor: Cursor time to start at
            used_pks: List of already used primary keys
            
        Returns:
            Tuple of (data, objects_generated, end_pk, updated_used_pks)
        """
        buffer = io.StringIO()
        
        # Start array
        buffer.write('[')
        
        object_count = 0
        current_pk = start_pk
        cursor = start_cursor
        
        # For memory efficiency, limit the cache size
        max_pk_cache = min(1000, 10_000_000 // self.config.target_size_mb)
        local_used_pks = used_pks.copy() if len(used_pks) <= max_pk_cache else []
        
        # Log start of generation
        logger.info(f"Starting generation of chunk #{chunk_index:05d} from PK={start_pk}")
        start_time = time.time()
        last_log_time = start_time
        
        # Keep track of buffer size
        first_object = True
        
        # Fill the chunk
        while buffer.tell() < self.config.chunk_size_bytes:
            # Determine whether to use an existing PK or generate a new one
            if local_used_pks and random.random() < (self.config.duplicate_pct / 100):
                row_pk = random.choice(local_used_pks)
            else:
                row_pk = current_pk
                if len(local_used_pks) < max_pk_cache:
                    local_used_pks.append(row_pk)
                current_pk += 1
            
            # Generate JSON object
            json_obj = self.generate_json_object(row_pk, cursor)
            
            # Add comma if not first object
            if not first_object:
                buffer.write(',')
            else:
                first_object = False
                
            # Write JSON object
            json.dump(json_obj, buffer)
            
            # Update counters
            cursor += self.config.cursor_increment
            object_count += 1
            
            # Log progress based on time rather than object count for large files
            current_time = time.time()
            if (object_count % self.config.log_frequency == 0 or 
                (current_time - last_log_time) > 60):  # Log at least every minute
                
                current_size = buffer.tell()
                size_mb = current_size / (1024 * 1024)
                elapsed = current_time - start_time
                objects_per_sec = object_count / elapsed if elapsed > 0 else 0
                
                logger.info(
                    f"Chunk #{chunk_index:05d}: {object_count:,} objects, "
                    f"{size_mb:.2f} MB ({size_mb/self.config.chunk_size_mb*100:.1f}%), "
                    f"rate: {objects_per_sec:.1f} objects/sec"
                )
                
                # Update log time
                last_log_time = current_time
                
                # Check memory usage occasionally
                self.check_memory_usage()
        
        # End array
        buffer.write(']')
        
        # Get final data
        data = buffer.getvalue()
        
        # Calculate statistics
        chunk_size_mb = len(data.encode("utf-8")) / (1024 * 1024)
        elapsed = time.time() - start_time
        objects_per_sec = object_count / elapsed if elapsed > 0 else 0
        
        logger.info(
            f"Chunk #{chunk_index:05d} generated: {object_count:,} objects, "
            f"{chunk_size_mb:.2f} MB in {elapsed:.2f}s ({objects_per_sec:.1f} objects/sec)"
        )
        
        return data, object_count, current_pk, local_used_pks
        
    def upload_chunk(self, chunk_index: int, data: str, 
                    final_blob_name: str) -> str:
        """
        Upload a chunk to GCS.
        
        Args:
            chunk_index: Index of the chunk
            data: Data to upload
            final_blob_name: Name of the final blob
            
        Returns:
            Name of the uploaded chunk blob
        """
        chunk_blob_name = f"{final_blob_name}.part_{chunk_index:05d}"
        chunk_blob = self.bucket.blob(chunk_blob_name)
        
        # Get data size
        encoded_data = data.encode("utf-8")
        chunk_size_mb = len(encoded_data) / (1024 * 1024)
        
        logger.info(f"Uploading chunk #{chunk_index:05d} ({chunk_size_mb:.2f} MB)")
        
        start_time = time.time()
        
        try:
            # Use robust upload with retry
            self.robust_upload(chunk_blob, data, content_type="application/json")
            
            # Log success with timing information
            elapsed = time.time() - start_time
            upload_speed = chunk_size_mb / elapsed if elapsed > 0 else 0
            
            logger.info(
                f"Successfully uploaded chunk #{chunk_index:05d} "
                f"({chunk_size_mb:.2f} MB at {upload_speed:.2f} MB/s)"
            )
            
            return chunk_blob_name
        except Exception as e:
            logger.error(f"Failed to upload chunk #{chunk_index:05d}: {str(e)}")
            raise
            
    def generate_json(self, file_index: Optional[int] = None) -> str:
        """
        Generate and upload JSON file to GCS with parallel chunk generation.
        
        Args:
            file_index: Optional index for multi-file generation
            
        Returns:
            Summary string with generation statistics
        """
        # Similar to generate_csv but for JSON format
        # Implementation follows the same pattern as CSVGenerator.generate_csv
        # with JSON-specific adjustments
        
        final_blob_name = self.get_final_blob_name(file_index)
        
        # Delete existing blob if it exists
        final_blob = self.bucket.blob(final_blob_name)
        if final_blob.exists():
            logger.info(f"Deleting existing blob: {final_blob_name}")
            final_blob.delete()

        start_time = time.time()
        
        # Calculate total number of chunks needed
        total_chunks = (self.config.target_size_bytes + self.config.chunk_size_bytes - 1) // self.config.chunk_size_bytes
        
        logger.info(f"Preparing to generate {total_chunks} JSON chunks")
        
        # TODO: Implementation would follow similar pattern to CSVGenerator
        # with appropriate JSON handling
        
        raise NotImplementedError("JSON generator implementation pending")
        
        # The rest of the implementation would be similar to CSVGenerator.generate_csv

# -------------------------------
# GENERATOR FACTORY
# -------------------------------
class GeneratorFactory:
    """Factory for creating appropriate generator instances."""
    
    @staticmethod
    def create_generator(config: GeneratorConfig) -> BaseGenerator:
        """
        Create generator based on output format.
        
        Args:
            config: Generator configuration
            
        Returns:
            Appropriate generator instance
        """
        if config.output_format.lower() == "csv":
            return CSVGenerator(config)
        elif config.output_format.lower() == "json":
            return JSONGenerator(config)
        else:
            raise ValueError(f"Unsupported output format: {config.output_format}")

# -------------------------------
# MAIN FUNCTION
# -------------------------------
def main(args: argparse.Namespace) -> None:
    """
    Main entry point for the generator.
    
    Args:
        args: Command line arguments
    """
    # Determine whether to load config from file or use command line args
    if args.config:
        logger.info(f"Loading configuration from {args.config}")
        config = GeneratorConfig.from_file(args.config)
    else:
        # Create config from command line args
        config = GeneratorConfig(
            project_id=args.project,
            bucket_name=args.bucket,
            target_size_mb=args.size,
            output_format=args.format,
            parallel_chunks=args.parallel_chunks,
            compression=args.compression,
            duplicate_pct=args.duplicates,
            chunk_size_mb=args.chunk_size,
            checkpoint_dir=args.checkpoint_dir,
        )
    
    # Set up additional logging if verbose
    if args.verbose:
        setup_logging(logging.DEBUG)
    
    # Create generator
    generator = GeneratorFactory.create_generator(config)
    
    # Generate multiple files if requested
    if args.files > 1:
        logger.info(f"Generating {args.files} files with total size {config.target_size_mb * args.files} MB")
        
        for i in range(args.files):
            logger.info(f"Generating file {i+1}/{args.files}")
            
            # Create a new generator for each file
            if i > 0:
                # Refresh generator to avoid memory buildup
                generator = GeneratorFactory.create_generator(config)
                
            # Generate the file
            if config.output_format.lower() == "csv":
                result = generator.generate_csv(i)
            else:
                result = generator.generate_json(i)
                
            logger.info(f"Completed file {i+1}/{args.files}: {result}")
            
            # Force garbage collection between files
            gc.collect()
    else:
        # Generate a single file
        if config.output_format.lower() == "csv":
            result = generator.generate_csv()
        else:
            result = generator.generate_json()
            
        logger.info(f"Completed generation: {result}")
        
    logger.info("All operations completed successfully")

if __name__ == "__main__":
    # Parse command line arguments with improved options
    parser = argparse.ArgumentParser(
        description='Generate data files of specified size with parallel processing',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Basic configuration
    parser.add_argument('--size', type=int, default=1024, 
                        help='Target size to generate in MB (default: 1024 MB)')
    parser.add_argument('--project', type=str, default="dataline-integration-testing", 
                        help='GCS project ID')
    parser.add_argument('--bucket', type=str, default="no_raw_tables", 
                        help='GCS bucket name')
                        
    # Advanced configuration
    parser.add_argument('--format', type=str, choices=['csv', 'json'], default='csv',
                        help='Output format (csv or json)')
    parser.add_argument('--parallel-chunks', type=int, default=None,
                        help='Number of chunks to generate in parallel (default: CPU count)')
    parser.add_argument('--compression', type=str, choices=['gzip', 'none'], default=None,
                        help='Compression to use (default: none)')
    parser.add_argument('--duplicates', type=int, default=20,
                        help='Percentage of duplicate PKs to generate (0-100)')
    parser.add_argument('--chunk-size', type=int, default=None,
                        help='Size of each chunk in MB (default: auto-calculated)')
    
    # Multi-file generation
    parser.add_argument('--files', type=int, default=1,
                        help='Number of files to generate')
    
    # Configuration and checkpointing
    parser.add_argument('--config', type=str, default=None,
                        help='Path to configuration file (YAML or JSON)')
    parser.add_argument('--checkpoint-dir', type=str, default=None,
                        help='Directory to store checkpoints for resumable operations')
    parser.add_argument('--save-config', type=str, default=None,
                        help='Save current configuration to specified file')
    
    # Debugging and logging
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print configuration and exit without generating data')
    
    args = parser.parse_args()
    
    # Handle dry run
    if args.dry_run:
        if args.config:
            config = GeneratorConfig.from_file(args.config)
        else:
            config = GeneratorConfig(
                project_id=args.project,
                bucket_name=args.bucket,
                target_size_mb=args.size,
                output_format=args.format,
                parallel_chunks=args.parallel_chunks,
                compression=args.compression,
                duplicate_pct=args.duplicates,
                chunk_size_mb=args.chunk_size,
                checkpoint_dir=args.checkpoint_dir,
            )
        
        print("Dry run - configuration:")
        for key, value in config.__dict__.items():
            print(f"  {key}: {value}")
        sys.exit(0)
        
    # Save configuration if requested
    if args.save_config and not args.config:
        config = GeneratorConfig(
            project_id=args.project,
            bucket_name=args.bucket,
            target_size_mb=args.size,
            output_format=args.format,
            parallel_chunks=args.parallel_chunks,
            compression=args.compression,
            duplicate_pct=args.duplicates,
            chunk_size_mb=args.chunk_size,
            checkpoint_dir=args.checkpoint_dir,
        )
        
        config.save_to_file(args.save_config)
        logger.info(f"Configuration saved to {args.save_config}")
        
        if args.dry_run:
            sys.exit(0)
    
    # Run the generator
    try:
        main(args)
    except Exception as e:
        logger.error(f"Error during execution: {str(e)}", exc_info=True)
        sys.exit(1)