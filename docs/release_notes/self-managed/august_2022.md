# August 2022

## Airbyte [v0.39.42-alpha](https://github.com/airbytehq/airbyte/releases/tag/v0.39.42-alpha) to [v0.40.3](https://github.com/airbytehq/airbyte/releases/tag/v0.40.3)

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

### New features

- Added reserved keywords for schema names by fixing the quotation logic in normalization. [#14683](https://github.com/airbytehq/airbyte/pull/14683)

- Added [documentation](https://docs.airbyte.com/cloud/managing-airbyte-cloud/review-sync-summary) about the data displayed in sync log summaries. [#15181](https://github.com/airbytehq/airbyte/pull/15181)

- Added OAuth login to Airbyte Cloud, which allows you to sign in using your Google login credentials. [#15414](https://github.com/airbytehq/airbyte/pull/15414)

  - You can use your Google login credentials to sign in to your Airbyte account if they share the same email address.

  - You can create a new Airbyte account with OAuth using your Google login credentials.

  - You cannot use OAuth to log in if you are invited to join a workspace.

### Improvements

- Improved the Airbyte version naming conventions by removing the `-alpha` tag. The Airbyte platform is used successfully by thousands of users, so the `-alpha` tag is no longer necessary. [#15766](https://github.com/airbytehq/airbyte/pull/15766)

- Improved the `loadBalancerIP` in the web app by making it configurable. [#14992](https://github.com/airbytehq/airbyte/pull/14992)

- Datadog:

  - Improved the Airbyte platform by supporting StatsD, which sends Temporal metrics to Datadog. [#14842](https://github.com/airbytehq/airbyte/pull/14842)

  - Added Datadog tags to help you identify metrics between Airbyte instances. [#15213](https://github.com/airbytehq/airbyte/pull/15213)

  - Added metric client tracking to record schema validation errors. [#13393](https://github.com/airbytehq/airbyte/pull/13393)

### Bugs

- Fixed an issue where data types did not display correctly in the UI. The correct data types are now displayed in the streams of your connections. [#15558](https://github.com/airbytehq/airbyte/pull/15558)

- Fixed an issue where requests would fail during a release by adding a shutdown hook to the Airbyte server. This ensures the requests will be gracefully terminated before they can fail. [#15934](https://github.com/airbytehq/airbyte/pull/15934)

- Helm charts:

  - Fixed the deployment problems of the Helm chart with FluxCD by removing unconditional resource assignment in the chart for Temporal. [#15374](https://github.com/airbytehq/airbyte/pull/15374)

  - Fixed the following issues in [#15199](https://github.com/airbytehq/airbyte/pull/15199):

    - Fixed an issue where `toyaml` was being used instead of `toYaml`, which caused Helm chart installation to fail.

    - Fixed incorrect `extraContainers` indentation, which caused Helm chart installation to fail if the value was supplied.

    - Fixed incorrect Postgres secret reference and made it more user friendly.

    - Updated the method of looking up secrets and included an override feature to protect users from common mistakes.
