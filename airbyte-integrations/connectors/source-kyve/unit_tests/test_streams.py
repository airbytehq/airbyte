#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_kyve.source import KYVEStream as KyveStream

from . import config, pool_data
from .test_data import MOCK_RESPONSE_BINARY


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(KyveStream, "path", "v0/example_endpoint")
    mocker.patch.object(KyveStream, "primary_key", "test_primary_key")
    mocker.patch.object(KyveStream, "__abstractmethods__", set())


@pytest.mark.parametrize(
    "stream_offset,stream_offset_context,next_page_token_value",
    [
        (None, None, "next_page_token"),
        (None, 200, "next_page_token"),
        (None, None, None),
        (None, 200, None),
        (100, None, None),
        (100, 200, None),
        (100, None, "next_page_token"),
        (100, 200, "next_page_token"),
    ],
)
def test_request_params(patch_base_class, stream_offset, stream_offset_context, next_page_token_value):
    stream = KyveStream(config, pool_data)
    if stream_offset:
        stream._offset = 100

    expected_params = {"pagination.limit": 100, "pagination.offset": stream_offset_context or stream_offset or 0}

    inputs = {
        "stream_slice": None,
        "stream_state": {"offset": stream_offset_context} if stream_offset_context else {},
        "next_page_token": next_page_token_value,
    }

    if next_page_token_value:
        expected_params["next_page_token"] = next_page_token_value
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token_max_pages_set(patch_base_class):
    stream = KyveStream(config, pool_data)
    stream.max_pages = 20
    stream._offset = 2100
    inputs = {"response": MagicMock()}

    assert stream.next_page_token(**inputs) is None


def test_next_page_token(patch_base_class):
    stream = KyveStream(config, pool_data)
    inputs = {"response": MagicMock()}
    expected_token = {"pagination.offset": 100}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, monkeypatch):
    stream = KyveStream(config, pool_data)

    input_request = requests.Response()
    inputs = {"response": input_request, "stream_state": {}}

    mock_input_request_response_json = {
        "finalized_bundles": [
            {
                "pool_id": "1",
                "id": "0",
                "storage_id": "c-24-Ik7KGaB2WJyrW_2fsAjoJkaAD6xfk30qlqEpCI",
                "uploader": "kyve199403h5jgfr64r9ewv83zx7q4xphhc4wyv8mhp",
                "from_index": "0",
                "to_index": "150",
                "from_key": "1",
                "to_key": "150",
                "bundle_summary": "150",
                "data_hash": "18446d6b0988bab5cf946482df579ebd6bd32cb289b26cb5515cfb6883269ef9",
                "finalized_at": {"height": "2355416", "timestamp": "2023-08-21T13:10:45Z"},
                "storage_provider_id": "2",
                "compression_id": "1",
                "stake_security": {"valid_vote_power": "957401304506", "total_vote_power": "1140107500247"},
            }
        ],
        "pagination": {"next_key": "AAAAAAAAAAE=", "total": "36767"},
    }

    mock_finalized_bundles_request = MagicMock(return_value=mock_input_request_response_json)
    monkeypatch.setattr("requests.Response.json", mock_finalized_bundles_request)

    class _MockContentResponse:
        def __init__(self):
            self.content = MOCK_RESPONSE_BINARY
            self.ok = True

    mock_get_content = MagicMock(return_value=_MockContentResponse())
    monkeypatch.setattr("requests.get", mock_get_content)

    expected_parsed_object = {
        "key": "1",
        "value": {
            "block": {
                "block_id": {
                    "hash": "C8DC787FAAE0941EF05C75C3AECCF04B85DFB1D4A8D054A463F323B0D9459719",
                    "parts": {"total": 1, "hash": "B60226F3A84CA6215464AF2983D36C8C7F0CBB12D87F8A933E22DB288EA48E31"},
                },
                "block": {
                    "header": {
                        "version": {"block": "11"},
                        "chain_id": "osmosis-1",
                        "height": "1",
                        "time": "2021-06-18T17:00:00Z",
                        "last_block_id": {"hash": "", "parts": {"total": 0, "hash": ""}},
                        "last_commit_hash": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
                        "data_hash": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
                        "validators_hash": "7730A5F777BDB9143E53FAEFE19399C64C75A6689F9A0F7289D66CFD9D1D5EAF",
                        "next_validators_hash": "7730A5F777BDB9143E53FAEFE19399C64C75A6689F9A0F7289D66CFD9D1D5EAF",
                        "consensus_hash": "62917BBB85377844C3D12DA9C04E65188A959D13AD2647AB1663219822006E2F",
                        "app_hash": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
                        "last_results_hash": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
                        "evidence_hash": "E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855",
                        "proposer_address": "D8A6C54C54A236D4843BA566520BA03F60F09E35",
                    },
                    "data": {"txs": []},
                    "evidence": {"evidence": []},
                    "last_commit": {
                        "height": "0",
                        "round": 0,
                        "block_id": {"hash": "", "parts": {"total": 0, "hash": ""}},
                        "signatures": [],
                    },
                },
            },
            "block_results": {
                "height": "1",
                "txs_results": None,
                "begin_block_events": [
                    {
                        "type": "epoch_start",
                        "attributes": [
                            {"key": "c3RhcnRfdGltZQ==", "value": "MTYyNDAzNTYwMA=="},
                            {"key": "ZXBvY2hfbnVtYmVy", "value": "MA=="},
                        ],
                    },
                    {
                        "type": "epoch_start",
                        "attributes": [
                            {"key": "c3RhcnRfdGltZQ==", "value": "MTYyNDAzNTYwMA=="},
                            {"key": "ZXBvY2hfbnVtYmVy", "value": "MA=="},
                        ],
                    },
                ],
                "end_block_events": None,
                "validator_updates": None,
                "consensus_param_updates": {
                    "block": {"max_bytes": "5242880", "max_gas": "6000000"},
                    "evidence": {"max_age_num_blocks": "403200", "max_age_duration": "1209600000000000", "max_bytes": "1048576"},
                    "validator": {"pub_key_types": ["ed25519"]},
                },
            },
        },
    }

    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_parse_response_error_on_finalized_bundle_fetching(patch_base_class, monkeypatch):
    stream = KyveStream(config, pool_data)

    input_request = requests.Response()
    inputs = {"response": input_request, "stream_state": {}}

    mock_finalized_bundles_request = MagicMock(side_effect=IndexError)
    monkeypatch.setattr("requests.Response.json", mock_finalized_bundles_request)

    with pytest.raises(StopIteration):
        next(stream.parse_response(**inputs))


def test_request_headers(patch_base_class):
    stream = KyveStream(config, pool_data)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = KyveStream(config, pool_data)
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = KyveStream(config, pool_data)
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = KyveStream(config, pool_data)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
