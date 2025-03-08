from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError, GatewayTimeout
import logging
import re
import time
import argparse
from typing import List, Dict, Tuple

logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def retry_with_backoff(func, max_retries=5, initial_backoff=1, max_backoff=60):
    """Execute a function with retry logic and exponential backoff."""
    retries = 0
    backoff = initial_backoff
    
    while True:
        try:
            return func()
        except (GoogleAPIError, GatewayTimeout) as e:
            retries += 1
            if retries > max_retries:
                logger.error(f"Maximum retries ({max_retries}) exceeded. Last error: {str(e)}")
                raise
            
            # Calculate backoff with exponential increase and some randomness
            sleep_time = min(backoff * (1.5 ** (retries - 1)), max_backoff)
            logger.warning(f"Operation failed with error: {str(e)}. Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

def list_existing_temp_files(
    storage_client,
    bucket_name: str,
    temp_prefix: str
) -> Dict[int, storage.Blob]:
    """
    List all existing temporary files from a previous run.
    
    Returns:
        Dictionary mapping batch index to blob object
    """
    bucket = storage_client.bucket(bucket_name)
    temp_pattern = re.compile(rf"^{re.escape(temp_prefix)}\.temp\.(\d+)$")
    
    temp_blobs = {}
    for blob in bucket.list_blobs(prefix=temp_prefix):
        match = temp_pattern.match(blob.name)
        if match:
            batch_idx = int(match.group(1))
            temp_blobs[batch_idx] = blob
    
    if temp_blobs:
        logger.info(f"Found {len(temp_blobs)} existing temporary files")
        logger.info(f"Temporary files indexes: {sorted(temp_blobs.keys())}")
    else:
        logger.info("No existing temporary files found")
        
    return temp_blobs

def list_all_part_files(
    storage_client,
    bucket_name: str,
    file_pattern: str
) -> Dict[int, storage.Blob]:
    """
    List all part files in the bucket matching the pattern.
    
    Returns:
        Dictionary of part number to blob
    """
    bucket = storage_client.bucket(bucket_name)
    
    # Get all blobs in the bucket
    all_blobs = list(bucket.list_blobs())
    logger.info(f"Found {len(all_blobs)} total files in the bucket")
    
    # Extract part files and their numbers
    part_blobs = {}
    part_pattern = re.compile(r'.*\.part_(\d{5})$')
    
    for blob in all_blobs:
        if file_pattern in blob.name:
            match = part_pattern.match(blob.name)
            if match:
                part_num = int(match.group(1))
                part_blobs[part_num] = blob
                
    logger.info(f"Found {len(part_blobs)} files matching the pattern {file_pattern}")
    
    # List some examples for verification
    examples = sorted(list(part_blobs.keys()))[:5]
    if examples:
        logger.info(f"Example part numbers found: {examples}")
        logger.info(f"Example filenames: {[part_blobs[part].name for part in examples]}")
    
    return part_blobs

def compose_with_retry(bucket, sources, destination_name):
    """Compose files with retry logic for timeout errors."""
    destination_blob = bucket.blob(destination_name)
    
    def _compose():
        destination_blob.compose(sources)
        return destination_blob
    
    return retry_with_backoff(_compose)

def compose_files_with_resume(
    project_id: str,
    bucket_name: str,
    file_pattern: str,
    start_part: int,
    end_part: int,
    destination_file: str,
    force_restart: bool = False
) -> None:
    """
    Compose multiple GCS files with resume capability.
    All composition happens server-side on GCS.
    
    Args:
        project_id: GCP project ID
        bucket_name: GCS bucket name
        file_pattern: Pattern to identify the files (e.g., "data_export_1048576MB_")
        start_part: Starting part number (inclusive)
        end_part: Ending part number (inclusive)
        destination_file: Final destination file name
        force_restart: Whether to force a restart, ignoring existing temp files
    """
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    
    # Check for existing temp files from previous run
    if not force_restart:
        existing_temp_blobs = list_existing_temp_files(storage_client, bucket_name, destination_file)
    else:
        existing_temp_blobs = {}
        logger.info("Forced restart: ignoring any existing temporary files")
    
    # GCS has a limit of 32 files per composition operation
    MAX_COMPOSE_SIZE = 32
    
    # If we have temporary blobs, we'll use them for the next level
    if existing_temp_blobs:
        logger.info("Resuming from existing temporary files")
        # Skip the first level composition
        temp_blobs = [blob for _, blob in sorted(existing_temp_blobs.items())]
    else:
        # Find all part files for first-level composition
        part_blobs_dict = list_all_part_files(storage_client, bucket_name, file_pattern)
        
        # Filter for the range we want
        source_blobs = []
        missing_parts = []
        
        for part_num in range(start_part, end_part + 1):
            if part_num in part_blobs_dict:
                source_blobs.append(part_blobs_dict[part_num])
                if part_num % 100 == 0:  # Log only every 100th file
                    logger.info(f"Including part {part_num:05d}: {part_blobs_dict[part_num].name}")
            else:
                missing_parts.append(part_num)
                logger.warning(f"Missing part {part_num:05d}")
        
        if missing_parts:
            logger.error(f"Missing {len(missing_parts)} parts out of {end_part - start_part + 1}")
            if len(missing_parts) <= 10:
                logger.error(f"Missing parts: {[f'{p:05d}' for p in missing_parts]}")
            else:
                logger.error(f"First 10 missing parts: {[f'{p:05d}' for p in missing_parts[:10]]}...")
            
            if len(missing_parts) > 0.1 * (end_part - start_part + 1):  # If more than 10% missing
                raise ValueError("Too many missing parts, aborting composition")
        
        if not source_blobs:
            raise ValueError("No matching files found!")
        
        logger.info(f"Found {len(source_blobs)} files out of {end_part - start_part + 1} expected")
        
        # We'll use the MAX_COMPOSE_SIZE defined above
        
        if len(source_blobs) <= MAX_COMPOSE_SIZE:
            # Direct composition if within limits
            logger.info(f"Composing {len(source_blobs)} files directly into {destination_file}")
            compose_with_retry(bucket, source_blobs, destination_file)
            logger.info(f"Successfully created {destination_file}")
            return
        else:
            # First level composition
            logger.info(f"Using multi-level composition for {len(source_blobs)} files")
            temp_blobs = []
            
            for i in range(0, len(source_blobs), MAX_COMPOSE_SIZE):
                # Skip if this temp file already exists
                temp_name = f"{destination_file}.temp.{i//MAX_COMPOSE_SIZE}"
                
                if i//MAX_COMPOSE_SIZE in existing_temp_blobs:
                    logger.info(f"Skipping existing temporary file: {temp_name}")
                    temp_blobs.append(existing_temp_blobs[i//MAX_COMPOSE_SIZE])
                    continue
                
                batch = source_blobs[i:i + MAX_COMPOSE_SIZE]
                logger.info(f"Composing batch {i//MAX_COMPOSE_SIZE + 1}/{(len(source_blobs)-1)//MAX_COMPOSE_SIZE + 1}: {len(batch)} files into {temp_name}")
                
                temp_blob = compose_with_retry(bucket, batch, temp_name)
                temp_blobs.append(temp_blob)
    
    # Continue composing until we have just one file
    level = 1
    while len(temp_blobs) > 1:
        level += 1
        new_temp_blobs = []
        
        for i in range(0, len(temp_blobs), MAX_COMPOSE_SIZE):
            batch = temp_blobs[i:i + MAX_COMPOSE_SIZE]
            temp_name = f"{destination_file}.temp.level{level}.{i//MAX_COMPOSE_SIZE}"
            
            logger.info(f"Composing level {level} batch {i//MAX_COMPOSE_SIZE + 1}/{(len(temp_blobs)-1)//MAX_COMPOSE_SIZE + 1}: {len(batch)} files into {temp_name}")
            temp_blob = compose_with_retry(bucket, batch, temp_name)
            new_temp_blobs.append(temp_blob)
        
        # Delete previous level temp files
        for blob in temp_blobs:
            try:
                blob.delete()
                logger.info(f"Deleted temp file: {blob.name}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file {blob.name}: {str(e)}")
        
        temp_blobs = new_temp_blobs
    
    # Rename the final temp blob to the destination name
    if len(temp_blobs) == 1:
        final_temp_blob = temp_blobs[0]
        
        # Copy the content
        logger.info(f"Creating final file: {destination_file}")
        
        def _copy_blob():
            bucket.copy_blob(final_temp_blob, bucket, destination_file)
        
        retry_with_backoff(_copy_blob)
        
        # Delete the last temp file
        try:
            final_temp_blob.delete()
            logger.info(f"Deleted final temp file: {final_temp_blob.name}")
        except Exception as e:
            logger.warning(f"Failed to delete final temp file {final_temp_blob.name}: {str(e)}")
    else:
        raise ValueError("Composition failed: no final temp file created")
    
    # Verify the final composed file
    destination_blob = bucket.blob(destination_file)
    destination_blob.reload()
    final_size_gb = destination_blob.size / (1024 ** 3)
    logger.info(f"Successfully created {destination_file} ({final_size_gb:.2f} GB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compose GCS files with resume capability")
    parser.add_argument("--project", default="dataline-integration-testing", help="GCP project ID")
    parser.add_argument("--bucket", default="no_raw_tables", help="GCS bucket name")
    parser.add_argument("--pattern", default="data_export_1048576MB_", help="File pattern to match")
    parser.add_argument("--start", type=int, default=0, help="Start part number (inclusive)")
    parser.add_argument("--end", type=int, default=780, help="End part number (inclusive)")
    parser.add_argument("--output", default="data_export_780GB_final.csv", help="Output filename")
    parser.add_argument("--force-restart", action="store_true", help="Force restart, ignoring existing temp files")
    
    args = parser.parse_args()
    
    compose_files_with_resume(
        project_id=args.project,
        bucket_name=args.bucket,
        file_pattern=args.pattern,
        start_part=args.start,
        end_part=args.end,
        destination_file=args.output,
        force_restart=args.force_restart
    )