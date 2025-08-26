# HubSpot
This directory contains the manifest-only connector for `source-hubspot`.

## Changelog

### 6.0.0 - Breaking Changes
**Marketing Emails API Migration**

This version migrates the `marketing_emails` stream from HubSpot's deprecated v1 API to the new v3 API.

**Important: This is a breaking change that requires a data reset.**

#### Changes:
- Migrated from `/marketing-emails/v1/emails/with-statistics` to `/marketing/v3/emails?includeStats=true`
- Updated response field path from `objects` to `results`
- No data loss expected, but schema may have minor differences

#### Migration Instructions:
1. **Full Refresh Required**: You must reset your `marketing_emails` stream data
2. **Timeline**: HubSpot will sunset the v1 API on **October 1, 2025**
3. **Action Required**: Update to version 6.0.0 before the deadline

For more details, see [HubSpot's API migration announcement](https://developers.hubspot.com/changelog/marketing-email-api-v3-released-to-general-availability-and-upcoming-sunset-for-v1).

## Documentation reference:
Visit `https://developers.hubspot.com/` for API documentation

## Authentication setup
**If you are a community contributor**, follow the instructions in the [documentation](https://docs.airbyte.com/integrations/sources/hubspot)
to generate the necessary credentials. Then create a file `secrets/config.json` conforming to the `source_hubspot/spec.yaml` file.
Note that any directory named `secrets` is gitignored across the entire Airbyte repo, so there is no danger of accidentally checking in sensitive information.
See `sample_files/sample_config.json` for a sample config file.

## Usage
There are multiple ways to use this connector:
- You can use this connector as any other connector in Airbyte Marketplace.
- You can load this connector in `pyairbyte` using `get_source`!
- You can open this connector in Connector Builder, edit it, and publish to your workspaces.

Please refer to the manifest-only connector documentation for more details.

## Local Development
We recommend you use the Connector Builder to edit this connector.

But, if you want to develop this connector locally, you can use the following steps.

### Environment Setup
You will need `airbyte-ci` installed. You can find the documentation [here](airbyte-ci).

### Build
This will create a dev image (`source-hubspot:dev`) that you can use to test the connector locally.
```bash
airbyte-ci connectors --name=source-hubspot build
```

### Test
This will run the acceptance tests for the connector.
```bash
airbyte-ci connectors --name=source-hubspot test
```
