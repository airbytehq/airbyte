<!--- this comment is for `report-connectors-dependency.yml` identification, do not remove -->

## Affected Connector Report

NOTE ⚠️ Changes in this PR affect the following connectors. Make sure to do the following as needed:
- Run integration tests
- Bump connector or module version
- Add changelog
- Publish the new version

<details {source_open}>
<summary>

### {source_status_summary} Sources ({num_sources})

</summary>

| Connector | Version | Changelog | Publish |
| --- | :---: | :---: | :---: |
{source_rows}

* See "Actionable Items" below for how to resolve warnings and errors.

</details>

<details {destination_open}>
<summary>

### {destination_status_summary} Destinations ({num_destinations})

</summary>

| Connector | Version | Changelog | Publish |
| --- | :---: | :---: | :---: |
{destination_rows}

* See "Actionable Items" below for how to resolve warnings and errors.

</details>

<details open>
<summary>

### {other_status_summary} Other Modules ({num_others})

</summary>

{others_rows}

</details>

<details>

<summary>

### Actionable Items

(click to expand)

</summary>

| Category | Status | Actionable Item |
| --- | :---: | --- |
| Version | ❌<br/>mismatch | The version of the connector is different from its normal variant. Please bump the version of the connector. |
| | ⚠<br/>doc not found | The connector does not seem to have a documentation file. This can be normal (e.g. basic connector like `source-jdbc` is not published or documented). Please double-check to make sure that it is not a bug. |
| Changelog | ⚠<br/>doc not found | The connector does not seem to have a documentation file. This can be normal (e.g. basic connector like `source-jdbc` is not published or documented). Please double-check to make sure that it is not a bug. |
| | ❌<br/>changelog missing | There is no chnagelog for the current version of the connector. If you are the author of the current version, please add a changelog. |
| Publish | ⚠<br/>not in seed | The connector is not in the seed file (e.g. `source_definitions.yaml`), so its publication status cannot be checked. This can be normal (e.g. some connectors are cloud-specific, and only listed in the cloud seed file). Please double-check to make sure that it is not a bug. |
| | ❌<br/>diff seed version | The connector exists in the seed file, but the latest version is not listed there. This usually means that the latest version is not published. Please use the `/publish` command to publish the latest version. |

</details>
