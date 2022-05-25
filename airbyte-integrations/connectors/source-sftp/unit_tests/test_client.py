from datetime import datetime
from unittest.mock import patch

import numpy as np
import pytest
import pytz
from source_sftp.client import Client, get_client

NUM_DF = 5


@pytest.fixture
def yield_multi_df(dataframe_sample):
    return [dataframe_sample.copy(deep=True) for i in range(NUM_DF)]


def test_get_client(client_config):
    client = get_client(client_config)
    assert isinstance(client, Client)


@pytest.mark.parametrize(
    "mocked_files, expected",
    [
        (
            [
                {"filepath": "file_old.csv", "last_modified": datetime(2021, 1, 1, tzinfo=pytz.UTC)},
                {"filepath": "file_new.csv", "last_modified": datetime(2022, 1, 1, tzinfo=pytz.UTC)},
            ],
            [
                {"filepath": "file_old.csv", "last_modified": datetime(2021, 1, 1, tzinfo=pytz.UTC)},
                {"filepath": "file_new.csv", "last_modified": datetime(2022, 1, 1, tzinfo=pytz.UTC)},
            ],
        )
    ],
)
@patch("source_sftp.client.Client.get_files_by_prefix")
def test_get_files(mocked_function, client_config, mocked_files, expected):
    mocked_function.return_value = mocked_files
    client = get_client(client_config)
    file_infos = client.get_files("", ".*")
    assert file_infos == expected


@pytest.mark.parametrize(
    "mocked_files, expected",
    [
        (
            [
                {"filepath": "file_old.csv", "last_modified": datetime(2021, 1, 1, tzinfo=pytz.UTC)},
                {"filepath": "file_new.csv", "last_modified": datetime(2022, 1, 1, tzinfo=pytz.UTC)},
            ],
            [
                {"filepath": "file_new.csv", "last_modified": datetime(2022, 1, 1, tzinfo=pytz.UTC)},
            ],
        )
    ],
)
@patch("source_sftp.client.Client.get_files_by_prefix")
def test_get_files_modified_sync(mocked_function, client_config, mocked_files, expected):
    mocked_function.return_value = mocked_files
    client = get_client(client_config)
    file_infos = client.get_files("", ".*", modified_since=datetime(2021, 6, 1, tzinfo=pytz.UTC))
    assert file_infos == expected


@pytest.mark.parametrize(
    "mocked_files, expected",
    [
        (
            [
                {"filepath": "file_old.csv", "last_modified": datetime(2021, 1, 1, tzinfo=pytz.UTC)},
                {"filepath": "file_new.csv", "last_modified": datetime(2022, 1, 1, tzinfo=pytz.UTC)},
            ],
            [
                {"filepath": "file_old.csv", "last_modified": datetime(2021, 1, 1, tzinfo=pytz.UTC)},
            ],
        )
    ],
)
@patch("source_sftp.client.Client.get_files_by_prefix")
def test_get_files_matching_pattern(mocked_function, client_config, mocked_files, expected):
    mocked_function.return_value = mocked_files
    client = get_client(client_config)
    file_infos = client.get_files("", "^.*old.*csv")
    assert file_infos == expected


@patch("source_sftp.client.Client.load_dataframes")
def test_read(mocked_load_df, yield_multi_df, client_config):
    mocked_load_df.return_value = yield_multi_df
    client = get_client(client_config)
    records = list(client.read(""))
    assert len(records) == NUM_DF * 2
    for rec in records:
        for _, value in rec.items():
            assert value != np.nan


@patch("source_sftp.client.Client.load_dataframes")
def test_get_file_properties(mocked_load_df, yield_multi_df, client_config):
    expected = {
        "number_col": {"type": ["number", "null"]},
        "str_col": {"type": ["string", "null"]},
        "nan_col": {"type": ["string", "null"]}
    }
    mocked_load_df.return_value = yield_multi_df
    client = get_client(client_config)
    properties = client.get_file_properties("")
    assert properties == expected

