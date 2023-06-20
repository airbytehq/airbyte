from unittest import mock
from source_kapiche_export_api.source import SourceKapicheExportApi


def test_check_connection(mocker):
    source = SourceKapicheExportApi()
    with mock.patch("source_kapiche_export_api.source.ExportDataList") as list_endpoint:
        logger_mock = mock.MagicMock()
        config_mock = {
            "api_token": "some-token",
            "export_api_url": "https://app.kapiche/export.com",
        }
        list_stream_object = mock.MagicMock()
        response = mock.MagicMock()
        response.status_code = 200
        list_stream_object._send_request.return_value = response
        list_endpoint.return_value = list_stream_object
        assert source.check_connection(logger_mock, config_mock) == (True, None)


def test_streams(mocker):
    source = SourceKapicheExportApi()
    with mock.patch("source_kapiche_export_api.source.ExportDataList") as list_endpoint:
        config_mock = {
            "api_token": "some-token",
            "export_api_url": "https://app.kapiche/export.com",
        }
        list_stream_object = mock.MagicMock()
        response = mock.MagicMock()
        response.json.return_value = [
            {
                "uuid": "uuid1",
                "export_url": "endpoint1",
                "project_name": "test1",
                "analysis_name": "test1",
                "enabled": False,
            },
            {
                "uuid": "uuid2",
                "export_url": "endpoint2",
                "project_name": "test2",
                "analysis_name": "test2",
                "enabled": True,
            },
        ]
        response.status_code = 200
        list_stream_object._send_request.return_value = response
        list_endpoint.return_value = list_stream_object
        streams = source.streams(config_mock)
        assert len(streams) == 1
