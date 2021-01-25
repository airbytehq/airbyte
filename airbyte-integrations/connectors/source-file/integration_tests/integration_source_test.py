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
from source_file.client import Client
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.ssh_exception import SSHException

HERE = Path(__file__).parent.absolute()


@pytest.fixture(scope="session")
def docker_compose_file():
    return HERE / "docker-compose.yml"


def is_ssh_ready(ip, port):
    try:
        with SSHClient() as ssh:
            ssh.set_missing_host_key_policy(AutoAddPolicy)
            ssh.connect(ip, port=port, username="user1", password="pass1", )
        return True
    except (SSHException, socket.error):
        return False


@pytest.fixture(scope="session")
def ssh_service(docker_ip, docker_services):
    """Ensure that SSH service is up and responsive."""

    # `port_for` takes a container port and returns the corresponding host port
    port = docker_services.port_for("ssh", 22)
    docker_services.wait_until_responsive(
        timeout=30.0, pause=0.1, check=lambda: is_ssh_ready(docker_ip, port)
    )
    return docker_ip


@pytest.fixture
def provider_config(ssh_service):
    def lookup(name):
        providers = {
            "ssh": dict(storage="SSH", host=ssh_service, user="user1", password="pass1", port=2222),
            "scp": dict(storage="SCP", host=ssh_service, user="user1", password="pass1", port=2222),
            "sftp": dict(storage="SFTP", host=ssh_service, user="user1", password="pass1", port=100),
            "hdfs": None
        }
        return providers[name]

    return lookup


"""
1. incorrect configuration, missing values or syntax
2. unknown url (dns)
3. don't have permissions or password/user don't match
4. file doesn't exist                                   // <- all before and this one should be covered in check as well
5. binary/text file
6. multiple binary formats pandas recognize and not

7. all above with read, check and discover
"""


@pytest.mark.parametrize(
    "provider_name,file_path", [
        ("ssh", "files/test.csv"),
        ("scp", "files/test.csv"),
        ("sftp", "files/test.csv"),
        ("ssh", "files/test.csv.gz"),
        ("sftp", "files/test.csv.gz"),
        # ("ssh", "files/test.pkl"),
        # ("sftp", "files/test.pkl"),
        # ("ssh", "files/empty.csv"),
        # ("sftp", "files/test.pkl"),
    ]
)
def test__read_from_ssh_providers(provider_config, provider_name, file_path):
    client = Client(dataset_name="output", format="csv", url=file_path,
                    provider=provider_config(provider_name))
    result = next(client.read())
    assert result == {'header1': 'text', 'header2': 1, 'header3': 0.2}


class TestSourceFile:
    service_account_file: str = HERE.parent / "secrets/gcs.json"
    aws_credentials: str = HERE.parent / "secrets/aws.json"
    cloud_bucket_name: str = "airbytetestbucket"

    @pytest.fixture(scope="class")
    def download_gcs_public_data(self):
        print("\nDownload public dataset from gcs to local /tmp")
        df = pandas.read_csv("https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv")
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        df.to_csv(tmp_file.name, index=False)
        yield tmp_file.name
        os.remove(tmp_file.name)
        print(f"\nLocal File {tmp_file.name} is now deleted")

    @pytest.fixture(scope="class")
    def create_gcs_private_data(self, download_gcs_public_data):
        storage_client = storage.Client.from_service_account_json(self.service_account_file)
        bucket_name = create_unique_gcs_bucket(storage_client, self.cloud_bucket_name)
        print(f"\nUpload dataset to private gcs bucket {bucket_name}")
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob("myfile.csv")
        blob.upload_from_filename(download_gcs_public_data)
        yield f"{bucket_name}/myfile.csv"
        bucket.delete(force=True)
        print(f"\nGCS Bucket {bucket_name} is now deleted")

    @pytest.fixture(scope="class")
    def create_aws_private_data(self, download_gcs_public_data):
        with open(self.aws_credentials) as json_file:
            aws_config = json.load(json_file)
        region = "eu-west-3"
        location = {"LocationConstraint": region}
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=aws_config["aws_access_key_id"],
            aws_secret_access_key=aws_config["aws_secret_access_key"],
            region_name=region,
        )
        bucket_name = self.cloud_bucket_name
        print(f"\nUpload dataset to private aws bucket {bucket_name}")
        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except ClientError:
            s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
        s3_client.upload_file(download_gcs_public_data, bucket_name, "myfile.csv")
        yield f"{bucket_name}/myfile.csv"
        s3 = boto3.resource(
            "s3", aws_access_key_id=aws_config["aws_access_key_id"], aws_secret_access_key=aws_config["aws_secret_access_key"]
        )
        bucket = s3.Bucket(bucket_name)
        bucket.objects.all().delete()
        print(f"\nS3 Bucket {bucket_name} is now deleted")

    @pytest.mark.parametrize(
        "storage_provider, url, columns_nb, config_index",
        [
            # epidemiology csv
            ("HTTPS", "https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv", 10, 0),
            ("HTTPS", "storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv", 10, 0),
            ("local", "injected by tests", 10, 0),
            # landsat compressed csv
            ("GCS", "gs://gcp-public-data-landsat/index.csv.gz", 18, 1),
            ("GCS", "gs://gcp-public-data-landsat/index.csv.gz", 18, 0),
            # GDELT csv
            ("S3", "s3://gdelt-open-data/events/20190914.export.csv", 58, 2),
            ("S3", "s3://gdelt-open-data/events/20190914.export.csv", 58, 2),
        ],
    )
    def test_public_and_local_data(self, download_gcs_public_data, storage_provider, url, columns_nb, config_index):
        config = get_config(config_index)
        config["provider"]["storage"] = storage_provider
        if storage_provider != "local":
            config["url"] = url
        else:
            # inject temp file path that was downloaded by the test as URL
            config["url"] = download_gcs_public_data
        run_load_dataframes(config, expected_columns=columns_nb)

    def test_private_gcs_load(self, create_gcs_private_data):
        config = get_config(0)
        config["provider"]["storage"] = "GCS"
        config["url"] = create_gcs_private_data
        with open(self.service_account_file) as json_file:
            config["provider"]["service_account_json"] = json.dumps(json.load(json_file))
        run_load_dataframes(config)

    def test_private_aws_load(self, create_aws_private_data):
        config = get_config(0)
        config["provider"]["storage"] = "S3"
        config["url"] = create_aws_private_data
        with open(self.aws_credentials) as json_file:
            aws_config = json.load(json_file)
        config["provider"]["aws_access_key_id"] = aws_config["aws_access_key_id"]
        config["provider"]["aws_secret_access_key"] = aws_config["aws_secret_access_key"]
        run_load_dataframes(config)

    @pytest.mark.parametrize(
        "storage_provider, url, user, password, host, columns_nb, rows_nb, config_index",
        [
            ("SFTP", "/pub/example/readme.txt", "demo", "password", "test.rebex.net", 1, 6, 3),
            ("SSH", "readme.txt", "demo", "password", "test.rebex.net", 1, 6, 3),
        ],
    )
    def test_private_provider(self, storage_provider, url, user, password, host, columns_nb, rows_nb, config_index):
        config = get_config(config_index)
        config["provider"]["storage"] = storage_provider
        config["url"] = url
        config["provider"]["user"] = user
        config["provider"]["password"] = password
        config["provider"]["host"] = host
        run_load_dataframes(config, columns_nb, rows_nb)


def run_load_dataframes(config, expected_columns=10, expected_rows=42):
    client = Client(**config)
    rows = list(client.read())
    assert len(rows[0]) == expected_columns, "DataFrame should have 10 columns"
    assert len(rows) == expected_rows, "DataFrame should have 42 rows of data"
    return rows


def get_config(index: int) -> Mapping[str, str]:
    default_config = {
        "format": "csv",
        "provider": {},
        "dataset_name": "output",
    }

    configs = [
        {"reader_options": '{"sep": ",", "nrows": 42}'},
        {"reader_options": '{"sep": ",", "nrows": 42}'},
        {"reader_options": '{"sep": "\\t", "nrows": 42, "header": null}'},
        {"reader_options": '{"sep": "\\r\\n", "names": ["text"], "header": null, "engine": "python"}'},
    ]
    return {**default_config, **configs[index]}


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
