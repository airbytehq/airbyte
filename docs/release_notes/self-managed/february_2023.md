# February 2023

## [airbyte v0.41.0](https://github.com/airbytehq/airbyte/releases/tag/v0.41.0) and [airbyte-platform v0.41.0](https://github.com/airbytehq/airbyte-platform/releases/tag/v0.41.0)

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

### Improvements

- Improved the Airbyte GitHub repository structure and processes by splitting the current repo into two repos, `airbytehq/airbyte` for connectors and `airbytehq/airbyte-platform` for platform code.
  - Allows for isolated changes and improvements to the development workflow.
  - Simplifies the deployment process both internally and externally.

:::note

If you want to contribute to the Airbyte Open Source platform, you will need to switch to `airbytehq/airbyte-platform`. If you want to contribute to Airbyte connectors, continue using `airbytehq/airbyte`.

:::

- Improved low-code CDK to meet the quality and functionality requirements to be promoted to beta. [#22853](https://github.com/airbytehq/airbyte/pull/22853)
- Improved the [Airbyte API](https://api.airbyte.com/) by adding new endpoints:
  - Create sources
  - Create connections
  - Create destinations
  - List jobs (+ job status)
  - Cancel jobs

:::note

The Airbyte API is now in beta. If you are interested in joining the beta program, please email [early-access@airbyte.io](mailto:early-access@airbyte.io)

:::

- Improved Airbyte’s [cost estimator](https://cost.airbyte.com/) UI by redesigning the layout and enhancing the cost visualization for a better user experience.
