#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from typing import List, Optional

import pytest
from source_klaviyo.schemas import BaseSchemaModel


class Company(BaseSchemaModel):
    id: int
    name: str
    domain: str
    tags: List[str]


company_schema = {
    "properties": {
        "domain": {"type": "string"},
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "object": {"type": "string"},
        "tags": {"items": {"type": "string"}, "type": "array"},
    },
    "required": ["object", "id", "name", "domain", "tags"],
    "type": "object",
}


class User(BaseSchemaModel):
    id: int
    name: str
    created: datetime
    updated: datetime
    age: int
    nickname: Optional[str]
    company: Optional[Company]


user_schema = {
    "properties": {
        "age": {"type": "integer"},
        "company": {
            "oneOf": [
                {"type": "null"},
                {
                    "properties": {
                        "domain": {"type": "string"},
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "object": {"type": "string"},
                        "tags": {"items": {"type": "string"}, "type": "array"},
                    },
                    "required": ["object", "id", "name", "domain", "tags"],
                    "type": "object",
                },
            ]
        },
        "created": {"format": "date-time", "type": "string"},
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "nickname": {"type": ["null", "string"]},
        "object": {"type": "string"},
        "updated": {"format": "date-time", "type": "string"},
    },
    "required": ["object", "id", "name", "created", "updated", "age"],
    "type": "object",
}


class AdCampaign(BaseSchemaModel):
    date_start: datetime
    date_end: datetime
    name: str
    advanced_options: dict


ad_campaign_schema = {
    "properties": {
        "advanced_options": {"type": "object"},
        "date_end": {"format": "date-time", "type": "string"},
        "date_start": {"format": "date-time", "type": "string"},
        "name": {"type": "string"},
        "object": {"type": "string"},
    },
    "required": ["object", "date_start", "date_end", "name", "advanced_options"],
    "type": "object",
}


@pytest.mark.parametrize("model, expected_schema", ((Company, company_schema), (User, user_schema), (AdCampaign, ad_campaign_schema)))
def test_schema(model, expected_schema):
    assert model.schema() == expected_schema
