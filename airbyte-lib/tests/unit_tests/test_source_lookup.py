import pytest
from unittest.mock import patch

from sqlalchemy import all_
from airbyte_lib._factories.connector_factories import _find_source, _normalize_source_name



@pytest.mark.parametrize('search_name, found, similar', [
    ('source-google-sheets', 'google-sheets', None),
    ('google-sheets', 'google-sheets', None),
    ('sheets', None, ['google-sheets']),
    ('googlesheets', None, ['google-sheets', 'google-ads']),
    ('facebook-ads', None, ['facebook']),
    ('source-instagram', None, []),
    ('instagram', None, []),
])
@patch('airbyte_lib._factories.connector_factories.get_all_source_names')
def test_find_source_exists(
    mock_get_all_source_names,
    search_name,
    found,
    similar
):
    all_source_names = [
        'source-google-sheets', 'source-google-adwords', 'source-google-ads', 'source-facebook', 'source-twitter'
    ]
    mock_get_all_source_names.return_value = all_source_names
    source_name, similar_source_names = _find_source(search_name)
    assert source_name == found
    assert similar_source_names == similar


@pytest.mark.parametrize('input_name, normalized_name', [
    ('source-google-sheets', 'google-sheets'),
    ('google-sheets', 'google-sheets'),
    ('google_sheets', 'google-sheets'),
    ('google sheets', 'google-sheets'),
    ('source-google_sheets', 'google-sheets'),
    ('source-google sheets', 'google-sheets'),
])
def test_source_name_normalization(
    input_name='source-google-sheets',
    expected_normalized_name='google-sheets'
):
    assert _normalize_source_name(input_name) == expected_normalized_name
