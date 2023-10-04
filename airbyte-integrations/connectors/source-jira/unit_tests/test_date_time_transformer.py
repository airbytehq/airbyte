#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_jira.source import SourceJira
from source_jira.streams import ApplicationRoles


@pytest.mark.parametrize(
    "origin_item,subschema,expected",
    [
        ("2023-05-08T03:04:45.139-0700", {"type": "string", "format": "date-time"}, "2023-05-08T03:04:45.139000-07:00"),
        ("2022-10-31T09:00:00.594Z", {"type": "string", "format": "date-time"}, "2022-10-31T09:00:00.594000+00:00"),
        ("2023-09-11t17:51:41.666-0700", {"type": "string", "format": "date-time"}, "2023-09-11T17:51:41.666000-07:00"),
        ("some string", {"type": "string"}, "some string"),
        (1234, {"type": "integer"}, 1234),
    ],
)
def test_converting_date_to_date_time(origin_item, subschema, expected, config):
    authenticator = SourceJira().get_authenticator(config=config)
    args = {"authenticator": authenticator, "domain": config["domain"], "projects": config.get("projects", [])}
    stream = ApplicationRoles(**args)
    actual = stream.transformer.default_convert(origin_item, subschema)
    assert actual == expected
