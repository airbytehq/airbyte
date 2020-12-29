# Looker

## Overview

The Looker source supports Full Refresh syncs. That is, every time a sync is run, 
Airbyte will copy all rows in the tables and columns you set up for replication into the destination in a new table.

### Output schema

Several output streams are available from this source:

* [Color Collections](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/color-collection#get_all_color_collections)
* [Connections](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/connection#get_all_connections)
* [Content Metadata](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/content#get_all_content_metadatas)
* [Content Metadata Access](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/content#get_all_content_metadata_accesses)
* [Dashboards](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/dashboard#get_all_dashboards)
  * [Dashboard Elements](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/dashboard#get_all_dashboardelements) 
  * [Dashboard Filters](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/dashboard#get_all_dashboard_filters) 
  * [Dashboard Layouts](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/dashboard#get_all_dashboardlayouts) 
* [Datagroups](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/datagroup#get_all_datagroups) 
* [Folders](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/folder#get_all_folders) 
* [Groups](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/group#get_all_groups) 
* [Homepages](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/homepage#get_all_homepages) 
* [Integration Hubs](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/integration#get_all_integration_hubs) 
* [Integrations](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/integration#get_all_integrations) 
* [Lookml Dashboards](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/dashboard#get_all_dashboards) 
* [Lookml Models](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/lookml-model#get_all_lookml_models) 
* [Looks](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/look#get_all_looks) 
* [Projects](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/project#get_all_projects) 
  * [Project Files](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/project#get_all_project_files) 
  * [Git Branches](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/project#get_all_git_branches) 
* [Query History](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/query#run_query) 
* [Roles](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/role#get_all_roles) 
  * [Model Sets](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/role#get_all_model_sets) 
  * [Permission Sets](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/role#get_all_permission_sets) 
  * [Permissions](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/role#get_all_permissions) 
  * [Role Groups](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/role#get_role_groups) 
* [Scheduled Plans](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/scheduled-plan#get_all_scheduled_plans) 
* [Spaces](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/space#get_all_spaces) 
* [User Attributes](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/user-attribute#get_all_user_attributes) 
  * [User Attribute Group Value](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/user-attribute#get_user_attribute_group_values) 
* [User Login Lockouts](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/auth#get_all_user_login_lockouts) 
* [Users](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/user#get_all_users) 
  * [User Attribute Values](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/user#get_user_attribute_values) 
  * [User Sessions](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/user#get_all_web_login_sessions) 
* [Versions](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/config#get_apiversion) 
* [Workspaces](https://docs.looker.com/reference/api-and-integration/api-reference/v3.1/workspace) 

If there are more endpoints you'd like Airbyte to support, please 
[create an issue.](https://github.com/airbytehq/airbyte/issues/new/choose)

### Features

| Feature | Supported? |
| :--- | :--- |
| Full Refresh Sync | Yes |
| Incremental Sync | No |
| Replicate Incremental Deletes | No |
| SSL connection | Yes |

### Performance considerations

The Looker connector should not run into Looker API limitations under normal usage. 
Please [create an issue](https://github.com/airbytehq/airbyte/issues) if you see any rate 
limit issues that are not automatically retried successfully.

## Getting started

### Requirements

* Client Id
* Client Secret
* Domain

### Setup guide

Please read the "API3 Key" section in [Looker's information for users docs](https://docs.looker.com/admin-options/settings/users) for instructions on how to generate Client Id and Client Secret.
