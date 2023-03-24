from google.cloud import storage


SPEC_CACHE_BUCKET_NAME = "io-airbyte-cloud-spec-cache"
CACHE_FOLDER = "specs"

def get_spec_cache_path(docker_repository, docker_image_tag):
    return f"{CACHE_FOLDER}/{docker_repository}/{docker_image_tag}/spec.json"

def is_spec_cached(docker_repository: str, docker_image_tag: str) -> bool:
    spec_path = get_spec_cache_path(docker_repository, docker_image_tag)

    client = storage.Client.create_anonymous_client()
    bucket = client.bucket(SPEC_CACHE_BUCKET_NAME)
    blob = bucket.blob(spec_path)

    return blob.exists()

