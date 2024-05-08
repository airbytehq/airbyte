# November 2022

## Airbyte [v0.40.18](https://github.com/airbytehq/airbyte/releases/tag/v0.40.18) to [v0.40.23](https://github.com/airbytehq/airbyte/releases/tag/v0.40.23)

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

### New features

- Added multi-region Cloud architecture, which allows for better [data protection](https://airbyte.com/blog/why-airbytes-eu-launch-is-a-milestone-for-our-data-protection-roadmap) and for Airbyte Cloud to [launch in Europe](https://airbyte.com/blog/airbyte-cloud-is-now-available-in-europe).
- Added the [low-code connector builder](https://www.loom.com/share/acf899938ef74dec8dd61ba012bc872f) UI to Airbyte Open Source. Run Airbyte v0.40.19 or higher and visit `localhost:8000/connector-builder` to start building low-code connectors.
- Added a Helm chart for deploying `airbyte-cron`. New installations of Airbyte Open Source will now deploy `airbyte-cron` by default. To disable cron, use `--set cron.enabled=false` when running a `helm install`. [#18542](https://github.com/airbytehq/airbyte/pull/18542)
- Added a progress bar estimate to syncs in Airbyte Cloud. [#19814](https://github.com/airbytehq/airbyte/pull/19814)

### Improvements

- Improved the Airbyte Protocol by introducing Airbyte Protocol v1 [#19846](https://github.com/airbytehq/airbyte/pull/19846), which defines a set of [well-known data types](https://github.com/airbytehq/airbyte/blob/5813700927cfc690d2bffcec28f5286e59ac0122/docs/understanding-airbyte/supported-data-types.md). [#17486](https://github.com/airbytehq/airbyte/pull/17486)
  - These replace existing JSON Schema primitive types.
  - They provide out-of-the-box validation and enforce specific formatting on some data types, like timestamps.
  - Non-primitive types, like `object`, `array`, and ` oneOf`, still use raw JSON Schema types.
  - These well-known types mostly correspond with the existing Airbyte data types, aside from a few differences:
    - `BinaryData` is the only new type, which is used in places that previously produced a `Base64` string.
    - `TimestampWithTimezone`, `TimestampWithoutTimezone`, `TimeWithTimezone`, and `TimeWithoutTimezone` have been in use for some time, so we made them official.
    - The `big_integer` and `big_number` types have been retired because they were not being used.
