# Looker

## Overview

The Looker source supports Full Refresh syncs. That is, every time a sync is run, Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source:

- [Boards](https://developers.looker.com/api/explorer/4.0/methods/Board/all_boards)
- [Board Items](https://developers.looker.com/api/explorer/4.0/methods/Board/all_board_items)
- [Board Sections](https://developers.looker.com/api/explorer/4.0/methods/Board/all_board_sections)
- [Color Collections](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/color-collection#get_all_color_collections)
- [Connections](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/connection#get_all_connections)
- [Content Metadata](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/content#get_all_content_metadatas)
- [Content Metadata Access](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/content#get_all_content_metadata_accesses)
- [Dashboards](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/dashboard#get_all_dashboards)
  - [Dashboard Elements](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/dashboard#get_all_dashboardelements)
  - [Dashboard Filters](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/dashboard#get_all_dashboard_filters)
  - [Dashboard Layout Components](https://developers.looker.com/api/explorer/4.0/methods/Dashboard/dashboard_layout_dashboard_layout_components)
  - [Dashboard Layouts](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/dashboard#get_all_dashboardlayouts)
- [Datagroups](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/datagroup#get_all_datagroups)
- [Folders](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/folder#get_all_folders)
- [Folder Ancestors](https://developers.looker.com/api/explorer/4.0/methods/Folder/folder_ancestors)
- [Groups](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/group#get_all_groups)
- [Integration Hubs](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/integration#get_all_integration_hubs)
- [Integrations](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/integration#get_all_integrations)
- [Legacy Features](https://developers.looker.com/api/explorer/4.0/methods/Config/all_legacy_features)
- [Lookml Models](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/lookml-model#get_all_lookml_models)
- [Looks](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/look#get_all_looks)
  - [Run Looks](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/look#run_look)
- [Projects](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/project#get_all_projects)
  - [Project Files](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/project#get_all_project_files)
  - [Git Branches](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/project#get_all_git_branches)
- [Primary Homepage Sections](https://developers.looker.com/api/explorer/4.0/methods/Homepage/all_primary_homepage_sections)
- [Query History](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/query#run_query)
- [Roles](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/role#get_all_roles)
  - [Model Sets](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/role#get_all_model_sets)
  - [Permission Sets](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/role#get_all_permission_sets)
  - [Permissions](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/role#get_all_permissions)
  - [Role Groups](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/role#get_role_groups)
- [Scheduled Plans](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/scheduled-plan#get_all_scheduled_plans)
- [User Attributes](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/user-attribute#get_all_user_attributes)
  - [User Attribute Group Values](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/user-attribute#get_user_attribute_group_values)
- [User Login Lockouts](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/auth#get_all_user_login_lockouts)
- [Users](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/user#get_all_users)
  - [User Attribute Values](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/user#get_user_attribute_values)
  - [User Sessions](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/user#get_all_web_login_sessions)
- [Versions](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/config#get_apiversion)
- [Workspaces](https://docs.looker.com/reference/api-and-integration/api-reference/v4.0/workspace)

If there are more endpoints you'd like Airbyte to support, please [create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature                       | Supported?  |
| :---------------------------- | :---------- |
| Full Refresh Sync             | Yes         |
| Incremental Sync              | Coming soon |
| Replicate Incremental Deletes | Coming soon |
| SSL connection                | Yes         |
| Namespaces                    | No          |

### Performance considerations

The Looker connector should not run into Looker API limitations under normal usage. Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate limit issues that are not automatically retried successfully.

## Getting started

### Requirements

- Client Id
- Client Secret
- Domain

### Setup guide

Please read the "API3 Key" section in [Looker's information for users docs](https://docs.looker.com/admin-options/settings/users) for instructions on how to generate Client Id and Client Secret.

## Changelog

<details>
  <summary>Expand to review</summary>

| Version | Date       | Pull Request                                             | Subject                                                  |
| :------ | :--------- | :------------------------------------------------------- | :------------------------------------------------------- |
| 1.0.13 | 2024-10-12 | [46805](https://github.com/airbytehq/airbyte/pull/46805) | Update dependencies |
| 1.0.12 | 2024-10-05 | [46397](https://github.com/airbytehq/airbyte/pull/46397) | Update dependencies |
| 1.0.11 | 2024-09-28 | [46191](https://github.com/airbytehq/airbyte/pull/46191) | Update dependencies |
| 1.0.10 | 2024-09-21 | [45762](https://github.com/airbytehq/airbyte/pull/45762) | Update dependencies |
| 1.0.9 | 2024-09-14 | [45564](https://github.com/airbytehq/airbyte/pull/45564) | Update dependencies |
| 1.0.8 | 2024-09-07 | [45305](https://github.com/airbytehq/airbyte/pull/45305) | Update dependencies |
| 1.0.7 | 2024-09-05 | [45161](https://github.com/airbytehq/airbyte/pull/45161) | Enable connector in Cloud registry |
| 1.0.6 | 2024-08-31 | [45014](https://github.com/airbytehq/airbyte/pull/45014) | Update dependencies |
| 1.0.5 | 2024-08-24 | [44730](https://github.com/airbytehq/airbyte/pull/44730) | Update dependencies |
| 1.0.4 | 2024-08-17 | [44252](https://github.com/airbytehq/airbyte/pull/44252) | Update dependencies |
| 1.0.3 | 2024-08-12 | [43873](https://github.com/airbytehq/airbyte/pull/43873) | Update dependencies |
| 1.0.2 | 2024-08-10 | [43504](https://github.com/airbytehq/airbyte/pull/43504) | Update dependencies |
| 1.0.1 | 2024-08-03 | [40148](https://github.com/airbytehq/airbyte/pull/40148) | Update dependencies |
| 1.0.0 | 2024-07-23 | [37464](https://github.com/airbytehq/airbyte/pull/37464) | Migrate to LowCode |
| 0.2.12 | 2024-06-06 | [39191](https://github.com/airbytehq/airbyte/pull/39191) | [autopull] Upgrade base image to v1.2.2 |
| 0.2.11 | 2024-06-03 | [38914](https://github.com/airbytehq/airbyte/pull/38914) | Replace AirbyteLogger with logging.Logger |
| 0.2.10 | 2024-06-03 | [38914](https://github.com/airbytehq/airbyte/pull/38914) | Replace AirbyteLogger with logging.Logger |
| 0.2.9 | 2024-05-20 | [38396](https://github.com/airbytehq/airbyte/pull/38396) | [autopull] base image + poetry + up_to_date |
| 0.2.8 | 2022-12-07 | [20182](https://github.com/airbytehq/airbyte/pull/20182) | Fix schema transformation issue |
| 0.2.7 | 2022-01-24 | [9609](https://github.com/airbytehq/airbyte/pull/9609) | Migrate to native CDK and fixing of intergration tests. |
| 0.2.6 | 2021-12-07 | [8578](https://github.com/airbytehq/airbyte/pull/8578) | Update titles and descriptions. |
| 0.2.5 | 2021-10-27 | [7284](https://github.com/airbytehq/airbyte/pull/7284) | Migrate Looker source to CDK structure, add SAT testing. |
| 0.2.4 | 2021-06-25 | [3911](https://github.com/airbytehq/airbyte/pull/3911) | Add `run_look` endpoint. |
| 0.2.3 | 2021-06-22 | [3587](https://github.com/airbytehq/airbyte/pull/3587) | Add support for self-hosted instances. |
| 0.2.2 | 2021-06-09 | [3973](https://github.com/airbytehq/airbyte/pull/3973) | Add `AIRBYTE_ENTRYPOINT` for kubernetes support. |
| 0.2.1 | 2021-04-02 | [2726](https://github.com/airbytehq/airbyte/pull/2726) | Fix connector base versioning. |
| 0.2.0 | 2021-03-09 | [2238](https://github.com/airbytehq/airbyte/pull/2238) | Allow future / unknown properties in the protocol. |
| 0.1.1 | 2021-01-27 | [1857](https://github.com/airbytehq/airbyte/pull/1857) | Fix failed CI tests. |
| 0.1.0 | 2020-12-24 | [1441](https://github.com/airbytehq/airbyte/pull/1441) | Add looker connector. |

</details>
