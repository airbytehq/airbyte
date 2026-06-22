# Criteo Marketing Migration Guide

## Upgrading to 0.1.0

This version adds a required `advertiser_ids` configuration field. The Criteo statistics report API requires advertiser IDs in the request body, but the connector previously did not include them, causing the `ad_spend_daily` stream to fail with HTTP 400 on every sync.

### Migration steps

1. Navigate to your Criteo Marketing source in Airbyte.
2. Click **Settings**.
3. Enter your Criteo advertiser IDs in the new **Advertiser IDs** field. This is a comma-separated list (e.g., `12345` or `12345,67890`). You can find your advertiser IDs in the [Criteo Management Center](https://marketing.criteo.com/).
4. Click **Save changes & test**.
5. If the connection test passes, trigger a sync to verify data flows correctly.
