#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import patch

import pytest
from pandas import read_csv, read_excel
from source_file.client import Client, ConfigurationError, URLFile
from urllib3.exceptions import ProtocolError


@pytest.fixture
def wrong_format_client():
    return Client(
        dataset_name="test_dataset",
        url="scp://test_dataset",
        provider={"provider": {"storage": "HTTPS", "reader_impl": "gcsfs", "user_agent": False}},
        format="wrong",
    )


@pytest.fixture
def csv_format_client():
    return Client(
        dataset_name="test_dataset",
        url="scp://test_dataset",
        provider={"provider": {"storage": "HTTPS", "reader_impl": "gcsfs", "user_agent": False}},
        format="csv",
    )


@pytest.mark.parametrize(
    "storage, expected_scheme",
    [
        ("GCS", "gs://"),
        ("S3", "s3://"),
        ("AZBLOB", "azure://"),
        ("HTTPS", "https://"),
        ("SSH", "scp://"),
        ("SCP", "scp://"),
        ("SFTP", "sftp://"),
        ("WEBHDFS", "webhdfs://"),
        ("LOCAL", "file://"),
    ],
)
def test_storage_scheme(storage, expected_scheme):
    urlfile = URLFile(provider={"storage": storage}, url="http://localhost")
    assert urlfile.storage_scheme == expected_scheme


def test_load_dataframes(client, wrong_format_client, absolute_path, test_files):
    f = f"{absolute_path}/{test_files}/test.csv"
    read_file = next(client.load_dataframes(fp=f))
    expected = read_csv(f)
    assert read_file.equals(expected)

    with pytest.raises(ConfigurationError):
        next(wrong_format_client.load_dataframes(fp=f))

    with pytest.raises(StopIteration):
        next(client.load_dataframes(fp=f, skip_data=True))


def test_raises_configuration_error_with_incorrect_file_type(csv_format_client, absolute_path, test_files):
    f = f"{absolute_path}/{test_files}/archive_with_test_xlsx.zip"
    with pytest.raises(ConfigurationError):
        next(csv_format_client.load_dataframes(fp=f))


def test_load_dataframes_xlsb(config, absolute_path, test_files):
    config["format"] = "excel_binary"
    client = Client(**config)
    f = f"{absolute_path}/{test_files}/test.xlsb"
    read_file = next(client.load_dataframes(fp=f))
    expected = read_excel(f, engine="pyxlsb")
    assert read_file.equals(expected)


def test_load_nested_json(client, absolute_path, test_files):
    f = f"{absolute_path}/{test_files}/formats/json/demo.json"
    with open(f, mode="rb") as file:
        assert client.load_nested_json(fp=file)


@pytest.mark.parametrize(
    "current_type, dtype, expected",
    [
        ("string", "string", "string"),
        ("", object, "string"),
        ("", "int64", "number"),
        ("", "float64", "number"),
        ("boolean", "bool", "boolean"),
        ("number", "int64", "number"),
        ("number", "float64", "number"),
        ("number", "datetime64[ns]", "datetime"),
    ],
)
def test_dtype_to_json_type(client, current_type, dtype, expected):
    assert client.dtype_to_json_type(current_type, dtype) == expected


def test_cache_stream(client, absolute_path, test_files):
    f = f"{absolute_path}/{test_files}/test.csv"
    with open(f, mode="rb") as file:
        assert client._cache_stream(file)


def test_open_aws_url():
    url = "s3://my_bucket/my_key"
    provider = {"storage": "S3"}
    with pytest.raises(OSError):
        assert URLFile(url=url, provider=provider)._open_aws_url()

    provider.update({"aws_access_key_id": "aws_access_key_id", "aws_secret_access_key": "aws_secret_access_key"})
    with pytest.raises(OSError):
        assert URLFile(url=url, provider=provider)._open_aws_url()


def test_open_azblob_url():
    provider = {"storage": "AZBLOB"}
    with pytest.raises(ValueError):
        assert URLFile(url="", provider=provider)._open_azblob_url()

    provider.update({"storage_account": "storage_account", "sas_token": "sas_token", "shared_key": "shared_key"})
    with pytest.raises(ValueError):
        assert URLFile(url="", provider=provider)._open_azblob_url()


def test_open_gcs_url():
    provider = {"storage": "GCS"}
    with pytest.raises(IndexError):
        assert URLFile(url="", provider=provider)._open_gcs_url()

    provider.update({"service_account_json": '{"service_account_json": "service_account_json"}'})
    with pytest.raises(ValueError):
        assert URLFile(url="", provider=provider)._open_gcs_url()

    provider.update({"service_account_json": '{service_account_json": "service_account_json"}'})
    with pytest.raises(ConfigurationError):
        assert URLFile(url="", provider=provider)._open_gcs_url()


def test_read(test_read_config):
    client = Client(**test_read_config)
    client.sleep_on_retry_sec = 0  # just for test
    with patch.object(client, "load_dataframes", side_effect=ConnectionResetError) as mock_method:
        try:
            return client.read(["date", "key"])
        except ConnectionResetError:
            print("Exception has been raised correctly!")
        mock_method.assert_called()


def test_read_network_issues(test_read_config):
    test_read_config.update(format='excel')
    client = Client(**test_read_config)
    client.sleep_on_retry_sec = 0  # just for test
    with patch.object(client, "_cache_stream", side_effect=ProtocolError), pytest.raises(ConfigurationError):
        next(client.read(["date", "key"]))
