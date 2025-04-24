#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from functools import cache


@cache
def get_analytics_columns() -> str:
    # https://developers.pinterest.com/docs/api/v5/#operation/ad_account/analytics
    analytics_columns = [
        "ADVERTISER_ID",  #
        "AD_ACCOUNT_ID",
        "AD_GROUP_ENTITY_STATUS",
        "AD_GROUP_ID",
        "AD_ID",
        "CAMPAIGN_DAILY_SPEND_CAP",
        "CAMPAIGN_ENTITY_STATUS",
        "CAMPAIGN_ID",
        "CAMPAIGN_LIFETIME_SPEND_CAP",
        "CAMPAIGN_NAME",
        "CHECKOUT_ROAS",
        "CLICKTHROUGH_1",  #
        "CLICKTHROUGH_1_GROSS",  #
        "CLICKTHROUGH_2",  #
        "CPC_IN_MICRO_DOLLAR",
        "CPM_IN_DOLLAR",
        "CPM_IN_MICRO_DOLLAR",
        "CTR",
        "CTR_2",
        "ECPCV_IN_DOLLAR",
        "ECPCV_P95_IN_DOLLAR",
        "ECPC_IN_DOLLAR",
        "ECPC_IN_MICRO_DOLLAR",
        "ECPE_IN_DOLLAR",
        "ECPM_IN_MICRO_DOLLAR",
        "ECPV_IN_DOLLAR",
        "ECTR",
        "EENGAGEMENT_RATE",
        "ENGAGEMENT_1",  #
        "ENGAGEMENT_2",  #
        "ENGAGEMENT_RATE",
        "IDEA_PIN_PRODUCT_TAG_VISIT_1",
        "IDEA_PIN_PRODUCT_TAG_VISIT_2",
        "IMPRESSION_1",
        "IMPRESSION_1_GROSS",
        "IMPRESSION_2",
        "INAPP_CHECKOUT_COST_PER_ACTION",
        "OUTBOUND_CLICK_1",
        "OUTBOUND_CLICK_2",
        "PAGE_VISIT_COST_PER_ACTION",
        "PAGE_VISIT_ROAS",
        "PAID_IMPRESSION",
        "PIN_ID",  #
        "PIN_PROMOTION_ID",  #
        "REPIN_1",  #
        "REPIN_2",  #
        "REPIN_RATE",
        "SPEND_IN_DOLLAR",
        "SPEND_IN_MICRO_DOLLAR",
        "TOTAL_CHECKOUT",
        "TOTAL_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_CLICKTHROUGH",
        "TOTAL_CLICK_ADD_TO_CART",  #
        "TOTAL_CLICK_CHECKOUT",
        "TOTAL_CLICK_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_CLICK_LEAD",  #
        "TOTAL_CLICK_SIGNUP",
        "TOTAL_CLICK_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_CONVERSIONS",
        "TOTAL_CUSTOM",  #
        "TOTAL_ENGAGEMENT",  #
        "TOTAL_ENGAGEMENT_CHECKOUT",
        "TOTAL_ENGAGEMENT_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_ENGAGEMENT_LEAD",  #
        "TOTAL_ENGAGEMENT_SIGNUP",
        "TOTAL_ENGAGEMENT_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_IDEA_PIN_PRODUCT_TAG_VISIT",
        "TOTAL_IMPRESSION_FREQUENCY",
        "TOTAL_IMPRESSION_USER",
        "TOTAL_LEAD",  #
        "TOTAL_OFFLINE_CHECKOUT",  #
        "TOTAL_PAGE_VISIT",
        "TOTAL_REPIN_RATE",
        "TOTAL_SIGNUP",
        "TOTAL_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_VIDEO_3SEC_VIEWS",
        "TOTAL_VIDEO_AVG_WATCHTIME_IN_SECOND",
        "TOTAL_VIDEO_MRC_VIEWS",
        "TOTAL_VIDEO_P0_COMBINED",
        "TOTAL_VIDEO_P100_COMPLETE",
        "TOTAL_VIDEO_P25_COMBINED",
        "TOTAL_VIDEO_P50_COMBINED",
        "TOTAL_VIDEO_P75_COMBINED",
        "TOTAL_VIDEO_P95_COMBINED",
        "TOTAL_VIEW_ADD_TO_CART",  #
        "TOTAL_VIEW_CHECKOUT",
        "TOTAL_VIEW_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_VIEW_LEAD",  #
        "TOTAL_VIEW_SIGNUP",
        "TOTAL_VIEW_SIGNUP_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_CHECKOUT",
        "TOTAL_WEB_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_CLICK_CHECKOUT",
        "TOTAL_WEB_CLICK_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_ENGAGEMENT_CHECKOUT",
        "TOTAL_WEB_ENGAGEMENT_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "TOTAL_WEB_SESSIONS",  #
        "TOTAL_WEB_VIEW_CHECKOUT",
        "TOTAL_WEB_VIEW_CHECKOUT_VALUE_IN_MICRO_DOLLAR",
        "VIDEO_3SEC_VIEWS_2",
        "VIDEO_LENGTH",  #
        "VIDEO_MRC_VIEWS_2",
        "VIDEO_P0_COMBINED_2",
        "VIDEO_P100_COMPLETE_2",
        "VIDEO_P25_COMBINED_2",
        "VIDEO_P50_COMBINED_2",
        "VIDEO_P75_COMBINED_2",
        "VIDEO_P95_COMBINED_2",
        "WEB_CHECKOUT_COST_PER_ACTION",
        "WEB_CHECKOUT_ROAS",
        "WEB_SESSIONS_1",  #
        "WEB_SESSIONS_2",  #
    ]
    return ",".join(analytics_columns)


def to_datetime_str(date: datetime) -> str:
    """
    Returns the formated datetime string.
    :: Output example: '2021-07-15' FORMAT : "%Y-%m-%d"
    """
    return date.strftime("%Y-%m-%d")
