# January 2023

## Airbyte [v0.40.27](https://github.com/airbytehq/airbyte/releases/tag/v0.40.27) to [v0.40.32](https://github.com/airbytehq/airbyte/releases/tag/v0.40.32)

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms.

### New features

- Added the [Free Connector Program](https://docs.airbyte.com/cloud/managing-airbyte-cloud/manage-credits#enroll-in-the-free-connector-program) to Airbyte Cloud, allowing you to sync connections with alpha or beta connectors for free.

### Improvements

- Improved Airbyte Open Source by integrating [Docker Compose V2](https://docs.docker.com/compose/compose-v2/). You must have Docker Compose V2 [installed](https://docs.docker.com/compose/install/) before upgrading to Airbyte version 0.42.0 or later. [#19321](https://github.com/airbytehq/airbyte/pull/19321)
- Improved the Airbyte Cloud UI by displaying the **Credits** label in the sidebar and low-credit alerts on the Credits page. [#20595](https://github.com/airbytehq/airbyte/pull/20595)
- Improved the Airbyte CI workflow by adding support to pull requests and limiting the CI runs to only occur on pushes to the master branch. This enhances collaboration with external contributors and reduces unnecessary runs. [#21266](https://github.com/airbytehq/airbyte/pull/21266)
- Improved the connector form by using proper validation in the array section. [#20725](https://github.com/airbytehq/airbyte/pull/20725)
- Ongoing improvements to the [Connector Builder UI](https://docs.airbyte.com/connector-development/config-based/connector-builder-ui/?_ga=2.261393869.1948366377.1675105348-1616004530.1663010260) in alpha:
  - Added support for substream slicers and cartesian slicers, allowing the Connector Builder to create substreams and new streams from multiple existing streams. [#20861](https://github.com/airbytehq/airbyte/pull/20861)
  - Added support for in-schema specification and validation, including a manual schema option. [#20862](https://github.com/airbytehq/airbyte/pull/20862)
  - Added user inputs, request options, authentication, pagination, and slicing to the Connector Builder UI. [#20809](https://github.com/airbytehq/airbyte/pull/20809)
  - Added ability to convert from YAML manifest to UI form values. [#21142](https://github.com/airbytehq/airbyte/pull/21142)
  - Improved the Connector Builder’s conversion of YAML manifest to UI form values by resolving references and options in the manifest. The Connector Builder Server API has been updated with a new endpoint for resolving the manifest, which is now utilized by the conversion function. [#21898](https://github.com/airbytehq/airbyte/pull/21898)

# Bugs

- Fixed an issue where the checkboxes in the stream table would collapse and updated icons to match the new design. [#21108](https://github.com/airbytehq/airbyte/pull/21108)
- Fixed issues with non-breaking schema changes by adding an i18n string, ensuring supported options are rendered, and fixing a custom styling issue when resizing. [#20625](https://github.com/airbytehq/airbyte/pull/20625)
