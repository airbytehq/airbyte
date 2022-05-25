from unittest.mock import patch

from airbyte_cdk.entrypoint import logger
from source_sftp.source import SourceSftp
from source_sftp.stream import SFTPIncrementalStream


def test_streams(client_config):
    source = SourceSftp()
    streams = source.streams(client_config)
    assert len(streams) == 1
    assert isinstance(streams[0], SFTPIncrementalStream)


@patch("source_sftp.client.Client.get_files")
def test_check_connection_pass_with_no_files(mocked_get_files, client_config):
    mocked_get_files.return_value = []
    source = SourceSftp()
    result, exc = source.check_connection(logger, client_config)
    assert result
    assert exc is None
