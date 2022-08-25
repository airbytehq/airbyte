from tempfile import TemporaryFile

import pytest
from pandas import read_excel
from source_file.client import Client, URLFile


@pytest.fixture
def urlfile():
    return URLFile()


@pytest.fixture
def client():
    return Client(
        dataset_name="test_dataset",
        url="scp://test_dataset",
        provider={"provider": {"storage": "HTTPS", "reader_impl": "gcsfs", "user_agent": False}},
    )


@pytest.fixture
def expected_excel_reader():
    return read_excel(engine="pyxlsb")


@pytest.fixture
def temp_excel_file(tmp_path_factory):
    return tmp_path_factory.mktemp("data") / "df.xls"


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


# @pytest.mark.parametrize(
#     "storage, url",
#     [
#         ("GCS", "gs://fileurl"),
#         ("S3", "s3://fileurl"),
#         ("AZBLOB", "azure://fileurl"),
#         ("HTTPS", "https://fileurl"),
#         ("SSH", "scp://fileurl"),
#         ("SCP", "scp://fileurl"),
#         ("SFTP", "sftp://fileurl"),
#         ("WEBHDFS", "webhdfs://fileurl"),
#         ("LOCAL", "file://fileurl"),
#     ],
# )
# def test_urlfile_open(storage, url):
#     urlfile = URLFile(provider={"storage": storage}, url=url)
#     tmp_file = TemporaryFile()
#     urlfile._open(tmp_file)


#  def test_load_dataframes(mocker, client, temp_excel_file):
#     reader = next(client.load_dataframes(fp=temp_excel_file))
#     assert reader == read_excel(temp_excel_file, engine="pyxlsb")
