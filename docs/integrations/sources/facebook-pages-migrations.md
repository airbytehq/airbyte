# Facebook Pages Migration Guide

## Upgrading to 2.0.0

Version `v2.0.0` updates the API version from v23 to v24.
Deprecated fields have been removed and new fields have been added for the streams `Post`, `Post Insights` and `Page Insights`.

[Deprecated fields API docs](https://developers.facebook.com/docs/platforminsights/page/deprecated-metrics/).

**Post Stream** - this version declares changes to this stream's schema, removing deprecated fields that are no longer available. Refresh stream schema and clear the stream data to continue using this stream. Please, follow Migration Steps below.
**Post Insight Stream and Page Insights Stream** - this version removes deprecated metrics which are no longer available in the records. The Schema is not changed so refreshing the schema is not needed. It is only recommended that you Clear affected streams if you would like to have all data in one consistent format. Please, follow Migration Steps below for Clearing streams. Otherwise, no action is needed for these streams.

**Post Stream Metrics:**

_Added:_

- `allowed_advertising_objects`
- `attachments`
- `full_picture`

_Removed:_

- `event`
- `expanded_height`
- `expanded_width`
- `height`
- `is_inline_created`
- `promotion_status`
- `target`
- `timeline_visibility`
- `via`
- `width`
- `comments`
- `dynamic_posts`
- `likes`
- `reactions`
- `sharedposts`

**Post Insights Stream Metrics:**

_Added:_

- `post_media_view`

_Removed:_

- `post_impressions`
- `post_impressions_paid`
- `post_impressions_fan`
- `post_impressions_fan_paid`
- `post_impressions_fan_paid_unique`
- `post_impressions_organic`
- `post_impressions_viral`
- `post_impressions_nonviral`
- `post_impressions_by_story_type`
- `post_impressions_by_story_type_unique`
- `post_engaged_users`
- `post_negative_feedback`
- `post_negative_feedback_unique`
- `post_negative_feedback_by_type`
- `post_negative_feedback_by_type_unique`
- `post_engaged_fan`
- `post_clicks_unique`
- `post_clicks_by_type_unique`

**Page Insights Stream Metrics:**

_Added:_

- `page_media_view`

_Removed:_

- `page_tab_views_login_top_unique`
- `page_tab_views_login_top`
- `page_tab_views_logout_top`
- `page_cta_clicks_logged_in_total`
- `page_cta_clicks_logged_in_unique`
- `page_cta_clicks_by_site_logged_in_unique`
- `page_cta_clicks_by_age_gender_logged_in_unique`
- `page_cta_clicks_logged_in_by_country_unique`
- `page_cta_clicks_logged_in_by_city_unique`
- `page_call_phone_clicks_logged_in_unique`
- `page_call_phone_clicks_by_age_gender_logged_in_unique`
- `page_call_phone_clicks_logged_in_by_country_unique`
- `page_call_phone_clicks_logged_in_by_city_unique`
- `page_call_phone_clicks_by_site_logged_in_unique`
- `page_get_directions_clicks_logged_in_unique`
- `page_get_directions_clicks_by_age_gender_logged_in_unique`
- `page_get_directions_clicks_logged_in_by_country_unique`
- `page_get_directions_clicks_logged_in_by_city_unique`
- `page_get_directions_clicks_by_site_logged_in_unique`
- `page_website_clicks_logged_in_unique`
- `page_website_clicks_by_age_gender_logged_in_unique`
- `page_website_clicks_logged_in_by_country_unique`
- `page_website_clicks_logged_in_by_city_unique`
- `page_website_clicks_by_site_logged_in_unique`
- `page_engaged_users`
- `page_consumptions`
- `page_consumptions_unique`
- `page_consumptions_by_consumption_type`
- `page_consumptions_by_consumption_type_unique`
- `page_places_checkin_total`
- `page_places_checkin_total_unique`
- `page_places_checkin_mobile`
- `page_places_checkin_mobile_unique`
- `page_places_checkins_by_age_gender`
- `page_places_checkins_by_locale`
- `page_places_checkins_by_country`
- `page_negative_feedback`
- `page_negative_feedback_unique`
- `page_negative_feedback_by_type`
- `page_negative_feedback_by_type_unique`
- `page_positive_feedback_by_type`
- `page_positive_feedback_by_type_unique`
- `page_fans_online`
- `page_fans_online_per_day`
- `page_impressions`
- `page_impressions_paid`
- `page_impressions_organic_v2`
- `page_impressions_organic_unique_v2`
- `page_impressions_viral`
- `page_impressions_nonviral`
- `page_impressions_by_story_type`
- `page_impressions_by_story_type_unique`
- `page_impressions_by_city_unique`
- `page_impressions_by_country_unique`
- `page_impressions_by_locale_unique`
- `page_impressions_by_age_gender_unique`
- `page_impressions_frequency_distribution`
- `page_impressions_viral_frequency_distribution`

### Migration Steps

#### Clearing data for Post Stream

Clearing your data is required for the affected streams to continue syncing successfully. To clear your data for the affected streams, follow the steps below:

1. Select **Connections** in the main navbar and select the connection(s) affected by the update.
2. Select the **Schema** tab.
   1. Select **Refresh source schema** to bring in any schema changes. Any detected schema changes will be listed for your review.
   2. Select **OK** to approve changes.
3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Clear affected streams** option is checked to ensure your streams continue syncing successfully with the new schema.
4. Select **Save connection**.

This will clear the data in your destination for the subset of streams with schema changes. After the clear succeeds,
trigger a sync by clicking **Sync Now**. For more information on clearing your data in Airbyte, see [this page](/platform/operator-guides/clear).

#### Clearing data for Post Insight and Page Insights Streams

To clear data for a single stream, navigate to a Connection's status page, click the three grey dots next to any stream, and select "Clear data". This will clear the data for just that stream. You will then need to sync the connection again in order to reload data for that stream.

## Upgrading to 1.0.0

:::note
This change is only breaking if you are syncing stream `Page`.
:::

This version brings an updated schema for the `v19.0` API version of the `Page` stream.
The `messenger_ads_default_page_welcome_message` field has been deleted, and `call_to_actions`, `posts`, `published_posts`, `ratings`, `tabs` and `tagged` fields have been added.

Users should:

- Refresh the source schema for the `Page` stream.
- Reset the stream after upgrading to ensure uninterrupted syncs.

### Refresh affected schemas and reset data

1. Select **Connections** in the main nav bar.
   1. Select the connection affected by the update.
2. Select the **Replication** tab.
   1. Select **Refresh source schema**.
   2. Select **OK**.

:::note
Any detected schema changes will be listed for your review.
:::

3. Select **Save changes** at the bottom of the page.
   1. Ensure the **Reset affected streams** option is checked.

:::note
Depending on destination type you may not be prompted to reset your data.
:::

4. Select **Save connection**.

:::note
This will reset the data in your destination and initiate a fresh sync.
:::

For more information on resetting your data in Airbyte, see [this page](/platform/operator-guides/clear)
