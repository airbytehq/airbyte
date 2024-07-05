#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, patch

import pytest
from requests.models import Response
from source_klaviyo.components.inclouded_fields_extractor import KlaviyoIncludedFieldExtractor


@pytest.fixture
def mock_response():
    return Mock(spec=Response)


@pytest.fixture
def mock_decoder():
    return Mock()


@pytest.fixture
def mock_config():
    return Mock()


@pytest.fixture
def mock_field_path():
    return [Mock() for _ in range(2)]


@pytest.fixture
def extractor(mock_config, mock_field_path, mock_decoder):
    return KlaviyoIncludedFieldExtractor(mock_field_path, mock_config, mock_decoder)


@patch('dpath.util.get')
@patch('dpath.util.values')
def test_extract_records_by_path(mock_values, mock_get, extractor, mock_response, mock_decoder):
    mock_values.return_value = [{'key': 'value'}]
    mock_get.return_value = {'key': 'value'}
    mock_decoder.decode.return_value = {'data': 'value'}

    field_paths = ['data']
    records = list(extractor.extract_records_by_path(mock_response, field_paths))
    assert records == [{'key': 'value'}]

    mock_values.return_value = []
    mock_get.return_value = None
    records = list(extractor.extract_records_by_path(mock_response, ['included']))
    assert records == []


def test_update_target_records_with_included(extractor):
    target_records = [{'relationships': {'type1': {'data': {}}}}]
    included_records = [{'type': 'type1', 'attributes': {'key': 'value'}}]

    updated_records = list(extractor.update_target_records_with_included(target_records, included_records))
    assert updated_records[0]['relationships']['type1']['data'] == {'key': 'value'}
