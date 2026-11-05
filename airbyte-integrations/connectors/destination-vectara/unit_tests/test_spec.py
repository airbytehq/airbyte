#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json
from pathlib import Path

from destination_vectara import DestinationVectara
from destination_vectara.config import VectaraConfig

from airbyte_cdk.models import ConnectorSpecificationSerializer


def test_spec_matches_baseline():
    expected_spec = json.loads((Path(__file__).parent / "resources/expected_spec.json").read_text())

    assert ConnectorSpecificationSerializer.dump(DestinationVectara().spec()) == expected_spec


def test_connection_specification_matches_baseline():
    expected_spec = json.loads((Path(__file__).parent / "resources/expected_spec.json").read_text())
    spec = ConnectorSpecificationSerializer.dump(DestinationVectara().spec())

    assert spec["connectionSpecification"] == expected_spec["connectionSpecification"]


def test_config_defaults():
    config = VectaraConfig.parse_obj(
        {
            "oauth2": {"client_id": "client-id", "client_secret": "client-secret"},
            "corpus_name": "test-corpus",
        }
    )

    assert config.parallelize is False
    assert config.text_fields == []
    assert config.title_field == ""
    assert config.metadata_fields == []
    assert config.customer_id is None
