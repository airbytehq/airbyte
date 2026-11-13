# Contributing to source-facebook-pages

For general guidance on contributing to Airbyte connectors, see the [Connector Development documentation](https://docs.airbyte.com/connector-development/).

**Connector type:** Declarative YAML (low-code CDK), defined in `source_facebook_pages/manifest.yaml`.

## Known API Behaviors

### "Please reduce the amount of data you're asking for" is transient

The Facebook Graph API intermittently returns error code 1 (often with HTTP 500) and the message
`Please reduce the amount of data you're asking for, then retry your request`. Despite the wording,
this error is **not** a reliable signal that the page size is too large: retrying the identical request,
without changing `page_size` or the requested fields, frequently succeeds on a subsequent attempt.

Because of this, the connector's error handler in `manifest.yaml` treats this message as a
`transient_error` with `action: RETRY` rather than failing the sync. Do not reclassify it as a
`config_error` or `FAIL` action; doing so surfaces a hard failure to users for a condition that
usually resolves itself on retry (see airbytehq/airbyte#86489). If the retries are exhausted, the
connector's error message asks the user to lower the Page Size option or deselect unneeded fields.

A future improvement is to automatically reduce the page size when this error persists across the
retry budget, instead of relying on the user to change the source configuration.
