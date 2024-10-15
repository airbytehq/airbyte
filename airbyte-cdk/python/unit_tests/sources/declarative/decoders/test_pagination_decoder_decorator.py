#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import pytest
import requests
from airbyte_cdk.sources.declarative.decoders import JsonDecoder, PaginationDecoderDecorator


class StreamingJsonDecoder(JsonDecoder):
    def is_stream_response(self) -> bool:
        return True


@pytest.mark.parametrize(
        "decoder_class, expected",
        [
            (StreamingJsonDecoder, {}),
            (JsonDecoder, {"data": [{"id": 1}, {"id": 2}]})
        ]
)
def test_pagination_decoder_decorator(requests_mock, decoder_class, expected):
    decoder = PaginationDecoderDecorator(decoder=decoder_class(parameters={}))
    response_body = "{\"data\": [{\"id\": 1}, {\"id\": 2}]}"
    requests_mock.register_uri("GET", "https://airbyte.io/", text=response_body)
    response = requests.get("https://airbyte.io/")
    assert next(decoder.decode(response)) == expected
