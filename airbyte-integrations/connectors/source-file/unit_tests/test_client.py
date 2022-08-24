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
        provider={"provider": {
            "storage": "HTTPS",
            "reader_impl": "gcsfs",
            "user_agent": False}})


@pytest.fixture
def expected_excel_reader():
    return read_excel(engine="pyxlsb")


@pytest.fixture
def temp_excel_file(tmp_path_factory):
    return tmp_path_factory.mktemp("data") / "df.xls"


# def test_load_dataframes(mocker, client, temp_excel_file):
#     reader = next(client.load_dataframes(fp=temp_excel_file))
#     assert reader == read_excel(temp_excel_file, engine="pyxlsb")
