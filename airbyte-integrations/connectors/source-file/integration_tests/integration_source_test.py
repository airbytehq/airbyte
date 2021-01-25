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
from pathlib import Path
from typing import Mapping

import pytest
from source_file.client import Client

HERE = Path(__file__).parent.absolute()


def check_read(config, expected_columns=10, expected_rows=42):
    client = Client(**config)
    rows = list(client.read())
    assert len(rows) == expected_rows
    assert len(rows[0]) == expected_columns


@pytest.mark.parametrize(
    "provider_name,file_path,file_format", [
        ("ssh", "files/test.csv", "csv"),
        ("scp", "files/test.csv", "csv"),
        ("sftp", "files/test.csv", "csv"),
        ("ssh", "files/test.csv.gz", "csv"),  # text in binary
        ("ssh", "files/test.pkl", "pickle"),  # binary
        ("sftp", "files/test.pkl.gz", "pickle"),  # binary in binary
    ]
)
def test__read_from_private_ssh(provider_config, provider_name, file_path, file_format):
    client = Client(dataset_name="output", format=file_format, url=file_path,
                    provider=provider_config(provider_name))
    result = next(client.read())
    assert result == {'header1': 'text', 'header2': 1, 'header3': 0.2}


@pytest.mark.parametrize(
    "provider_name,file_path,file_format", [
        ("ssh", "files/file_does_not_exist.csv", "csv"),
        ("gcs", "gs://gcp-public-data-landsat/file_does_not_exist.csv", "csv"),
    ]
)
def test__read_file_not_found(provider_config, provider_name, file_path, file_format):
    client = Client(dataset_name="output", format=file_format, url=file_path,
                    provider=provider_config(provider_name))
    with pytest.raises(FileNotFoundError):
        next(client.read())


@pytest.mark.parametrize(
    "provider_name, file_path, file_format", [
        ("ssh", "files/test.csv", "csv"),
        ("ssh", "files/test.pkl", "pickle"),
        ("sftp", "files/test.pkl.gz", "pickle"),
    ]
)
def test__streams_from_ssh_providers(provider_config, provider_name, file_path, file_format):
    client = Client(dataset_name="output", format=file_format, url=file_path,
                    provider=provider_config(provider_name))
    streams = list(client.streams)
    assert len(streams) == 1
    assert streams[0].json_schema['properties'] == {'header1': {'type': 'string'}, 'header2': {'type': 'number'},
                                                    'header3': {'type': 'number'}}


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
def test__read_from_public_provider(download_gcs_public_data, storage_provider, url, columns_nb, config_index):
    config = get_config(config_index)
    config["provider"]["storage"] = storage_provider
    if storage_provider != "local":
        config["url"] = url
    else:
        # inject temp file path that was downloaded by the test as URL
        config["url"] = download_gcs_public_data
    check_read(config, expected_columns=columns_nb)


def test__read_from_private_gcs(google_cloud_service_credentials, private_google_cloud_file):
    config = get_config(0)
    config["provider"]["storage"] = "GCS"
    config["provider"]["service_account_json"] = json.dumps(google_cloud_service_credentials)
    config["url"] = private_google_cloud_file

    check_read(config)


def test__read_from_private_aws(aws_credentials, private_aws_file):
    config = get_config(0)
    config["provider"]["storage"] = "S3"
    config["provider"]["aws_access_key_id"] = aws_credentials["aws_access_key_id"]
    config["provider"]["aws_secret_access_key"] = aws_credentials["aws_secret_access_key"]
    config["url"] = private_aws_file
    check_read(config)


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
