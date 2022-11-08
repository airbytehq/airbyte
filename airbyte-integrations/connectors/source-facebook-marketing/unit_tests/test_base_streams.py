#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from functools import partial
from typing import Any, Iterable, Mapping

import pytest
from facebook_business import FacebookSession
from facebook_business.api import FacebookAdsApi, FacebookAdsApiBatch, FacebookRequest
from source_facebook_marketing.api import MyFacebookAdsApi
from source_facebook_marketing.streams.base_streams import FBMarketingStream


@pytest.fixture(name="mock_batch_responses")
def mock_batch_responses_fixture(requests_mock):
    return partial(requests_mock.register_uri, "POST", f"{FacebookSession.GRAPH}/{FacebookAdsApi.API_VERSION}/")


@pytest.fixture(name="batch")
def batch_fixture(api, mocker):
    batch = FacebookAdsApiBatch(api=api.api)
    mocker.patch.object(batch, "execute", wraps=batch.execute)
    mocker.patch.object(batch, "add_request", wraps=batch.add_request)
    mocker.patch.object(MyFacebookAdsApi, "new_batch", return_value=batch)
    return batch


class SomeTestStream(FBMarketingStream):
    def list_objects(self, params: Mapping[str, Any]) -> Iterable:
        yield from []


class TestBaseStream:
    def test_execute_in_batch_with_few_requests(self, api, batch, mock_batch_responses):
        """Should execute single batch if number of requests less than MAX_BATCH_SIZE."""
        mock_batch_responses(
            [
                {
                    "json": [{"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}}] * 3,
                }
            ]
        )

        stream = SomeTestStream(api=api)
        requests = [FacebookRequest("node", "GET", "endpoint") for _ in range(5)]

        result = list(stream.execute_in_batch(requests))

        assert batch.add_request.call_count == len(requests)
        batch.execute.assert_called_once()
        assert len(result) == 3

    def test_execute_in_batch_with_many_requests(self, api, batch, mock_batch_responses):
        """Should execute as many batches as needed if number of requests bigger than MAX_BATCH_SIZE."""
        mock_batch_responses(
            [
                {
                    "json": [{"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}}] * 5,
                }
            ]
        )

        stream = SomeTestStream(api=api)
        requests = [FacebookRequest("node", "GET", "endpoint") for _ in range(50 + 1)]

        result = list(stream.execute_in_batch(requests))

        assert batch.add_request.call_count == len(requests)
        assert batch.execute.call_count == 2
        assert len(result) == 5 * 2

    def test_execute_in_batch_with_retries(self, api, batch, mock_batch_responses):
        """Should retry batch execution until succeed"""
        # batch.execute.side_effect = [batch, batch, None]
        mock_batch_responses(
            [
                {
                    "json": [
                        {},
                        {},
                        {"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}},
                    ],
                },
                {
                    "json": [
                        {},
                        {"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}},
                    ],
                },
                {
                    "json": [
                        {"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}},
                    ],
                },
            ]
        )

        stream = SomeTestStream(api=api)
        requests = [FacebookRequest("node", "GET", "endpoint") for _ in range(3)]

        result = list(stream.execute_in_batch(requests))

        assert batch.add_request.call_count == len(requests)
        assert batch.execute.call_count == 1
        assert len(result) == 3

    def test_execute_in_batch_with_fails(self, api, batch, mock_batch_responses):
        """Should fail with exception when any request returns error"""
        mock_batch_responses(
            [
                {
                    "json": [
                        {"body": "{}", "code": 500, "headers": {}},
                        {"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}},
                    ],
                }
            ]
        )

        stream = SomeTestStream(api=api)
        requests = [FacebookRequest("node", "GET", "endpoint") for _ in range(5)]

        with pytest.raises(RuntimeError, match="Batch request failed with response:"):
            list(stream.execute_in_batch(requests))

        assert batch.add_request.call_count == len(requests)
        assert batch.execute.call_count == 1

    def test_execute_in_batch_retry_batch_error(self, api, batch, mock_batch_responses):
        """Should retry without exception when any request returns 960 error code"""
        mock_batch_responses(
            [
                {
                    "json": [
                        {"body": json.dumps({"name": "creative 1"}), "code": 200, "headers": {}},
                        {
                            "body": json.dumps(
                                {
                                    "error": {
                                        "message": "Request aborted. This could happen if a dependent request failed or the entire request timed out.",
                                        "type": "FacebookApiException",
                                        "code": 960,
                                        "fbtrace_id": "AWuyQlmgct0a_n64b-D1AFQ",
                                    }
                                }
                            ),
                            "code": 500,
                            "headers": {},
                        },
                        {"body": json.dumps({"name": "creative 3"}), "code": 200, "headers": {}},
                    ],
                },
                {
                    "json": [
                        {"body": json.dumps({"name": "creative 2"}), "code": 200, "headers": {}},
                    ],
                },
            ]
        )

        stream = SomeTestStream(api=api)
        requests = [FacebookRequest("node", "GET", "endpoint") for _ in range(3)]
        result = list(stream.execute_in_batch(requests))

        assert batch.add_request.call_count == len(requests) + 1
        assert batch.execute.call_count == 2
        assert len(result) == len(requests)
