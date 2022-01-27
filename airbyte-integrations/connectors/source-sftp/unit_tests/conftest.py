from io import StringIO
import json
import pandas as pd
import pytest

from source_sftp.client import get_client
from source_sftp.stream import SFTPStream, SFTPIncrementalStream


@pytest.fixture
def client_config():
    return {
        "host": "localhost",
        "user": "user",
        "port": "22",
        "password": "1234",
        "request_timeout": "60",
        "read_config": {},
        "dataset_name": "dataset",
        "start_date": "2020-01-01T00:00:00"
    }


@pytest.fixture
def mock_file():
    file_content = """
number_col,str_col,nan_col
1,,text
2,b,text
"""
    return StringIO(file_content)


@pytest.fixture
def dataframe_sample(mock_file):
    return pd.read_csv(mock_file)


@pytest.fixture
def client(client_config):
    return get_client(client_config)


@pytest.fixture
def stream(client):
    return SFTPStream(client, "dataset")


@pytest.fixture
def incremental_stream(client):
    return SFTPIncrementalStream(client, "dataset")
