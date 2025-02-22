from google.cloud import storage
import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def compose_files(
    project_id: str,
    bucket_name: str,
    source_files: list[str],
    destination_file: str
) -> None:
    """
    Compose multiple GCS files into one without downloading.
    All composition happens server-side on GCS.
    """
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    
    # Get source blob references
    source_blobs = [bucket.blob(f) for f in source_files]
    
    # Verify all source files exist and get their sizes
    for blob in source_blobs:
        if not blob.exists():
            raise ValueError(f"Source file {blob.name} does not exist")
        blob.reload()  # Load metadata including size
        logger.info(f"Found source file: {blob.name} ({blob.size / 1024 / 1024 / 1024:.2f} GB)")
    
    # Create destination blob
    destination_blob = bucket.blob(destination_file)
    
    # Perform server-side composition
    logger.info(f"Starting composition of {len(source_blobs)} files into {destination_file}")
    destination_blob.compose(source_blobs)
    
    # Verify final size
    destination_blob.reload()  # Refresh metadata
    final_size_gb = destination_blob.size / 1024 / 1024 / 1024
    logger.info(f"Successfully created {destination_file} ({final_size_gb:.2f} GB)")

if __name__ == "__main__":
    PROJECT_ID = "dataline-integration-testing"
    BUCKET_NAME = "no_raw_tables"
    
    # Your source files
    SOURCE_FILES = [
        f"data_export_20000MB_20250220_084437_00{i}.csv"
        for i in range(5)
    ]
    
    # Destination file
    DESTINATION_FILE = "data_export_100GB_final.csv"
    
    compose_files(
        project_id=PROJECT_ID,
        bucket_name=BUCKET_NAME,
        source_files=SOURCE_FILES,
        destination_file=DESTINATION_FILE
    )