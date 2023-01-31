from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, validator


class PromotedTweets(BaseModel):
    id: str
    line_item_id: str
    tweet_id: str
    entity_status: str
    created_at: datetime
    updated_at: datetime
    approval_status: str
    deleted: bool

    @validator("deleted", pre=True, always=True)
    def clean_boolean_values(cls, v: Any) -> bool:  # noqa
        return bool(v)


class PromotedTweetEngagementMetrics(BaseModel):
    promoted_tweet_id: str
    date: date
    app_clicks: Optional[int] = Field(description="Number of app install or app open attempts")
    card_engagements: Optional[int] = Field(description="Total number of card engagements")
    carousel_swipes: Optional[int] = Field(description="Total swipes on Carousel images or videos")
    clicks: Optional[int] = Field(description="Total number of clicks, including favorites and other engagements")
    engagements: Optional[int] = Field(description="Total number of engagements")
    follows: Optional[int] = Field(description="Total number of follows")
    impressions: Optional[int] = Field(description="Total number of impressions")
    likes: Optional[int] = Field(description="Total number of likes")
    poll_card_vote: Optional[int] = Field(description="Total number of poll card votes")
    qualified_impressions: Optional[int] = Field(description="Total number of qualified impressions")
    replies: Optional[int] = Field(description="Total number of replies")
    retweets: Optional[int] = Field(description="Total number of retweets")
    tweets_send: Optional[int] = Field(description="Total number of tweets sends")
    unfollows: Optional[int] = Field(description="Total number of unfollows")
    url_clicks: Optional[int] = Field(description="Total clicks on the link or Website Card in an ad, including earned.")


class PromotedTweetBillingMetrics(BaseModel):
    promoted_tweet_id: str
    date: date
    billed_charge_local_micro: Optional[int] = Field(description="Total spend in micros")
    billed_engagements: Optional[int] = Field(description="Total number of billed engagements")


class PromotedTweetVideoMetrics(BaseModel):
    promoted_tweet_id: str
    date: date
    video_total_views: Optional[int] = Field(description="Total number of video views")
    video_views_25: Optional[int] = Field(description="Total number of views where at least 25% of the video was viewed.")
    video_views_50: Optional[int] = Field(description="Total number of views where at least 50% of the video was viewed.")
    video_views_75: Optional[int] = Field(description="Total number of views where at least 75% of the video was viewed.")
    video_views_100: Optional[int] = Field(description="Total number of views where at least 100% of the video was viewed.")
    video_cta_clicks: Optional[int] = Field(description="Total clicks on the call to action")
    video_content_starts: Optional[int] = Field(description="Total number of video playback starts")
    video_3s100pct_views: Optional[int] = Field(
        description="Total number of views where at least 3 seconds were played while 100% in view (legacy video_total_views)"
    )
    video_6s_views: Optional[int] = Field(description="Total number of views where at least 6 seconds of the video was viewed")
    video_15s_views: Optional[int] = Field(
        description="Total number of views where at least 15 seconds of the video or for 95% of the total duration was viewed"
    )


class PromotedTweetMediaMetrics(BaseModel):
    promoted_tweet_id: str
    date: date
    media_views: Optional[int] = Field(
        description="Total number of views (autoplay and click) of media across Videos, Vines, GIFs, and Images."
    )
    media_engagements: Optional[int] = Field(description="Total number of clicks of media across Videos, Vines, GIFs, and Images.")


class WebConversionMetrics(BaseModel):
    assisted: Optional[int]
    metric: Optional[int]
    order_quantity: Optional[int]
    order_quantity_engagement: Optional[int]
    order_quantity_view: Optional[int]
    post_engagement: Optional[int]
    post_view: Optional[int]
    sale_amount: Optional[int]
    sale_amount_engagement: Optional[int]
    sale_amount_view: Optional[int]


class PromotedTweetWebConversionMetrics(BaseModel):
    promoted_tweet_id: str
    date: date
    auto_created_conversion_landing_page_view: Optional[int]
    auto_created_conversion_session: Optional[int]
    conversion_purchases: WebConversionMetrics = Field(
        description="Number of conversions of type PURCHASE and the corresponding sale amount and order quantity"
    )
    conversion_sign_ups: WebConversionMetrics = Field(
        description="Number of conversions of type SIGN_UP and the corresponding sale amount and order quantity"
    )
    conversion_site_visits: WebConversionMetrics = Field(
        description="Number of conversions of type SITE_VISIT and the corresponding sale amount and order quantity"
    )
    conversion_downloads: WebConversionMetrics = Field(
        description="Number of conversions of type DOWNLOAD and the corresponding sale amount and order quantity"
    )
    conversion_custom: WebConversionMetrics = Field(
        description="Number of conversions of type CUSTOM and the corresponding sale amount and order quantity"
    )


class MobileConversionsPostMetrics(BaseModel):
    post_engagement: Optional[int]
    post_view: Optional[int]


class MobileConversionsMetrics(MobileConversionsPostMetrics):
    assisted: Optional[int]
    order_quantity: Optional[int]
    sale_amount: Optional[int]


class PromotedTweetMobileConversionMetrics(BaseModel):
    promoted_tweet_id: str
    date: date
    mobile_conversion_spent_credits: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type SPENT_CREDIT by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_installs: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type INSTALL by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_content_views: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type CONTENT_VIEW by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_add_to_wishlists: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type ADD_TO_WISHLIST by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_checkouts_initiated: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type CHECKOUT_INITIATED by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_reservations: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type RESERVATION by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_tutorials_completed: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type TUTORIAL_COMPLETED by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_achievements_unlocked: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type ACHIEVEMENT_UNLOCKED by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_searches: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type SEARCH by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_add_to_carts: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type ADD_TO_CART by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_payment_info_additions: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type PAYMENT_INFO_ADDITION by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_re_engages: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type RE_ENGAGE by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_shares: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type SHARE by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_rates: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type RATE by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_logins: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type LOGIN by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_updates: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type UPDATE by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_levels_achieved: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type LEVEL_ACHIEVED by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_invites: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type INVITE by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_key_page_views: MobileConversionsPostMetrics = Field(
        description="Breakdown of mobile conversions of type KEY_PAGE_VIEW by post_view and post_engagement"
    )
    mobile_conversion_downloads: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type DOWNLOAD by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_purchases: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type PURCHASE by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_sign_ups: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type SIGN_UP by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )
    mobile_conversion_site_visits: MobileConversionsMetrics = Field(
        description="Breakdown of mobile conversions of type SITE_VISIT by post_view, post_engagement, assisted, order_quantity, and sale_amount"
    )


class LifeTimeValueMobileConversionMetrics(BaseModel):
    metric: Optional[int]
    order_quantity: Optional[int]
    sale_amount: Optional[int]


class PromotedTweetLifeTimeValueMobileConversion(BaseModel):
    promoted_tweet_id: str
    date: date
    mobile_conversion_lifetime_value_purchases: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type PURCHASE"
    )
    mobile_conversion_lifetime_value_sign_ups: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type SIGN_UP"
    )
    mobile_conversion_lifetime_value_updates: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type UPDATE"
    )
    mobile_conversion_lifetime_value_tutorials_completed: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type TUTORIAL_COMPLETED"
    )
    mobile_conversion_lifetime_value_reservations: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type RESERVATION"
    )
    mobile_conversion_lifetime_value_add_to_carts: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type ADD_TO_CART"
    )
    mobile_conversion_lifetime_value_add_to_wishlists: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type ADD_TO_WISHLIST"
    )
    mobile_conversion_lifetime_value_checkouts_initiated: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type CHECKOUT_INITIATED"
    )
    mobile_conversion_lifetime_value_levels_achieved: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type LEVEL_ACHIEVED"
    )
    mobile_conversion_lifetime_value_achievements_unlocked: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type ACHIEVEMENT_UNLOCKED"
    )
    mobile_conversion_lifetime_value_shares: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type SHARE"
    )
    mobile_conversion_lifetime_value_invites: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type INVITE"
    )
    mobile_conversion_lifetime_value_payment_info_additions: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type PAYMENT_INFO_ADDITION"
    )
    mobile_conversion_lifetime_value_spent_credits: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type SPENT_CREDIT"
    )
    mobile_conversion_lifetime_value_rates: LifeTimeValueMobileConversionMetrics = Field(
        description="Breakdown of mobile conversions of type RATE"
    )


class LineItems(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    campaign_id: str
    entity_status: str
    deleted: bool
    advertiser_user_id: Optional[str]
    name: Optional[str]
    placements: list[str] = []
    start_time: Optional[datetime]
    bid_amount_local_micro: Optional[int]
    advertiser_domain: Optional[str]
    target_cpa_local_micro: Optional[str]
    primary_web_event_tag: Optional[str]
    goal: Optional[str]
    daily_budget_amount_local_micro: Optional[int]
    product_type: Optional[str]
    end_time: Optional[datetime]
    funding_instrument_id: Optional[str]
    bid_strategy: Optional[str]
    duration_in_days: Optional[int]
    standard_delivery: bool
    total_budget_amount_local_micro: Optional[int]
    objective: Optional[str]
    automatic_tweet_promotion: bool
    frequency_cap: Optional[int]
    android_app_store_identifier: Optional[str]
    categories: list[str] = []
    currency: Optional[str]
    pay_by: Optional[str]
    ios_app_store_identifier: Optional[str]
    creative_source: Optional[str]

    @validator("deleted", "standard_delivery", "automatic_tweet_promotion", pre=True, always=True)
    def clean_boolean_values(cls, v: Any) -> bool:  # noqa
        return bool(v)


class Campaigns(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    entity_status: str
    deleted: bool
    name: Optional[str]
    budget_optimization: Optional[str]
    reasons_not_servable: list[str] = []
    servable: bool
    purchase_order_number: Optional[str]
    effective_status: Optional[str]
    daily_budget_amount_local_micro: Optional[int]
    funding_instrument_id: Optional[str]
    duration_in_days: Optional[int]
    standard_delivery: bool
    total_budget_amount_local_micro: Optional[int]
    frequency_cap: Optional[int]
    currency: Optional[str]

    @validator("deleted", "servable", "standard_delivery", pre=True, always=True)
    def clean_boolean_values(cls, v: Any) -> bool:  # noqa
        return bool(v)


class PromotedTweetTweets(BaseModel):
    id: str
    tweet_id: str
    user_id: str
    card_uri: Optional[str]
    name: Optional[str]
    full_text: Optional[str]
    lang: Optional[str]


class PromotedTweetCards(BaseModel):
    id: str
    card_uri: str
    card_type: str
    created_at: datetime
    updated_at: datetime
    deleted: bool
    name: Optional[str]
    components: list[dict] = []

    @validator("deleted", pre=True, always=True)
    def clean_boolean_values(cls, v: Any) -> bool:  # noqa
        return bool(v)
