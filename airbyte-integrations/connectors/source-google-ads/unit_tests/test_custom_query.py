#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from source_google_ads.custom_query_stream import CustomQuery


def test_custom_query():
    input_q = """SELECT ad_group.resource_name, ad_group.status, ad_group.target_cpa_micros, ad_group.target_cpm_micros,
     ad_group.target_roas, ad_group.targeting_setting.target_restrictions, ad_group.tracking_url_template, ad_group.type,
     ad_group.url_custom_parameters, campaign.accessible_bidding_strategy, campaign.ad_serving_optimization_status,
     campaign.advertising_channel_type, campaign.advertising_channel_sub_type, campaign.app_campaign_setting.app_id,
     campaign.app_campaign_setting.app_store FROM search_term_view"""
    output_q = CustomQuery.insert_segments_date_expr(input_q, "1980-01-01", "1980-01-01")
    assert (
        output_q
        == """SELECT ad_group.resource_name, ad_group.status, ad_group.target_cpa_micros, ad_group.target_cpm_micros,
     ad_group.target_roas, ad_group.targeting_setting.target_restrictions, ad_group.tracking_url_template, ad_group.type,
     ad_group.url_custom_parameters, campaign.accessible_bidding_strategy, campaign.ad_serving_optimization_status,
     campaign.advertising_channel_type, campaign.advertising_channel_sub_type, campaign.app_campaign_setting.app_id,
     campaign.app_campaign_setting.app_store , segments.date
FROM search_term_view
WHERE segments.date BETWEEN '1980-01-01' AND '1980-01-01'
"""
    )
