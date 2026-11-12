#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import tempfile
from pathlib import Path

import pytest
import yaml
from components import SellerFeedbackReportsTypeTransformer

from .conftest import get_source, get_stream_by_name
from .integration.config import ConfigBuilder


MANIFEST_PATH = Path(__file__).parent.parent / "manifest.yaml"
IE_MARKETPLACE_ID = "A28R8C7NBKEWEA"


@pytest.fixture
def manifest():
    return yaml.safe_load(MANIFEST_PATH.read_text())


@pytest.fixture
def ie_config():
    config = ConfigBuilder()
    config._config["region"] = "IE"
    return config.build()


def test_ie_in_region_enum(manifest):
    """IE should be present in the region enum list in the manifest spec."""
    region_enum = manifest["spec"]["connection_specification"]["properties"]["region"]["enum"]
    assert "IE" in region_enum


def test_ie_maps_to_eu_endpoint(manifest):
    """IE should map to the EU selling partner API endpoint."""
    transformations = manifest["spec"]["config_normalization_rules"]["transformations"]
    endpoint_remap = next(t for t in transformations if t["type"] == "ConfigRemapField" and t["field_path"] == ["endpoint"])
    eu_endpoint_template = (
        "{{ 'https://sellingpartnerapi' if config['aws_environment'] == 'PRODUCTION' "
        "else 'https://sandbox.sellingpartnerapi' }}-eu.amazon.com"
    )
    assert endpoint_remap["map"].get("IE") == eu_endpoint_template


def test_ie_maps_to_correct_marketplace_id(manifest):
    """IE should map to marketplace ID A28R8C7NBKEWEA."""
    transformations = manifest["spec"]["config_normalization_rules"]["transformations"]
    marketplace_remap = next(t for t in transformations if t["type"] == "ConfigRemapField" and t["field_path"] == ["marketplace_id"])
    assert marketplace_remap["map"]["IE"] == IE_MARKETPLACE_ID


def test_ie_marketplace_date_format_in_seller_feedback():
    """IE marketplace ID should have d/m/y date format in SellerFeedbackReportsTypeTransformer."""
    assert IE_MARKETPLACE_ID in SellerFeedbackReportsTypeTransformer.MARKETPLACE_DATE_FORMAT_MAP
    assert SellerFeedbackReportsTypeTransformer.MARKETPLACE_DATE_FORMAT_MAP[IE_MARKETPLACE_ID] == "%d/%m/%y"


@pytest.mark.parametrize(
    "input_date,expected_date",
    [
        pytest.param("13/1/17", "2017-01-13", id="day_first_single_digit_month"),
        pytest.param("12/12/17", "2017-12-12", id="day_month_double_digits"),
        pytest.param("17/12/17", "2017-12-17", id="day_exceeds_12"),
        pytest.param("13/12/11", "2011-12-13", id="different_year"),
    ],
)
def test_ie_seller_feedback_date_transform(input_date, expected_date):
    """Date transformation for IE marketplace should parse d/m/y format correctly."""
    transformer = SellerFeedbackReportsTypeTransformer(config={"marketplace_id": IE_MARKETPLACE_ID})
    schema = get_stream_by_name("GET_SELLER_FEEDBACK_DATA", ConfigBuilder().build()).get_json_schema()
    input_data = {"date": input_date, "rating": 1, "comments": "c", "response": "r", "order_id": "1", "rater_email": "e"}
    transformer.transform(input_data, schema)
    assert input_data["date"] == expected_date


def test_ie_config_resolves_marketplace_id(ie_config):
    """When region=IE, the source should resolve to the IE marketplace ID."""
    source = get_source(ie_config)
    with tempfile.TemporaryDirectory() as tmp_dir:
        resolved_config = source.configure(config=ie_config, temp_dir=tmp_dir)
    assert resolved_config.get("marketplace_id") == IE_MARKETPLACE_ID


def test_ie_config_resolves_eu_endpoint(ie_config):
    """When region=IE, the source should resolve to the EU endpoint."""
    source = get_source(ie_config)
    with tempfile.TemporaryDirectory() as tmp_dir:
        resolved_config = source.configure(config=ie_config, temp_dir=tmp_dir)
    assert resolved_config.get("endpoint") == "https://sellingpartnerapi-eu.amazon.com"
