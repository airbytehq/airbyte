<!--- this comment is for `report-connectors-dependency.yml` identification, do not remove -->

NOTE ⚠️ Changes in this PR affect the following connectors. Make sure to do the following as needed:
- Run integration tests
- Bump connector version
- Add changelog
- Publish the new version

<details {source_open}>
<summary>

### {source_status_summary} Sources ({num_sources})

</summary>

| Connector | Version | Changelog | Publish |
| --- | :---: | :---: | :---: |
{source_rows}

</details>

<details {destination_open}>
<summary>

### {destination_status_summary} Destinations ({num_destinations})

</summary>

| Connector | Version | Changelog | Publish |
| --- | :---: | :---: | :---: |
{destination_rows}

</details>

{others}
