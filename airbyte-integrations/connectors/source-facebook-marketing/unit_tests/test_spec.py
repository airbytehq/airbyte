#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_facebook_marketing import SourceFacebookMarketing


@pytest.fixture
def spec_properties():
    spec = SourceFacebookMarketing().spec(None)
    return spec.connectionSpecification["properties"]


def _access_token_descriptions(properties):
    descriptions = [properties["access_token"]["description"]]
    for option in properties["credentials"]["oneOf"]:
        descriptions.append(option["properties"]["access_token"]["description"])
    return descriptions


def test_access_token_descriptions_recommend_system_user_token(spec_properties):
    for description in _access_token_descriptions(spec_properties):
        assert "read_insights" not in description
        assert '"Marketing API" then "Tools"' not in description
        assert "System users" in description
        assert "ads_read" in description
        assert "ads_management" in description


def test_start_date_description_mentions_37_months(spec_properties):
    description = spec_properties["start_date"]["description"]
    assert "37 months" in description
    assert "2 years" not in description
