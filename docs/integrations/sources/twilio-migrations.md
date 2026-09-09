# Twilio Migration Guide

## Upgrading to 1.0.0

Version `1.0.0` migrates the `services` and `roles` streams from Twilio's
deprecated [Programmable Chat REST API](https://www.twilio.com/en-us/changelog/programmable-chat-end-of-life-notice)
(base URL `https://chat.twilio.com/v2`) to the
[Twilio Conversations API](https://www.twilio.com/docs/conversations/api/service-resource)
(base URL `https://conversations.twilio.com/v1`).

### What changed

- The `services` stream now reads from
  `GET https://conversations.twilio.com/v1/Services` instead of
  `GET https://chat.twilio.com/v2/Services`.
- The `roles` stream now reads from
  `GET https://conversations.twilio.com/v1/Services/{ChatServiceSid}/Roles`
  instead of `GET https://chat.twilio.com/v2/Services/{ServiceSid}/Roles`.
- The record schemas for both streams have been simplified to match what the
  Conversations API actually returns. For the `services` stream, the
  Conversations API returns a much smaller set of fields than the deprecated
  Chat API — for example, `consumption_report_interval`,
  `default_service_role_sid`, `default_channel_role_sid`,
  `default_channel_creator_role_sid`, `limits`, `notifications`,
  `pre_webhook_url`, `post_webhook_url`, `pre_webhook_retry_count`,
  `post_webhook_retry_count`, `reachability_enabled`, `read_status_enabled`,
  `typing_indicator_timeout`, `webhook_filters`, `webhook_method`, and `media`
  are no longer declared on Service records.
- On the `roles` stream, the `service_sid` field has been renamed to
  `chat_service_sid` to match the Conversations API response.
- The `chat.twilio.com` host has been removed from the connector's
  `allowedHosts` list and replaced with `conversations.twilio.com`.

### Known limitations

> [!WARNING]
> **The `account_sid` field on `services` records is now always `null`.**
> The Twilio Conversations API does not populate `account_sid` for Service
> resources, whereas the deprecated Chat API returned the actual account
> SID. If your downstream pipelines or dashboards rely on `account_sid`
> from the `services` stream, you will need to update them. The `roles`
> stream is **not** affected and continues to return `account_sid` with
> the correct value.
>
> This is a Twilio API behavior, not an Airbyte connector bug. The field
> is [documented in Twilio's API reference](https://www.twilio.com/docs/conversations/api/service-resource)
> but consistently returns `null` in practice, including for newly created
> services.

### Why we made this change

Twilio
[deprecated the Programmable Chat API in 2021](https://www.twilio.com/en-us/changelog/programmable-chat-end-of-life-notice)
and has now
[scheduled its final end of life — including Programmable Chat in Flex — for June 1, 2026](https://www.twilio.com/en-us/changelog/programmable-chat-in-flex-reaching-end-of-life-on-june-1--2026).
After that date, requests to `chat.twilio.com/v2` will fail and any sync that
includes the `services` or `roles` streams would break. Twilio's official
replacement for these resources is the Conversations API.

Per Twilio's
[migration guide](https://www.twilio.com/docs/conversations/migrating-chat-conversations),
"the Conversations API is built on the Programmable Chat foundation, and most
of your existing messaging and user data is going to be made available
automatically, with no data migration required." Service SIDs (`IS...`) and
Role SIDs (`RL...`) are preserved across the migration, so existing records
keep the same primary keys after the upgrade.

### Who is affected

Only users who have the `services` or `roles` streams enabled in their Twilio
source connections are impacted. All other streams (for example, `accounts`,
`calls`, `messages`, `conversations`, `users`, `verify_services`) are
unchanged.

### Migration steps

Take these steps after upgrading the connector to version `1.0.0`:

1. Open the Twilio source in the Airbyte UI.
2. Click **Refresh source schema** so Airbyte picks up the updated
   `services` and `roles` schemas.
3. For each connection that syncs the `services` or `roles` streams, clear
   data for those two streams so that the next sync repopulates them using
   the new Conversations API shape. Records from the deprecated Chat API
   endpoint may reference fields that no longer exist in the destination
   schema.
4. Trigger a sync. The `services` and `roles` streams will now read from
   `conversations.twilio.com/v1` and produce records matching the
   Conversations API schema.

No credential changes are required. HTTP Basic authentication with your
Twilio Account SID and Auth Token continues to work against the
Conversations API.

## Connector upgrade guide

import MigrationGuide from '@site/static/_migration_guides_upgrade_guide.md';

<MigrationGuide />
