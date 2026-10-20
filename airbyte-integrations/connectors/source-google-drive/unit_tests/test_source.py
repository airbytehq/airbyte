# Copyright (c) 2026 Airbyte, Inc., all rights reserved.


from unittest.mock import Mock

from source_google_drive import SourceGoogleDrive
from source_google_drive.utils import FOLDER_URL_ERROR

from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.file_based.file_based_source import FileBasedSource


def test_source_instantiation():
    source = SourceGoogleDrive(catalog=None, config=None, state=None)
    assert isinstance(source, SourceGoogleDrive)


def test_source_spec():
    source = SourceGoogleDrive(catalog=None, config=None, state=None)
    spec = source.spec()
    assert isinstance(spec, ConnectorSpecification)
    assert spec.documentationUrl == "https://docs.airbyte.com/integrations/sources/google-drive"


def test_check_connection_rejects_invalid_folder_url_before_api_call(mocker):
    check_connection = mocker.patch.object(FileBasedSource, "check_connection")
    source = SourceGoogleDrive(catalog=None, config=None, state=None)

    result = source.check_connection(Mock(), {"folder_url": "https://drive.google.com/open"})

    assert result == (False, FOLDER_URL_ERROR)
    check_connection.assert_not_called()
