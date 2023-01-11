# December 2022
## Airbyte [v0.40.24](https://github.com/airbytehq/airbyte/releases/tag/v0.40.24) to [v0.40.26](https://github.com/airbytehq/airbyte/releases/tag/v0.40.26)

This page includes new features and improvements to the Airbyte Cloud and Airbyte Open Source platforms. 

### New features
* Added throughput metrics and progress bar to running syncs in the Connection Sync History UI for Airbyte Open Source. This gives users real-time information on data transfer rates and progress of syncs. [#19193](https://github.com/airbytehq/airbyte/pull/19193)
* Added custom connector UI to Airbyte Cloud in alpha, which allows users to create and update custom connectors. [#20483](https://github.com/airbytehq/airbyte/pull/20483)
* Added the stream details panel to the Connection Replication UI, which allows you to display and configure streams in your connection. [#19219](https://github.com/airbytehq/airbyte/pull/19219)
    * Added source-defined **Cursor** and **Primary key** fields to the stream details panel. [#20366](https://github.com/airbytehq/airbyte/pull/20366) 
* Added the UX flow for auto-detect schema changes. [#19226](https://github.com/airbytehq/airbyte/pull/19226)
* Added auto-detect schema changes option to the Connection Replication UI, which allows you to choose if Airbyte ignores or disables the connection when it detects a non-breaking schema change in the source. [#19734](https://github.com/airbytehq/airbyte/pull/19734)
* Added stream table configuration windows for Destination namespace and Stream name, which allow you to choose how the data is stored and edit the names and prefixes of tables in the destination. [#19713](https://github.com/airbytehq/airbyte/pull/19713)
* Added the AWS Secret Manager to Airbyte Open Source as an option for storing secrets. [#19690](https://github.com/airbytehq/airbyte/pull/19690)
* Added the [Airbyte Cloud API](http://reference.airbyte.com/) in alpha, which allows you to programmatically control Airbyte Cloud through an API.

### Improvements
* Improved the Connection UX by preventing users from editing an existing connection if there is a breaking change in the source schema. Now users must review changes before editing the connection. [#20276](https://github.com/airbytehq/airbyte/pull/20276)
* Improved stream catalog index by defining `stream`. This precaution keeps all streams matching correctly and data organized consistently. [#20443](https://github.com/airbytehq/airbyte/pull/20443)
* Ongoing improvements to Low-code CDK in alpha:
    * Added `SessionTokenAuthenticator` for authentication management. [#19716](https://github.com/airbytehq/airbyte/pull/19716)
    * Added the first iteration of the Configuration UI, which allows users to build connectors by filling out forms instead of writing a YAML file. [#20008](https://github.com/airbytehq/airbyte/pull/20008)
    * Added request options component to streams. Users can now choose request options for streams in the connector builder. [#20497](https://github.com/airbytehq/airbyte/pull/20497)
    * Fixed an issue where errors were not indicated properly by disregarding individually touched fields in `useBuilderErrors`. [#20463](https://github.com/airbytehq/airbyte/pull/20463)
    * Updated UI to match the current design and includes UI text changes and the addition of the stream delete button. [#20464](https://github.com/airbytehq/airbyte/pull/20464)
    * Upgraded Orval and updated the connector builder OpenAPI to pull the connector manifest schema directly into the API. [#20166](https://github.com/airbytehq/airbyte/pull/20166)
