"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import os
import socket
import tempfile
import uuid
from pathlib import Path
from typing import Mapping

import boto3
import pandas
import pytest
from botocore.errorfactory import ClientError
from google.api_core.exceptions import Conflict
from google.cloud import storage
from paramiko.client import AutoAddPolicy, SSHClient
from paramiko.ssh_exception import SSHException

HERE = Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def docker_compose_file() -> Path:
    return HERE / "docker-compose.yml"


@pytest.fixture(scope="session")
def google_cloud_service_file() -> Path:
    return HERE.parent / "secrets/gcs.json"


@pytest.fixture(scope="session")
def google_cloud_service_credentials(google_cloud_service_file) -> Mapping:
    with open(google_cloud_service_file) as json_file:
        return json.load(json_file)


@pytest.fixture(scope="session")
def aws_credentials() -> Mapping:
    filename = HERE.parent / "secrets/aws.json"
    with open(filename) as json_file:
        return json.load(json_file)


@pytest.fixture(scope="session")
def cloud_bucket_name():
    return "airbytetestbucket"


def is_ssh_ready(ip, port):
    try:
        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy)
            ssh.connect(
                ip,
                port=port,
                username="user1",
                password="pass1",
            )
        return True
    except (SSHException, socket.error):
        return False


@pytest.fixture(scope="session")
def ssh_service(docker_ip, docker_services):
    """Ensure that SSH service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("ssh", 22)
    docker_services.wait_until_responsive(timeout=30.0, pause=0.1, check=lambda: is_ssh_ready(docker_ip, port))
    return docker_ip


@pytest.fixture
def provider_config(ssh_service):
    def lookup(name):
        providers = {
            "ssh": dict(storage="SSH", host=ssh_service, user="user1", password="pass1", port=2222),
            "scp": dict(storage="SCP", host=ssh_service, user="user1", password="pass1", port=2222),
            "sftp": dict(storage="SFTP", host=ssh_service, user="user1", password="pass1", port=100),
            "gcs": dict(storage="GCS"),
            "s3": dict(storage="S3"),
        }
        return providers[name]

    return lookup


def create_unique_gcs_bucket(storage_client, name: str) -> str:
    """
    Make a unique bucket to which we'll upload the file.
    (GCS buckets are part of a single global namespace.)
    """
    for i in range(0, 5):
        bucket_name = f"{name}-{uuid.uuid1()}"
        try:
            bucket = storage_client.bucket(bucket_name)
            bucket.storage_class = "STANDARD"
            # fixed locations are cheaper...
            storage_client.create_bucket(bucket, location="us-east1")
            print(f"\nNew GCS bucket created {bucket_name}")
            return bucket_name
        except Conflict:
            print(f"\nError: {bucket_name} already exists!")


@pytest.fixture(scope="session")
def download_gcs_public_data():
    print("\nDownload public dataset from gcs to local /tmp")
    df = pandas.read_csv("https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv")
    tmp_file = tempfile.NamedTemporaryFile(delete=False)
    df.to_csv(tmp_file.name, index=False)

    yield tmp_file.name

    os.remove(tmp_file.name)
    print(f"\nLocal File {tmp_file.name} is now deleted")


@pytest.fixture(scope="session")
def private_google_cloud_file(google_cloud_service_file, cloud_bucket_name, download_gcs_public_data):
    storage_client = storage.Client.from_service_account_json(str(google_cloud_service_file))
    bucket_name = create_unique_gcs_bucket(storage_client, cloud_bucket_name)
    print(f"\nUpload dataset to private gcs bucket {bucket_name}")
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("myfile.csv")
    blob.upload_from_filename(download_gcs_public_data)

    yield f"{bucket_name}/myfile.csv"

    bucket.delete(force=True)
    print(f"\nGCS Bucket {bucket_name} is now deleted")


@pytest.fixture(scope="session")
def private_aws_file(aws_credentials, cloud_bucket_name, download_gcs_public_data):
    region = "eu-west-3"
    location = {"LocationConstraint": region}
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_credentials["aws_access_key_id"],
        aws_secret_access_key=aws_credentials["aws_secret_access_key"],
        region_name=region,
    )
    bucket_name = cloud_bucket_name
    print(f"\nUpload dataset to private aws bucket {bucket_name}")
    try:
        s3_client.head_bucket(Bucket=bucket_name)
    except ClientError:
        s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
    s3_client.upload_file(download_gcs_public_data, bucket_name, "myfile.csv")

    yield f"{bucket_name}/myfile.csv"

    s3 = boto3.resource(
        "s3", aws_access_key_id=aws_credentials["aws_access_key_id"], aws_secret_access_key=aws_credentials["aws_secret_access_key"]
    )
    bucket = s3.Bucket(bucket_name)
    bucket.objects.all().delete()
    print(f"\nS3 Bucket {bucket_name} is now deleted")
