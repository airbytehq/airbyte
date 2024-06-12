#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from unittest.mock import MagicMock

from source_google_ads.custom_query_stream import CustomQueryMixin, IncrementalCustomQuery
from source_google_ads.utils import GAQL


def test_custom_query():
    input_q = """SELECT ad_group.resource_name, ad_group.status, ad_group.target_cpa_micros, ad_group.target_cpm_micros,
     ad_group.target_roas, ad_group.targeting_setting.target_restrictions, ad_group.tracking_url_template, ad_group.type,
     ad_group.url_custom_parameters, campaign.accessible_bidding_strategy, campaign.ad_serving_optimization_status,
     campaign.advertising_channel_type, campaign.advertising_channel_sub_type, campaign.app_campaign_setting.app_id,
     campaign.app_campaign_setting.app_store FROM search_term_view"""
    output_q = IncrementalCustomQuery.insert_segments_date_expr(GAQL.parse(input_q), "1980-01-01", "1980-01-01")
    assert (
        str(output_q)
        == """SELECT ad_group.resource_name, ad_group.status, ad_group.target_cpa_micros, ad_group.target_cpm_micros, ad_group.target_roas, ad_group.targeting_setting.target_restrictions, ad_group.tracking_url_template, ad_group.type, ad_group.url_custom_parameters, campaign.accessible_bidding_strategy, campaign.ad_serving_optimization_status, campaign.advertising_channel_type, campaign.advertising_channel_sub_type, campaign.app_campaign_setting.app_id, campaign.app_campaign_setting.app_store, segments.date FROM search_term_view WHERE segments.date BETWEEN '1980-01-01' AND '1980-01-01'"""
    )


class Obj:
    def __init__(self, **entries):
        self.__dict__.update(entries)


def test_get_json_schema():
    query_object = MagicMock(
        return_value={
            "a": Obj(data_type=Obj(name="ENUM"), is_repeated=False, enum_values=["a", "aa"]),
            "b": Obj(data_type=Obj(name="ENUM"), is_repeated=True, enum_values=["b", "bb"]),
            "c": Obj(data_type=Obj(name="MESSAGE"), is_repeated=False),
            "d": Obj(data_type=Obj(name="MESSAGE"), is_repeated=True),
            "e": Obj(data_type=Obj(name="STRING"), is_repeated=False),
            "f": Obj(data_type=Obj(name="DATE"), is_repeated=False),
            "segments.month": Obj(data_type=Obj(name="DATE"), is_repeated=False),
        }
    )
    instance = CustomQueryMixin(config={"query": Obj(fields=["a", "b", "c", "d", "e", "f", "segments.month"])})
    instance.cursor_field = None
    instance.google_ads_client = Obj(get_fields_metadata=query_object)
    schema = instance.get_json_schema()

    assert schema == {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": True,
        "type": "object",
        "properties": {
            "a": {"type": "string", "enum": ["a", "aa"]},
            "b": {"type": ["null", "array"], "items": {"type": "string", "enum": ["b", "bb"]}},
            "c": {"type": ["string", "null"]},
            "d": {"type": ["null", "array"], "items": {"type": ["string", "null"]}},
            "e": {"type": ["string", "null"]},
            "f": {"type": ["string", "null"]},
            "segments.month": {"type": ["string", "null"], "format": "date"},
        },
    }
