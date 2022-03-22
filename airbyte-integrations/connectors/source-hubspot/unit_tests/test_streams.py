#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pendulum
from source_hubspot.streams import ContactLists

from .utils import read_incremental


def test_updated_at_field_non_exist_handler(requests_mock, common_params, fake_properties_list):
    stream = ContactLists(**common_params)

    responses = [
        {
            "json": {
                stream.data_field: [
                    {
                        "id": "test_id",
                        "createdAt": "2022-03-25T16:43:11Z",
                    },
                ],
            }
        }
    ]
    properties_response = [
        {
            "json": [
                {"name": property_name, "type": "string", "updatedAt": 1571085954360, "createdAt": 1565059306048}
                for property_name in fake_properties_list
            ],
            "status_code": 200,
        }
    ]

    requests_mock.register_uri("GET", stream.url, responses)
    requests_mock.register_uri("GET", "/properties/v2/contact/properties", properties_response)

    _, stream_state = read_incremental(stream, {})

    expected = int(pendulum.parse(common_params["start_date"]).timestamp() * 1000)

    assert stream_state[stream.updated_at_field] == expected
