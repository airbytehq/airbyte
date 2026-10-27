import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

# Facebook Pages Migration Guide

## Upgrading to 4.0.0

This version moves the connector from Graph API v24.0 to v26.0. Every stream now calls `https://graph.facebook.com/v26.0`, which is the version Meta released on 2026-07-29 and the one with the longest remaining life, so the connector no longer sits close to a version retirement.

Meta removed a set of video and Reels insights metrics from every API version when v26.0 launched, and this version stops requesting the ones that were in the connector defaults. The `video_insights` stream no longer requests `total_video_views_unique`, `total_video_impressions` or `total_video_impressions_unique`, and the `reel_insights` stream no longer requests `post_impressions_unique`. The stream schemas are unchanged, because each metric is a row rather than a column, so rows for those metrics simply stop arriving. If you set a custom **Video Insights Metrics** or **Reel Insights Metrics** list that still names one of them, Facebook rejects the whole request and the sync fails with the "must be a valid insights metric" error, so remove them from your list.

This version also removes the `commerce_orders` column from the `page` stream schema. Meta removed the `/{page-id}/commerce_orders` endpoint from all API versions on 2026-10-27 as part of retiring the Commerce Order Management API, with no replacement, so the column could never be populated again. The connector never requested that edge by default, so the request it sends for the `page` stream is unchanged.

:::caution
If you need the last-known values of the removed video and Reels metrics, or of `page.commerce_orders`, export or snapshot them before upgrading and refreshing the schema. Meta no longer serves any of them on any API version.
:::

### Why this change?

Meta retires each Graph API version roughly two years after release, and v24.0 is scheduled to be retired on 2028-02-18, so staying on it put a deadline on the connector. Moving to v26.0 resets that clock. The metric removals and the Commerce Order Management API retirement were announced in the [v25.0 changelog](https://developers.facebook.com/docs/graph-api/changelog/version25.0) and the [v26.0 changelog](https://developers.facebook.com/docs/graph-api/changelog/version26.0), and both apply to every API version, so they affect the connector whether or not it moves to v26.0. The other v26.0 changes, such as the removal of the legacy Page fields, were already handled in version 3.0.0, and the connector does not use the retired `pretty`, `debug`, `date_format` or `If-None-Match` request options.

### Who is affected?

- `video_insights` — rows for `total_video_views_unique`, `total_video_impressions` and `total_video_impressions_unique` are no longer emitted. The schema is unchanged.
- `reel_insights` — rows for `post_impressions_unique` are no longer emitted. The schema is unchanged.
- `page` — the `commerce_orders` column is removed from the schema.
- `post`, `page_insights`, `post_insights`, `comment` and `rating` are unaffected beyond the API version change. The fields and metrics they request all exist in v26.0.

No specification, configuration or state changes are required unless you set a custom video or Reels metric list that names a removed metric.

### Migration steps

1. Upgrade the connector to version `4.0.0`.
2. Refresh the source schema for the `page` stream.
3. Update downstream models or SQL that reference `page.commerce_orders`.
4. If you set a custom **Video Insights Metrics** or **Reel Insights Metrics** list, remove `total_video_views_unique`, `total_video_impressions`, `total_video_impressions_unique` and `post_impressions_unique` from it.

Clearing the streams is not required. Clear `video_insights` or `reel_insights` only if you prefer a history in your destination that does not contain rows for the removed metrics.

## Upgrading to 3.0.0

This version removes the Meta-deprecated legacy Page fields `current_location`, `genre`, `network`, `parking` and `start_info` from the `page` stream schema. The connector no longer requests them.

This version also stops requesting `page.live_videos` and removes it from the `page` stream schema. Meta does not make the `/{page-id}/live_videos` edge available for New Pages Experience Pages; requesting it returns `(#10) To use live-video-api ...` and the connector maps that response to a configuration error, causing the entire `page` stream to fail.

:::caution
These fields are not requested after upgrading, and Meta no longer serves them for New Pages Experience Pages. If you need the last-known values of `current_location`, `genre`, `network`, `parking` or `start_info`, export or snapshot those columns before upgrading and refreshing the schema.
:::

### Why this change?

Meta deprecated these fields for New Pages Experience Pages in Graph API v26.0, launched on 2026-07-29, and provides no replacement. Meta states that the deprecation will reach all remaining supported Graph API versions approximately 90 days after launch; the exact date is to be confirmed. The connector's error handler fails hard on `Tried accessing nonexisting field`, so leaving these fields in the request would fail the entire `page` stream. If you sync a New Pages Experience Page and stay on `2.x`, the `page` stream will start failing once Meta applies the change to all API versions. See the [Meta Graph API v26.0 changelog](https://developers.facebook.com/docs/graph-api/changelog/version26.0).

### Who is affected?

- `page` — all five fields are removed from the top-level record, and `current_location`, `genre` and `network` are removed from the nested `best_page` and `parent_page` objects.
- `page.live_videos` — the edge is removed from the `page` stream.
- `post` — `current_location`, `genre` and `network` are removed from the nested page objects under `sponsor_tags[].data[]`. `parking` and `start_info` were never present there.
- `page_insights` and `post_insights` are unaffected; no action is required for them.

No specification, configuration, or state changes are required.

### Migration steps

1. Upgrade the connector to version `3.0.0`.
2. Refresh the source schema for the `page` and `post` streams.
3. Update downstream models or SQL that reference any of the following:
   - `page.current_location`, `page.genre`, `page.network`, `page.parking`, `page.start_info`
   - `page.live_videos`
   - `page.best_page.current_location`, `page.best_page.genre`, `page.best_page.network`
   - `page.parent_page.current_location`, `page.parent_page.genre`, `page.parent_page.network`
   - `post.sponsor_tags.data[].current_location`, `post.sponsor_tags.data[].genre`, `post.sponsor_tags.data[].network`

Clearing the `page` stream is not required.

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

## Connector upgrade guide

<MigrationGuide />
