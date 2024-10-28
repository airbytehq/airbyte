#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from pathlib import Path

import pytest
from source_file.client import Client

HERE = Path(__file__).parent.absolute()


def check_read(config, expected_columns=10, expected_rows=42):
    client = Client(**config)
    rows = list(client.read())
    assert len(rows) == expected_rows
    assert len(rows[0]) == expected_columns


@pytest.mark.parametrize(
    "provider_name,file_path,file_format",
    [
        ("ssh", "files/test.csv", "csv"),
        ("scp", "files/test.csv", "csv"),
        ("sftp", "files/test.csv", "csv"),
        ("ssh", "files/test.csv.zip", "csv"),
        ("ssh", "files/test.csv.gz", "csv"),  # text in binary
        ("ssh", "files/test.pkl", "pickle"),  # binary
        ("sftp", "files/test.pkl.gz", "pickle"),  # binary in binary
    ],
)
def test__read_from_private_ssh(provider_config, provider_name, file_path, file_format):
    client = Client(dataset_name="output", format=file_format, url=file_path, provider=provider_config(provider_name))
    result = next(client.read())
    assert result == {"header1": "text", "header2": 1, "header3": 0.2, "header4": True}


@pytest.mark.parametrize(
    "provider_name,file_path,file_format",
    [
        ("ssh", "files/file_does_not_exist.csv", "csv"),
        ("gcs", "gs://gcp-public-data-landsat/file_does_not_exist.csv", "csv"),
    ],
)
def test__read_file_not_found(provider_config, provider_name, file_path, file_format):
    client = Client(dataset_name="output", format=file_format, url=file_path, provider=provider_config(provider_name))
    with pytest.raises(FileNotFoundError):
        next(client.read())


@pytest.mark.parametrize(
    "provider_name, file_path, file_format",
    [
        ("ssh", "files/test.csv", "csv"),
        ("ssh", "files/test.pkl", "pickle"),
        ("sftp", "files/test.pkl.gz", "pickle"),
    ],
)
def test__streams_from_ssh_providers(provider_config, provider_name, file_path, file_format):
    client = Client(dataset_name="output", format=file_format, url=file_path, provider=provider_config(provider_name))
    streams = list(client.streams())
    assert len(streams) == 1
    assert streams[0].json_schema["properties"] == {
        "header1": {"type": ["string", "null"]},
        "header2": {"type": ["number", "null"]},
        "header3": {"type": ["number", "null"]},
        "header4": {"type": ["boolean", "null"]},
    }


@pytest.mark.parametrize(
    "storage_provider, url, columns_nb, separator, has_header",
    [
        # epidemiology csv
        ("HTTPS", "https://storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv", 10, ",", True),
        ("HTTPS", "storage.googleapis.com/covid19-open-data/v2/latest/epidemiology.csv", 10, ",", True),
        ("local", "injected by tests", 10, ",", True),
        # landsat compressed csv
        ("GCS", "gs://gcp-public-data-landsat/index.csv.gz", 18, ",", True),
        ("GCS", "gs://gcp-public-data-landsat/index.csv.gz", 18, ",", True),
        # GDELT csv
        ("S3", "s3://gdelt-open-data/events/20190914.export.csv", 58, "\\t", False),
        ("S3", "s3://gdelt-open-data/events/20190914.export.csv", 58, "\\t", False),
    ],
)
def test__read_from_public_provider(download_gcs_public_data, storage_provider, url, columns_nb, separator, has_header):
    # inject temp file path that was downloaded by the test as URL
    url = download_gcs_public_data if storage_provider == "local" else url
    config = {
        "format": "csv",
        "dataset_name": "output",
        "reader_options": {"sep": separator, "nrows": 42},
        "provider": {"storage": storage_provider, "user_agent": False},
        "url": url,
    }

    check_read(config, expected_columns=columns_nb)


def test__read_from_private_gcs(google_cloud_service_credentials, private_google_cloud_file):
    config = {
        "dataset_name": "output",
        "format": "csv",
        "url": private_google_cloud_file,
        "reader_options": {"sep": ",", "nrows": 42},
        "provider": {
            "storage": "GCS",
            "service_account_json": json.dumps(google_cloud_service_credentials),
        },
    }
    check_read(config)


def test__read_from_private_aws(aws_credentials, private_aws_file):
    config = {
        "dataset_name": "output",
        "format": "csv",
        "url": private_aws_file,
        "reader_options": {"sep": ",", "nrows": 42},
        "provider": {
            "storage": "S3",
            "aws_access_key_id": aws_credentials["aws_access_key_id"],
            "aws_secret_access_key": aws_credentials["aws_secret_access_key"],
        },
    }
    check_read(config)


def test__read_from_public_azblob(azblob_credentials, public_azblob_file):
    config = {
        "dataset_name": "output",
        "format": "csv",
        "url": public_azblob_file,
        "reader_options": {"sep": ",", "nrows": 42},
        "provider": {"storage": "AzBlob", "storage_account": azblob_credentials["storage_account"]},
    }
    check_read(config)


def test__read_from_private_azblob_shared_key(azblob_credentials, private_azblob_file):
    config = {
        "dataset_name": "output",
        "format": "csv",
        "url": private_azblob_file,
        "reader_options": {"sep": ",", "nrows": 42},
        "provider": {
            "storage": "AzBlob",
            "storage_account": azblob_credentials["storage_account"],
            "shared_key": azblob_credentials["shared_key"],
        },
    }
    check_read(config)


def test__read_from_private_azblob_sas_token(azblob_credentials, private_azblob_file):
    config = {
        "dataset_name": "output",
        "format": "csv",
        "url": private_azblob_file,
        "reader_options": {"sep": ",", "nrows": 42},
        "provider": {
            "storage": "AzBlob",
            "storage_account": azblob_credentials["storage_account"],
            "sas_token": azblob_credentials["sas_token"],
        },
    }
    check_read(config)
