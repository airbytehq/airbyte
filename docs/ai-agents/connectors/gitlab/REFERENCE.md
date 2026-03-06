# Gitlab full reference

This is the full reference documentation for the Gitlab agent connector.

## Supported entities and actions

The Gitlab connector supports the following entities and actions.

| Entity | Actions |
|--------|---------|
| Projects | [List](#projects-list), [Get](#projects-get), [Search](#projects-search) |
| Issues | [List](#issues-list), [Get](#issues-get), [Search](#issues-search) |
| Merge Requests | [List](#merge-requests-list), [Get](#merge-requests-get), [Search](#merge-requests-search) |
| Users | [List](#users-list), [Get](#users-get), [Search](#users-search) |
| Commits | [List](#commits-list), [Get](#commits-get), [Search](#commits-search) |
| Groups | [List](#groups-list), [Get](#groups-get), [Search](#groups-search) |
| Branches | [List](#branches-list), [Get](#branches-get), [Search](#branches-search) |
| Pipelines | [List](#pipelines-list), [Get](#pipelines-get), [Search](#pipelines-search) |
| Group Members | [List](#group-members-list), [Get](#group-members-get), [Search](#group-members-search) |
| Project Members | [List](#project-members-list), [Get](#project-members-get), [Search](#project-members-search) |
| Releases | [List](#releases-list), [Get](#releases-get), [Search](#releases-search) |
| Tags | [List](#tags-list), [Get](#tags-get), [Search](#tags-search) |
| Group Milestones | [List](#group-milestones-list), [Get](#group-milestones-get), [Search](#group-milestones-search) |
| Project Milestones | [List](#project-milestones-list), [Get](#project-milestones-get), [Search](#project-milestones-search) |

## Projects

### Projects List

Get a list of all visible projects across GitLab for the authenticated user.

#### Python SDK

```python
await gitlab.projects.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number (1-indexed) |
| `per_page` | `integer` | No | Number of items per page (max 100) |
| `membership` | `boolean` | No | Limit by projects that the current user is a member of |
| `owned` | `boolean` | No | Limit by projects explicitly owned by the current user |
| `search` | `string` | No | Return list of projects matching the search criteria |
| `order_by` | `"id" \| "name" \| "path" \| "created_at" \| "updated_at" \| "last_activity_at" \| "similarity" \| "star_count"` | No | Return projects ordered by field |
| `sort` | `"asc" \| "desc"` | No | Return projects sorted in asc or desc order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `name_with_namespace` | `string` |  |
| `path` | `string` |  |
| `path_with_namespace` | `string` |  |
| `description` | `null \| string` |  |
| `default_branch` | `null \| string` |  |
| `visibility` | `string` |  |
| `web_url` | `string` |  |
| `ssh_url_to_repo` | `string` |  |
| `http_url_to_repo` | `string` |  |
| `created_at` | `string` |  |
| `last_activity_at` | `string` |  |
| `namespace` | `object` |  |
| `archived` | `boolean` |  |
| `forks_count` | `integer` |  |
| `star_count` | `integer` |  |
| `open_issues_count` | `integer` |  |
| `topics` | `array<string>` |  |
| `avatar_url` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `description_html` | `null \| string` |  |
| `tag_list` | `null \| array` |  |
| `readme_url` | `null \| string` |  |
| `_links` | `null \| object` |  |
| `container_registry_image_prefix` | `null \| string` |  |
| `empty_repo` | `null \| boolean` |  |
| `packages_enabled` | `null \| boolean` |  |
| `marked_for_deletion_at` | `null \| string` |  |
| `marked_for_deletion_on` | `null \| string` |  |
| `container_registry_enabled` | `null \| boolean` |  |
| `container_expiration_policy` | `null \| object` |  |
| `repository_object_format` | `null \| string` |  |
| `issues_enabled` | `null \| boolean` |  |
| `merge_requests_enabled` | `null \| boolean` |  |
| `wiki_enabled` | `null \| boolean` |  |
| `jobs_enabled` | `null \| boolean` |  |
| `snippets_enabled` | `null \| boolean` |  |
| `service_desk_enabled` | `null \| boolean` |  |
| `service_desk_address` | `null \| string` |  |
| `can_create_merge_request_in` | `null \| boolean` |  |
| `resolve_outdated_diff_discussions` | `null \| boolean` |  |
| `lfs_enabled` | `null \| boolean` |  |
| `shared_runners_enabled` | `null \| boolean` |  |
| `group_runners_enabled` | `null \| boolean` |  |
| `creator_id` | `null \| integer` |  |
| `import_url` | `null \| string` |  |
| `import_type` | `null \| string` |  |
| `import_status` | `null \| string` |  |
| `import_error` | `null \| string` |  |
| `emails_disabled` | `null \| boolean` |  |
| `emails_enabled` | `null \| boolean` |  |
| `show_diff_preview_in_email` | `null \| boolean` |  |
| `auto_devops_enabled` | `null \| boolean` |  |
| `auto_devops_deploy_strategy` | `null \| string` |  |
| `request_access_enabled` | `null \| boolean` |  |
| `merge_method` | `null \| string` |  |
| `squash_option` | `null \| string` |  |
| `enforce_auth_checks_on_uploads` | `null \| boolean` |  |
| `shared_with_groups` | `null \| array` |  |
| `only_allow_merge_if_pipeline_succeeds` | `null \| boolean` |  |
| `allow_merge_on_skipped_pipeline` | `null \| boolean` |  |
| `only_allow_merge_if_all_discussions_are_resolved` | `null \| boolean` |  |
| `remove_source_branch_after_merge` | `null \| boolean` |  |
| `printing_merge_request_link_enabled` | `null \| boolean` |  |
| `build_timeout` | `null \| integer` |  |
| `auto_cancel_pending_pipelines` | `null \| string` |  |
| `build_git_strategy` | `null \| string` |  |
| `public_jobs` | `null \| boolean` |  |
| `restrict_user_defined_variables` | `null \| boolean` |  |
| `keep_latest_artifact` | `null \| boolean` |  |
| `runner_token_expiration_interval` | `null \| string` |  |
| `resource_group_default_process_mode` | `null \| string` |  |
| `ci_config_path` | `null \| string` |  |
| `ci_default_git_depth` | `null \| integer` |  |
| `ci_delete_pipelines_in_seconds` | `null \| integer` |  |
| `ci_forward_deployment_enabled` | `null \| boolean` |  |
| `ci_forward_deployment_rollback_allowed` | `null \| boolean` |  |
| `ci_job_token_scope_enabled` | `null \| boolean` |  |
| `ci_separated_caches` | `null \| boolean` |  |
| `ci_allow_fork_pipelines_to_run_in_parent_project` | `null \| boolean` |  |
| `ci_id_token_sub_claim_components` | `null \| array` |  |
| `ci_pipeline_variables_minimum_override_role` | `null \| string` |  |
| `ci_push_repository_for_job_token_allowed` | `null \| boolean` |  |
| `ci_display_pipeline_variables` | `null \| boolean` |  |
| `protect_merge_request_pipelines` | `null \| boolean` |  |
| `suggestion_commit_message` | `null \| string` |  |
| `merge_commit_template` | `null \| string` |  |
| `squash_commit_template` | `null \| string` |  |
| `issue_branch_template` | `null \| string` |  |
| `merge_request_title_regex` | `null \| string` |  |
| `merge_request_title_regex_description` | `null \| string` |  |
| `warn_about_potentially_unwanted_characters` | `null \| boolean` |  |
| `autoclose_referenced_issues` | `null \| boolean` |  |
| `max_artifacts_size` | `null \| integer` |  |
| `external_authorization_classification_label` | `null \| string` |  |
| `requirements_enabled` | `null \| boolean` |  |
| `requirements_access_level` | `null \| string` |  |
| `security_and_compliance_enabled` | `null \| boolean` |  |
| `security_and_compliance_access_level` | `null \| string` |  |
| `compliance_frameworks` | `null \| array` |  |
| `web_based_commit_signing_enabled` | `null \| boolean` |  |
| `permissions` | `null \| object` |  |
| `issues_access_level` | `null \| string` |  |
| `repository_access_level` | `null \| string` |  |
| `merge_requests_access_level` | `null \| string` |  |
| `forking_access_level` | `null \| string` |  |
| `wiki_access_level` | `null \| string` |  |
| `builds_access_level` | `null \| string` |  |
| `snippets_access_level` | `null \| string` |  |
| `pages_access_level` | `null \| string` |  |
| `analytics_access_level` | `null \| string` |  |
| `container_registry_access_level` | `null \| string` |  |
| `releases_access_level` | `null \| string` |  |
| `environments_access_level` | `null \| string` |  |
| `feature_flags_access_level` | `null \| string` |  |
| `infrastructure_access_level` | `null \| string` |  |
| `monitor_access_level` | `null \| string` |  |
| `model_experiments_access_level` | `null \| string` |  |
| `model_registry_access_level` | `null \| string` |  |
| `package_registry_access_level` | `null \| string` |  |


</details>

### Projects Get

Get a specific project by ID.

#### Python SDK

```python
await gitlab.projects.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID or URL-encoded path of the project |
| `statistics` | `boolean` | No | Include project statistics |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `name_with_namespace` | `string` |  |
| `path` | `string` |  |
| `path_with_namespace` | `string` |  |
| `description` | `null \| string` |  |
| `default_branch` | `null \| string` |  |
| `visibility` | `string` |  |
| `web_url` | `string` |  |
| `ssh_url_to_repo` | `string` |  |
| `http_url_to_repo` | `string` |  |
| `created_at` | `string` |  |
| `last_activity_at` | `string` |  |
| `namespace` | `object` |  |
| `archived` | `boolean` |  |
| `forks_count` | `integer` |  |
| `star_count` | `integer` |  |
| `open_issues_count` | `integer` |  |
| `topics` | `array<string>` |  |
| `avatar_url` | `null \| string` |  |
| `updated_at` | `null \| string` |  |
| `description_html` | `null \| string` |  |
| `tag_list` | `null \| array` |  |
| `readme_url` | `null \| string` |  |
| `_links` | `null \| object` |  |
| `container_registry_image_prefix` | `null \| string` |  |
| `empty_repo` | `null \| boolean` |  |
| `packages_enabled` | `null \| boolean` |  |
| `marked_for_deletion_at` | `null \| string` |  |
| `marked_for_deletion_on` | `null \| string` |  |
| `container_registry_enabled` | `null \| boolean` |  |
| `container_expiration_policy` | `null \| object` |  |
| `repository_object_format` | `null \| string` |  |
| `issues_enabled` | `null \| boolean` |  |
| `merge_requests_enabled` | `null \| boolean` |  |
| `wiki_enabled` | `null \| boolean` |  |
| `jobs_enabled` | `null \| boolean` |  |
| `snippets_enabled` | `null \| boolean` |  |
| `service_desk_enabled` | `null \| boolean` |  |
| `service_desk_address` | `null \| string` |  |
| `can_create_merge_request_in` | `null \| boolean` |  |
| `resolve_outdated_diff_discussions` | `null \| boolean` |  |
| `lfs_enabled` | `null \| boolean` |  |
| `shared_runners_enabled` | `null \| boolean` |  |
| `group_runners_enabled` | `null \| boolean` |  |
| `creator_id` | `null \| integer` |  |
| `import_url` | `null \| string` |  |
| `import_type` | `null \| string` |  |
| `import_status` | `null \| string` |  |
| `import_error` | `null \| string` |  |
| `emails_disabled` | `null \| boolean` |  |
| `emails_enabled` | `null \| boolean` |  |
| `show_diff_preview_in_email` | `null \| boolean` |  |
| `auto_devops_enabled` | `null \| boolean` |  |
| `auto_devops_deploy_strategy` | `null \| string` |  |
| `request_access_enabled` | `null \| boolean` |  |
| `merge_method` | `null \| string` |  |
| `squash_option` | `null \| string` |  |
| `enforce_auth_checks_on_uploads` | `null \| boolean` |  |
| `shared_with_groups` | `null \| array` |  |
| `only_allow_merge_if_pipeline_succeeds` | `null \| boolean` |  |
| `allow_merge_on_skipped_pipeline` | `null \| boolean` |  |
| `only_allow_merge_if_all_discussions_are_resolved` | `null \| boolean` |  |
| `remove_source_branch_after_merge` | `null \| boolean` |  |
| `printing_merge_request_link_enabled` | `null \| boolean` |  |
| `build_timeout` | `null \| integer` |  |
| `auto_cancel_pending_pipelines` | `null \| string` |  |
| `build_git_strategy` | `null \| string` |  |
| `public_jobs` | `null \| boolean` |  |
| `restrict_user_defined_variables` | `null \| boolean` |  |
| `keep_latest_artifact` | `null \| boolean` |  |
| `runner_token_expiration_interval` | `null \| string` |  |
| `resource_group_default_process_mode` | `null \| string` |  |
| `ci_config_path` | `null \| string` |  |
| `ci_default_git_depth` | `null \| integer` |  |
| `ci_delete_pipelines_in_seconds` | `null \| integer` |  |
| `ci_forward_deployment_enabled` | `null \| boolean` |  |
| `ci_forward_deployment_rollback_allowed` | `null \| boolean` |  |
| `ci_job_token_scope_enabled` | `null \| boolean` |  |
| `ci_separated_caches` | `null \| boolean` |  |
| `ci_allow_fork_pipelines_to_run_in_parent_project` | `null \| boolean` |  |
| `ci_id_token_sub_claim_components` | `null \| array` |  |
| `ci_pipeline_variables_minimum_override_role` | `null \| string` |  |
| `ci_push_repository_for_job_token_allowed` | `null \| boolean` |  |
| `ci_display_pipeline_variables` | `null \| boolean` |  |
| `protect_merge_request_pipelines` | `null \| boolean` |  |
| `suggestion_commit_message` | `null \| string` |  |
| `merge_commit_template` | `null \| string` |  |
| `squash_commit_template` | `null \| string` |  |
| `issue_branch_template` | `null \| string` |  |
| `merge_request_title_regex` | `null \| string` |  |
| `merge_request_title_regex_description` | `null \| string` |  |
| `warn_about_potentially_unwanted_characters` | `null \| boolean` |  |
| `autoclose_referenced_issues` | `null \| boolean` |  |
| `max_artifacts_size` | `null \| integer` |  |
| `external_authorization_classification_label` | `null \| string` |  |
| `requirements_enabled` | `null \| boolean` |  |
| `requirements_access_level` | `null \| string` |  |
| `security_and_compliance_enabled` | `null \| boolean` |  |
| `security_and_compliance_access_level` | `null \| string` |  |
| `compliance_frameworks` | `null \| array` |  |
| `web_based_commit_signing_enabled` | `null \| boolean` |  |
| `permissions` | `null \| object` |  |
| `issues_access_level` | `null \| string` |  |
| `repository_access_level` | `null \| string` |  |
| `merge_requests_access_level` | `null \| string` |  |
| `forking_access_level` | `null \| string` |  |
| `wiki_access_level` | `null \| string` |  |
| `builds_access_level` | `null \| string` |  |
| `snippets_access_level` | `null \| string` |  |
| `pages_access_level` | `null \| string` |  |
| `analytics_access_level` | `null \| string` |  |
| `container_registry_access_level` | `null \| string` |  |
| `releases_access_level` | `null \| string` |  |
| `environments_access_level` | `null \| string` |  |
| `feature_flags_access_level` | `null \| string` |  |
| `infrastructure_access_level` | `null \| string` |  |
| `monitor_access_level` | `null \| string` |  |
| `model_experiments_access_level` | `null \| string` |  |
| `model_registry_access_level` | `null \| string` |  |
| `package_registry_access_level` | `null \| string` |  |


</details>

### Projects Search

Search and filter projects records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.projects.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "projects",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the project |
| `description` | `string` | Description of the project |
| `description_html` | `string` | HTML-rendered description of the project |
| `name` | `string` | Name of the project |
| `name_with_namespace` | `string` | Full name including namespace |
| `path` | `string` | URL path of the project |
| `path_with_namespace` | `string` | Full path including namespace |
| `created_at` | `string` | Timestamp when the project was created |
| `updated_at` | `string` | Timestamp when the project was last updated |
| `default_branch` | `string` | Default branch of the project |
| `tag_list` | `array` | List of tags for the project |
| `topics` | `array` | List of topics for the project |
| `ssh_url_to_repo` | `string` | SSH URL to the repository |
| `http_url_to_repo` | `string` | HTTP URL to the repository |
| `web_url` | `string` | Web URL of the project |
| `readme_url` | `string` | URL to the project README |
| `avatar_url` | `string` | URL of the project avatar |
| `forks_count` | `integer` | Number of forks |
| `star_count` | `integer` | Number of stars |
| `last_activity_at` | `string` | Timestamp of last activity |
| `namespace` | `object` | Namespace the project belongs to |
| `container_registry_image_prefix` | `string` | Prefix for container registry images |
| `_links` | `object` | Related resource links |
| `packages_enabled` | `boolean` | Whether packages are enabled |
| `empty_repo` | `boolean` | Whether the repository is empty |
| `archived` | `boolean` | Whether the project is archived |
| `visibility` | `string` | Visibility level of the project |
| `resolve_outdated_diff_discussions` | `boolean` | Whether outdated diff discussions are auto-resolved |
| `container_registry_enabled` | `boolean` | Whether container registry is enabled |
| `container_expiration_policy` | `object` | Container expiration policy settings |
| `issues_enabled` | `boolean` | Whether issues are enabled |
| `merge_requests_enabled` | `boolean` | Whether merge requests are enabled |
| `wiki_enabled` | `boolean` | Whether wiki is enabled |
| `jobs_enabled` | `boolean` | Whether jobs are enabled |
| `snippets_enabled` | `boolean` | Whether snippets are enabled |
| `service_desk_enabled` | `boolean` | Whether service desk is enabled |
| `service_desk_address` | `string` | Email address for the service desk |
| `can_create_merge_request_in` | `boolean` | Whether user can create merge requests |
| `issues_access_level` | `string` | Access level for issues |
| `repository_access_level` | `string` | Access level for the repository |
| `merge_requests_access_level` | `string` | Access level for merge requests |
| `forking_access_level` | `string` | Access level for forking |
| `wiki_access_level` | `string` | Access level for the wiki |
| `builds_access_level` | `string` | Access level for builds |
| `snippets_access_level` | `string` | Access level for snippets |
| `pages_access_level` | `string` | Access level for pages |
| `operations_access_level` | `string` | Access level for operations |
| `analytics_access_level` | `string` | Access level for analytics |
| `emails_disabled` | `boolean` | Whether emails are disabled |
| `shared_runners_enabled` | `boolean` | Whether shared runners are enabled |
| `lfs_enabled` | `boolean` | Whether Git LFS is enabled |
| `creator_id` | `integer` | ID of the project creator |
| `import_status` | `string` | Import status of the project |
| `open_issues_count` | `integer` | Number of open issues |
| `ci_default_git_depth` | `integer` | Default git depth for CI pipelines |
| `ci_forward_deployment_enabled` | `boolean` | Whether CI forward deployment is enabled |
| `public_jobs` | `boolean` | Whether jobs are public |
| `build_timeout` | `integer` | Build timeout in seconds |
| `auto_cancel_pending_pipelines` | `string` | Auto-cancel pending pipelines setting |
| `ci_config_path` | `string` | Path to the CI configuration file |
| `shared_with_groups` | `array` | Groups the project is shared with |
| `only_allow_merge_if_pipeline_succeeds` | `boolean` | Whether merge requires pipeline success |
| `allow_merge_on_skipped_pipeline` | `boolean` | Whether merge is allowed on skipped pipeline |
| `restrict_user_defined_variables` | `boolean` | Whether user-defined variables are restricted |
| `request_access_enabled` | `boolean` | Whether access requests are enabled |
| `only_allow_merge_if_all_discussions_are_resolved` | `boolean` | Whether merge requires all discussions resolved |
| `remove_source_branch_after_merge` | `boolean` | Whether source branch is removed after merge |
| `printing_merge_request_link_enabled` | `boolean` | Whether MR link printing is enabled |
| `merge_method` | `string` | Merge method used for the project |
| `statistics` | `object` | Project statistics |
| `auto_devops_enabled` | `boolean` | Whether Auto DevOps is enabled |
| `auto_devops_deploy_strategy` | `string` | Auto DevOps deployment strategy |
| `autoclose_referenced_issues` | `boolean` | Whether referenced issues are auto-closed |
| `external_authorization_classification_label` | `string` | External authorization classification label |
| `requirements_enabled` | `boolean` | Whether requirements are enabled |
| `security_and_compliance_enabled` | `boolean` | Whether security and compliance is enabled |
| `compliance_frameworks` | `array` | Compliance frameworks for the project |
| `permissions` | `object` | User permissions for the project |
| `keep_latest_artifact` | `boolean` | Whether the latest artifact is kept |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the project |
| `data[].description` | `string` | Description of the project |
| `data[].description_html` | `string` | HTML-rendered description of the project |
| `data[].name` | `string` | Name of the project |
| `data[].name_with_namespace` | `string` | Full name including namespace |
| `data[].path` | `string` | URL path of the project |
| `data[].path_with_namespace` | `string` | Full path including namespace |
| `data[].created_at` | `string` | Timestamp when the project was created |
| `data[].updated_at` | `string` | Timestamp when the project was last updated |
| `data[].default_branch` | `string` | Default branch of the project |
| `data[].tag_list` | `array` | List of tags for the project |
| `data[].topics` | `array` | List of topics for the project |
| `data[].ssh_url_to_repo` | `string` | SSH URL to the repository |
| `data[].http_url_to_repo` | `string` | HTTP URL to the repository |
| `data[].web_url` | `string` | Web URL of the project |
| `data[].readme_url` | `string` | URL to the project README |
| `data[].avatar_url` | `string` | URL of the project avatar |
| `data[].forks_count` | `integer` | Number of forks |
| `data[].star_count` | `integer` | Number of stars |
| `data[].last_activity_at` | `string` | Timestamp of last activity |
| `data[].namespace` | `object` | Namespace the project belongs to |
| `data[].container_registry_image_prefix` | `string` | Prefix for container registry images |
| `data[]._links` | `object` | Related resource links |
| `data[].packages_enabled` | `boolean` | Whether packages are enabled |
| `data[].empty_repo` | `boolean` | Whether the repository is empty |
| `data[].archived` | `boolean` | Whether the project is archived |
| `data[].visibility` | `string` | Visibility level of the project |
| `data[].resolve_outdated_diff_discussions` | `boolean` | Whether outdated diff discussions are auto-resolved |
| `data[].container_registry_enabled` | `boolean` | Whether container registry is enabled |
| `data[].container_expiration_policy` | `object` | Container expiration policy settings |
| `data[].issues_enabled` | `boolean` | Whether issues are enabled |
| `data[].merge_requests_enabled` | `boolean` | Whether merge requests are enabled |
| `data[].wiki_enabled` | `boolean` | Whether wiki is enabled |
| `data[].jobs_enabled` | `boolean` | Whether jobs are enabled |
| `data[].snippets_enabled` | `boolean` | Whether snippets are enabled |
| `data[].service_desk_enabled` | `boolean` | Whether service desk is enabled |
| `data[].service_desk_address` | `string` | Email address for the service desk |
| `data[].can_create_merge_request_in` | `boolean` | Whether user can create merge requests |
| `data[].issues_access_level` | `string` | Access level for issues |
| `data[].repository_access_level` | `string` | Access level for the repository |
| `data[].merge_requests_access_level` | `string` | Access level for merge requests |
| `data[].forking_access_level` | `string` | Access level for forking |
| `data[].wiki_access_level` | `string` | Access level for the wiki |
| `data[].builds_access_level` | `string` | Access level for builds |
| `data[].snippets_access_level` | `string` | Access level for snippets |
| `data[].pages_access_level` | `string` | Access level for pages |
| `data[].operations_access_level` | `string` | Access level for operations |
| `data[].analytics_access_level` | `string` | Access level for analytics |
| `data[].emails_disabled` | `boolean` | Whether emails are disabled |
| `data[].shared_runners_enabled` | `boolean` | Whether shared runners are enabled |
| `data[].lfs_enabled` | `boolean` | Whether Git LFS is enabled |
| `data[].creator_id` | `integer` | ID of the project creator |
| `data[].import_status` | `string` | Import status of the project |
| `data[].open_issues_count` | `integer` | Number of open issues |
| `data[].ci_default_git_depth` | `integer` | Default git depth for CI pipelines |
| `data[].ci_forward_deployment_enabled` | `boolean` | Whether CI forward deployment is enabled |
| `data[].public_jobs` | `boolean` | Whether jobs are public |
| `data[].build_timeout` | `integer` | Build timeout in seconds |
| `data[].auto_cancel_pending_pipelines` | `string` | Auto-cancel pending pipelines setting |
| `data[].ci_config_path` | `string` | Path to the CI configuration file |
| `data[].shared_with_groups` | `array` | Groups the project is shared with |
| `data[].only_allow_merge_if_pipeline_succeeds` | `boolean` | Whether merge requires pipeline success |
| `data[].allow_merge_on_skipped_pipeline` | `boolean` | Whether merge is allowed on skipped pipeline |
| `data[].restrict_user_defined_variables` | `boolean` | Whether user-defined variables are restricted |
| `data[].request_access_enabled` | `boolean` | Whether access requests are enabled |
| `data[].only_allow_merge_if_all_discussions_are_resolved` | `boolean` | Whether merge requires all discussions resolved |
| `data[].remove_source_branch_after_merge` | `boolean` | Whether source branch is removed after merge |
| `data[].printing_merge_request_link_enabled` | `boolean` | Whether MR link printing is enabled |
| `data[].merge_method` | `string` | Merge method used for the project |
| `data[].statistics` | `object` | Project statistics |
| `data[].auto_devops_enabled` | `boolean` | Whether Auto DevOps is enabled |
| `data[].auto_devops_deploy_strategy` | `string` | Auto DevOps deployment strategy |
| `data[].autoclose_referenced_issues` | `boolean` | Whether referenced issues are auto-closed |
| `data[].external_authorization_classification_label` | `string` | External authorization classification label |
| `data[].requirements_enabled` | `boolean` | Whether requirements are enabled |
| `data[].security_and_compliance_enabled` | `boolean` | Whether security and compliance is enabled |
| `data[].compliance_frameworks` | `array` | Compliance frameworks for the project |
| `data[].permissions` | `object` | User permissions for the project |
| `data[].keep_latest_artifact` | `boolean` | Whether the latest artifact is kept |

</details>

## Issues

### Issues List

Get a list of a project's issues.

#### Python SDK

```python
await gitlab.issues.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `state` | `"opened" \| "closed" \| "all"` | No | Filter issues by state |
| `scope` | `"created_by_me" \| "assigned_to_me" \| "all"` | No | Filter issues by scope |
| `order_by` | `"created_at" \| "updated_at" \| "priority" \| "due_date" \| "relative_position" \| "label_priority" \| "milestone_due" \| "popularity" \| "weight"` | No | Return issues ordered by field |
| `sort` | `"asc" \| "desc"` | No | Return issues sorted in asc or desc order |
| `created_after` | `string` | No | Return issues created on or after the given time (ISO 8601 format) |
| `created_before` | `string` | No | Return issues created on or before the given time (ISO 8601 format) |
| `updated_after` | `string` | No | Return issues updated on or after the given time (ISO 8601 format) |
| `updated_before` | `string` | No | Return issues updated on or before the given time (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `project_id` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `closed_at` | `null \| string` |  |
| `labels` | `array<string>` |  |
| `milestone` | `null \| object` |  |
| `author` | `object` |  |
| `assignee` | `null \| object` |  |
| `assignees` | `array<object>` |  |
| `web_url` | `string` |  |
| `due_date` | `null \| string` |  |
| `confidential` | `boolean` |  |
| `weight` | `null \| integer` |  |
| `user_notes_count` | `integer` |  |
| `upvotes` | `integer` |  |
| `downvotes` | `integer` |  |
| `closed_by` | `null \| object` |  |
| `time_stats` | `null \| object` |  |
| `task_completion_status` | `null \| object` |  |
| `references` | `null \| object` |  |
| `_links` | `null \| object` |  |
| `discussion_locked` | `null \| boolean` |  |
| `merge_requests_count` | `null \| integer` |  |
| `blocking_issues_count` | `null \| integer` |  |
| `severity` | `null \| string` |  |
| `type` | `null \| string` |  |
| `issue_type` | `null \| string` |  |
| `has_tasks` | `null \| boolean` |  |
| `task_status` | `null \| string` |  |
| `moved_to_id` | `null \| integer` |  |
| `service_desk_reply_to` | `null \| string` |  |
| `epic_iid` | `null \| integer` |  |
| `epic` | `null \| object` |  |
| `iteration` | `null \| object` |  |
| `health_status` | `null \| string` |  |
| `start_date` | `null \| string` |  |
| `imported` | `null \| boolean` |  |
| `imported_from` | `null \| string` |  |
| `subscribed` | `null \| boolean` |  |


</details>

### Issues Get

Get a single project issue.

#### Python SDK

```python
await gitlab.issues.get(
    project_id="<str>",
    issue_iid=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "issue_iid": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `issue_iid` | `integer` | Yes | The internal ID of a project's issue |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `project_id` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `closed_at` | `null \| string` |  |
| `labels` | `array<string>` |  |
| `milestone` | `null \| object` |  |
| `author` | `object` |  |
| `assignee` | `null \| object` |  |
| `assignees` | `array<object>` |  |
| `web_url` | `string` |  |
| `due_date` | `null \| string` |  |
| `confidential` | `boolean` |  |
| `weight` | `null \| integer` |  |
| `user_notes_count` | `integer` |  |
| `upvotes` | `integer` |  |
| `downvotes` | `integer` |  |
| `closed_by` | `null \| object` |  |
| `time_stats` | `null \| object` |  |
| `task_completion_status` | `null \| object` |  |
| `references` | `null \| object` |  |
| `_links` | `null \| object` |  |
| `discussion_locked` | `null \| boolean` |  |
| `merge_requests_count` | `null \| integer` |  |
| `blocking_issues_count` | `null \| integer` |  |
| `severity` | `null \| string` |  |
| `type` | `null \| string` |  |
| `issue_type` | `null \| string` |  |
| `has_tasks` | `null \| boolean` |  |
| `task_status` | `null \| string` |  |
| `moved_to_id` | `null \| integer` |  |
| `service_desk_reply_to` | `null \| string` |  |
| `epic_iid` | `null \| integer` |  |
| `epic` | `null \| object` |  |
| `iteration` | `null \| object` |  |
| `health_status` | `null \| string` |  |
| `start_date` | `null \| string` |  |
| `imported` | `null \| boolean` |  |
| `imported_from` | `null \| string` |  |
| `subscribed` | `null \| boolean` |  |


</details>

### Issues Search

Search and filter issues records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.issues.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "issues",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the issue |
| `iid` | `integer` | Internal ID of the issue within the project |
| `project_id` | `integer` | ID of the project the issue belongs to |
| `title` | `string` | Title of the issue |
| `description` | `string` | Description of the issue |
| `state` | `string` | State of the issue |
| `created_at` | `string` | Timestamp when the issue was created |
| `updated_at` | `string` | Timestamp when the issue was last updated |
| `closed_at` | `string` | Timestamp when the issue was closed |
| `labels` | `array` | Labels assigned to the issue |
| `assignees` | `array` | Users assigned to the issue |
| `type` | `string` | Type of the issue |
| `user_notes_count` | `integer` | Number of user notes on the issue |
| `merge_requests_count` | `integer` | Number of related merge requests |
| `upvotes` | `integer` | Number of upvotes |
| `downvotes` | `integer` | Number of downvotes |
| `due_date` | `string` | Due date for the issue |
| `confidential` | `boolean` | Whether the issue is confidential |
| `discussion_locked` | `boolean` | Whether discussion is locked |
| `issue_type` | `string` | Type classification of the issue |
| `web_url` | `string` | Web URL of the issue |
| `time_stats` | `object` | Time tracking statistics |
| `task_completion_status` | `object` | Task completion status |
| `blocking_issues_count` | `integer` | Number of blocking issues |
| `has_tasks` | `boolean` | Whether the issue has tasks |
| `_links` | `object` | Related resource links |
| `references` | `object` | Issue references |
| `author` | `object` | Author of the issue |
| `author_id` | `integer` | ID of the author |
| `assignee` | `object` | Primary assignee of the issue |
| `assignee_id` | `integer` | ID of the primary assignee |
| `closed_by` | `object` | User who closed the issue |
| `closed_by_id` | `integer` | ID of the user who closed the issue |
| `milestone` | `object` | Milestone the issue belongs to |
| `milestone_id` | `integer` | ID of the milestone |
| `weight` | `integer` | Weight of the issue |
| `severity` | `string` | Severity level of the issue |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the issue |
| `data[].iid` | `integer` | Internal ID of the issue within the project |
| `data[].project_id` | `integer` | ID of the project the issue belongs to |
| `data[].title` | `string` | Title of the issue |
| `data[].description` | `string` | Description of the issue |
| `data[].state` | `string` | State of the issue |
| `data[].created_at` | `string` | Timestamp when the issue was created |
| `data[].updated_at` | `string` | Timestamp when the issue was last updated |
| `data[].closed_at` | `string` | Timestamp when the issue was closed |
| `data[].labels` | `array` | Labels assigned to the issue |
| `data[].assignees` | `array` | Users assigned to the issue |
| `data[].type` | `string` | Type of the issue |
| `data[].user_notes_count` | `integer` | Number of user notes on the issue |
| `data[].merge_requests_count` | `integer` | Number of related merge requests |
| `data[].upvotes` | `integer` | Number of upvotes |
| `data[].downvotes` | `integer` | Number of downvotes |
| `data[].due_date` | `string` | Due date for the issue |
| `data[].confidential` | `boolean` | Whether the issue is confidential |
| `data[].discussion_locked` | `boolean` | Whether discussion is locked |
| `data[].issue_type` | `string` | Type classification of the issue |
| `data[].web_url` | `string` | Web URL of the issue |
| `data[].time_stats` | `object` | Time tracking statistics |
| `data[].task_completion_status` | `object` | Task completion status |
| `data[].blocking_issues_count` | `integer` | Number of blocking issues |
| `data[].has_tasks` | `boolean` | Whether the issue has tasks |
| `data[]._links` | `object` | Related resource links |
| `data[].references` | `object` | Issue references |
| `data[].author` | `object` | Author of the issue |
| `data[].author_id` | `integer` | ID of the author |
| `data[].assignee` | `object` | Primary assignee of the issue |
| `data[].assignee_id` | `integer` | ID of the primary assignee |
| `data[].closed_by` | `object` | User who closed the issue |
| `data[].closed_by_id` | `integer` | ID of the user who closed the issue |
| `data[].milestone` | `object` | Milestone the issue belongs to |
| `data[].milestone_id` | `integer` | ID of the milestone |
| `data[].weight` | `integer` | Weight of the issue |
| `data[].severity` | `string` | Severity level of the issue |

</details>

## Merge Requests

### Merge Requests List

Get all merge requests for a project.

#### Python SDK

```python
await gitlab.merge_requests.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "merge_requests",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `state` | `"opened" \| "closed" \| "locked" \| "merged" \| "all"` | No | Filter merge requests by state |
| `scope` | `"created_by_me" \| "assigned_to_me" \| "all"` | No | Filter merge requests by scope |
| `order_by` | `"created_at" \| "title" \| "updated_at"` | No | Return merge requests ordered by field |
| `sort` | `"asc" \| "desc"` | No | Return merge requests sorted in asc or desc order |
| `created_after` | `string` | No | Return merge requests created on or after the given time (ISO 8601 format) |
| `created_before` | `string` | No | Return merge requests created on or before the given time (ISO 8601 format) |
| `updated_after` | `string` | No | Return merge requests updated on or after the given time (ISO 8601 format) |
| `updated_before` | `string` | No | Return merge requests updated on or before the given time (ISO 8601 format) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `project_id` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `merged_at` | `null \| string` |  |
| `closed_at` | `null \| string` |  |
| `source_branch` | `string` |  |
| `target_branch` | `string` |  |
| `author` | `object` |  |
| `assignee` | `null \| object` |  |
| `assignees` | `array<object>` |  |
| `labels` | `array<string>` |  |
| `milestone` | `null \| object` |  |
| `web_url` | `string` |  |
| `merge_status` | `string` |  |
| `draft` | `null \| boolean` |  |
| `user_notes_count` | `integer` |  |
| `upvotes` | `integer` |  |
| `downvotes` | `integer` |  |
| `sha` | `null \| string` |  |
| `merged_by` | `null \| object` |  |
| `merge_user` | `null \| object` |  |
| `closed_by` | `null \| object` |  |
| `reviewers` | `null \| array` |  |
| `source_project_id` | `null \| integer` |  |
| `target_project_id` | `null \| integer` |  |
| `work_in_progress` | `null \| boolean` |  |
| `merge_when_pipeline_succeeds` | `null \| boolean` |  |
| `detailed_merge_status` | `null \| string` |  |
| `merge_after` | `null \| string` |  |
| `merge_commit_sha` | `null \| string` |  |
| `squash_commit_sha` | `null \| string` |  |
| `discussion_locked` | `null \| boolean` |  |
| `should_remove_source_branch` | `null \| boolean` |  |
| `force_remove_source_branch` | `null \| boolean` |  |
| `prepared_at` | `null \| string` |  |
| `reference` | `null \| string` |  |
| `references` | `null \| object` |  |
| `time_stats` | `null \| object` |  |
| `squash` | `null \| boolean` |  |
| `squash_on_merge` | `null \| boolean` |  |
| `task_completion_status` | `null \| object` |  |
| `has_conflicts` | `null \| boolean` |  |
| `blocking_discussions_resolved` | `null \| boolean` |  |
| `approvals_before_merge` | `null \| integer` |  |
| `imported` | `null \| boolean` |  |
| `imported_from` | `null \| string` |  |
| `subscribed` | `null \| boolean` |  |
| `changes_count` | `null \| string` |  |
| `latest_build_started_at` | `null \| string` |  |
| `latest_build_finished_at` | `null \| string` |  |
| `first_deployed_to_production_at` | `null \| string` |  |
| `pipeline` | `null \| object` |  |
| `head_pipeline` | `null \| object` |  |
| `diff_refs` | `null \| object` |  |
| `merge_error` | `null \| string` |  |
| `first_contribution` | `null \| boolean` |  |
| `user` | `null \| object` |  |


</details>

### Merge Requests Get

Get information about a single merge request.

#### Python SDK

```python
await gitlab.merge_requests.get(
    project_id="<str>",
    merge_request_iid=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "merge_requests",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "merge_request_iid": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `merge_request_iid` | `integer` | Yes | The internal ID of the merge request |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `project_id` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `merged_at` | `null \| string` |  |
| `closed_at` | `null \| string` |  |
| `source_branch` | `string` |  |
| `target_branch` | `string` |  |
| `author` | `object` |  |
| `assignee` | `null \| object` |  |
| `assignees` | `array<object>` |  |
| `labels` | `array<string>` |  |
| `milestone` | `null \| object` |  |
| `web_url` | `string` |  |
| `merge_status` | `string` |  |
| `draft` | `null \| boolean` |  |
| `user_notes_count` | `integer` |  |
| `upvotes` | `integer` |  |
| `downvotes` | `integer` |  |
| `sha` | `null \| string` |  |
| `merged_by` | `null \| object` |  |
| `merge_user` | `null \| object` |  |
| `closed_by` | `null \| object` |  |
| `reviewers` | `null \| array` |  |
| `source_project_id` | `null \| integer` |  |
| `target_project_id` | `null \| integer` |  |
| `work_in_progress` | `null \| boolean` |  |
| `merge_when_pipeline_succeeds` | `null \| boolean` |  |
| `detailed_merge_status` | `null \| string` |  |
| `merge_after` | `null \| string` |  |
| `merge_commit_sha` | `null \| string` |  |
| `squash_commit_sha` | `null \| string` |  |
| `discussion_locked` | `null \| boolean` |  |
| `should_remove_source_branch` | `null \| boolean` |  |
| `force_remove_source_branch` | `null \| boolean` |  |
| `prepared_at` | `null \| string` |  |
| `reference` | `null \| string` |  |
| `references` | `null \| object` |  |
| `time_stats` | `null \| object` |  |
| `squash` | `null \| boolean` |  |
| `squash_on_merge` | `null \| boolean` |  |
| `task_completion_status` | `null \| object` |  |
| `has_conflicts` | `null \| boolean` |  |
| `blocking_discussions_resolved` | `null \| boolean` |  |
| `approvals_before_merge` | `null \| integer` |  |
| `imported` | `null \| boolean` |  |
| `imported_from` | `null \| string` |  |
| `subscribed` | `null \| boolean` |  |
| `changes_count` | `null \| string` |  |
| `latest_build_started_at` | `null \| string` |  |
| `latest_build_finished_at` | `null \| string` |  |
| `first_deployed_to_production_at` | `null \| string` |  |
| `pipeline` | `null \| object` |  |
| `head_pipeline` | `null \| object` |  |
| `diff_refs` | `null \| object` |  |
| `merge_error` | `null \| string` |  |
| `first_contribution` | `null \| boolean` |  |
| `user` | `null \| object` |  |


</details>

### Merge Requests Search

Search and filter merge requests records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.merge_requests.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "merge_requests",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the merge request |
| `iid` | `integer` | Internal ID of the merge request within the project |
| `project_id` | `integer` | ID of the project |
| `title` | `string` | Title of the merge request |
| `description` | `string` | Description of the merge request |
| `state` | `string` | State of the merge request |
| `created_at` | `string` | Timestamp when the merge request was created |
| `updated_at` | `string` | Timestamp when the merge request was last updated |
| `merged_at` | `string` | Timestamp when the merge request was merged |
| `closed_at` | `string` | Timestamp when the merge request was closed |
| `target_branch` | `string` | Target branch for the merge request |
| `source_branch` | `string` | Source branch for the merge request |
| `user_notes_count` | `integer` | Number of user notes |
| `upvotes` | `integer` | Number of upvotes |
| `downvotes` | `integer` | Number of downvotes |
| `assignees` | `array` | Users assigned to the merge request |
| `reviewers` | `array` | Users assigned as reviewers |
| `source_project_id` | `integer` | ID of the source project |
| `target_project_id` | `integer` | ID of the target project |
| `labels` | `array` | Labels assigned to the merge request |
| `work_in_progress` | `boolean` | Whether the merge request is a work in progress |
| `merge_when_pipeline_succeeds` | `boolean` | Whether to merge when pipeline succeeds |
| `merge_status` | `string` | Merge status of the merge request |
| `sha` | `string` | SHA of the head commit |
| `merge_commit_sha` | `string` | SHA of the merge commit |
| `squash_commit_sha` | `string` | SHA of the squash commit |
| `discussion_locked` | `boolean` | Whether discussion is locked |
| `should_remove_source_branch` | `boolean` | Whether source branch should be removed |
| `force_remove_source_branch` | `boolean` | Whether to force remove source branch |
| `reference` | `string` | Short reference for the merge request |
| `references` | `object` | Merge request references |
| `web_url` | `string` | Web URL of the merge request |
| `time_stats` | `object` | Time tracking statistics |
| `squash` | `boolean` | Whether to squash commits on merge |
| `task_completion_status` | `object` | Task completion status |
| `has_conflicts` | `boolean` | Whether the merge request has conflicts |
| `blocking_discussions_resolved` | `boolean` | Whether blocking discussions are resolved |
| `author` | `object` | Author of the merge request |
| `author_id` | `integer` | ID of the author |
| `assignee` | `object` | Primary assignee of the merge request |
| `assignee_id` | `integer` | ID of the primary assignee |
| `closed_by` | `object` | User who closed the merge request |
| `closed_by_id` | `integer` | ID of the user who closed it |
| `milestone` | `object` | Milestone the merge request belongs to |
| `milestone_id` | `integer` | ID of the milestone |
| `merged_by` | `object` | User who merged the merge request |
| `merged_by_id` | `integer` | ID of the user who merged it |
| `draft` | `boolean` | Whether the merge request is a draft |
| `detailed_merge_status` | `string` | Detailed merge status |
| `merge_user` | `object` | User who performed the merge |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the merge request |
| `data[].iid` | `integer` | Internal ID of the merge request within the project |
| `data[].project_id` | `integer` | ID of the project |
| `data[].title` | `string` | Title of the merge request |
| `data[].description` | `string` | Description of the merge request |
| `data[].state` | `string` | State of the merge request |
| `data[].created_at` | `string` | Timestamp when the merge request was created |
| `data[].updated_at` | `string` | Timestamp when the merge request was last updated |
| `data[].merged_at` | `string` | Timestamp when the merge request was merged |
| `data[].closed_at` | `string` | Timestamp when the merge request was closed |
| `data[].target_branch` | `string` | Target branch for the merge request |
| `data[].source_branch` | `string` | Source branch for the merge request |
| `data[].user_notes_count` | `integer` | Number of user notes |
| `data[].upvotes` | `integer` | Number of upvotes |
| `data[].downvotes` | `integer` | Number of downvotes |
| `data[].assignees` | `array` | Users assigned to the merge request |
| `data[].reviewers` | `array` | Users assigned as reviewers |
| `data[].source_project_id` | `integer` | ID of the source project |
| `data[].target_project_id` | `integer` | ID of the target project |
| `data[].labels` | `array` | Labels assigned to the merge request |
| `data[].work_in_progress` | `boolean` | Whether the merge request is a work in progress |
| `data[].merge_when_pipeline_succeeds` | `boolean` | Whether to merge when pipeline succeeds |
| `data[].merge_status` | `string` | Merge status of the merge request |
| `data[].sha` | `string` | SHA of the head commit |
| `data[].merge_commit_sha` | `string` | SHA of the merge commit |
| `data[].squash_commit_sha` | `string` | SHA of the squash commit |
| `data[].discussion_locked` | `boolean` | Whether discussion is locked |
| `data[].should_remove_source_branch` | `boolean` | Whether source branch should be removed |
| `data[].force_remove_source_branch` | `boolean` | Whether to force remove source branch |
| `data[].reference` | `string` | Short reference for the merge request |
| `data[].references` | `object` | Merge request references |
| `data[].web_url` | `string` | Web URL of the merge request |
| `data[].time_stats` | `object` | Time tracking statistics |
| `data[].squash` | `boolean` | Whether to squash commits on merge |
| `data[].task_completion_status` | `object` | Task completion status |
| `data[].has_conflicts` | `boolean` | Whether the merge request has conflicts |
| `data[].blocking_discussions_resolved` | `boolean` | Whether blocking discussions are resolved |
| `data[].author` | `object` | Author of the merge request |
| `data[].author_id` | `integer` | ID of the author |
| `data[].assignee` | `object` | Primary assignee of the merge request |
| `data[].assignee_id` | `integer` | ID of the primary assignee |
| `data[].closed_by` | `object` | User who closed the merge request |
| `data[].closed_by_id` | `integer` | ID of the user who closed it |
| `data[].milestone` | `object` | Milestone the merge request belongs to |
| `data[].milestone_id` | `integer` | ID of the milestone |
| `data[].merged_by` | `object` | User who merged the merge request |
| `data[].merged_by_id` | `integer` | ID of the user who merged it |
| `data[].draft` | `boolean` | Whether the merge request is a draft |
| `data[].detailed_merge_status` | `string` | Detailed merge status |
| `data[].merge_user` | `object` | User who performed the merge |

</details>

## Users

### Users List

Get a list of users.

#### Python SDK

```python
await gitlab.users.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `search` | `string` | No | Search for users by name, username, or email |
| `active` | `boolean` | No | Filter users by active state |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `name` | `string` |  |
| `state` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `web_url` | `string` |  |
| `locked` | `null \| boolean` |  |
| `public_email` | `null \| string` |  |


</details>

### Users Get

Get a single user by ID.

#### Python SDK

```python
await gitlab.users.get(
    id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "get",
    "params": {
        "id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `integer` | Yes | The ID of the user |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `name` | `string` |  |
| `state` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `web_url` | `string` |  |
| `locked` | `null \| boolean` |  |
| `public_email` | `null \| string` |  |


</details>

### Users Search

Search and filter users records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.users.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "users",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the user |
| `name` | `string` | Full name of the user |
| `username` | `string` | Username of the user |
| `state` | `string` | State of the user account |
| `avatar_url` | `string` | URL of the user avatar |
| `web_url` | `string` | Web URL of the user profile |
| `locked` | `boolean` | Whether the user account is locked |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the user |
| `data[].name` | `string` | Full name of the user |
| `data[].username` | `string` | Username of the user |
| `data[].state` | `string` | State of the user account |
| `data[].avatar_url` | `string` | URL of the user avatar |
| `data[].web_url` | `string` | Web URL of the user profile |
| `data[].locked` | `boolean` | Whether the user account is locked |

</details>

## Commits

### Commits List

Get a list of repository commits in a project.

#### Python SDK

```python
await gitlab.commits.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `ref_name` | `string` | No | The name of a repository branch, tag, or revision range |
| `since` | `string` | No | Only commits after or on this date (ISO 8601) |
| `until` | `string` | No | Only commits before or on this date (ISO 8601) |
| `with_stats` | `boolean` | No | Include stats about each commit |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `short_id` | `string` |  |
| `title` | `string` |  |
| `message` | `string` |  |
| `author_name` | `string` |  |
| `author_email` | `string` |  |
| `authored_date` | `string` |  |
| `committer_name` | `string` |  |
| `committer_email` | `string` |  |
| `committed_date` | `string` |  |
| `created_at` | `string` |  |
| `parent_ids` | `array<string>` |  |
| `web_url` | `string` |  |
| `stats` | `null \| object` |  |
| `trailers` | `null \| object` |  |
| `extended_trailers` | `null \| object` |  |


</details>

### Commits Get

Get a specific commit identified by the commit hash or name of a branch or tag.

#### Python SDK

```python
await gitlab.commits.get(
    project_id="<str>",
    sha="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "sha": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `sha` | `string` | Yes | The commit hash or name of a repository branch or tag |
| `stats` | `boolean` | No | Include commit stats |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `string` |  |
| `short_id` | `string` |  |
| `title` | `string` |  |
| `message` | `string` |  |
| `author_name` | `string` |  |
| `author_email` | `string` |  |
| `authored_date` | `string` |  |
| `committer_name` | `string` |  |
| `committer_email` | `string` |  |
| `committed_date` | `string` |  |
| `created_at` | `string` |  |
| `parent_ids` | `array<string>` |  |
| `web_url` | `string` |  |
| `stats` | `null \| object` |  |
| `trailers` | `null \| object` |  |
| `extended_trailers` | `null \| object` |  |


</details>

### Commits Search

Search and filter commits records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.commits.search(
    query={"filter": {"eq": {"project_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "commits",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"project_id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `project_id` | `integer` | ID of the project the commit belongs to |
| `id` | `string` | SHA of the commit |
| `short_id` | `string` | Short SHA of the commit |
| `created_at` | `string` | Timestamp when the commit was created |
| `parent_ids` | `array` | SHAs of parent commits |
| `title` | `string` | Title of the commit |
| `message` | `string` | Full commit message |
| `author_name` | `string` | Name of the commit author |
| `author_email` | `string` | Email of the commit author |
| `authored_date` | `string` | Date the commit was authored |
| `committer_name` | `string` | Name of the committer |
| `committer_email` | `string` | Email of the committer |
| `committed_date` | `string` | Date the commit was committed |
| `trailers` | `object` | Git trailers for the commit |
| `web_url` | `string` | Web URL of the commit |
| `stats` | `object` | Commit statistics |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].project_id` | `integer` | ID of the project the commit belongs to |
| `data[].id` | `string` | SHA of the commit |
| `data[].short_id` | `string` | Short SHA of the commit |
| `data[].created_at` | `string` | Timestamp when the commit was created |
| `data[].parent_ids` | `array` | SHAs of parent commits |
| `data[].title` | `string` | Title of the commit |
| `data[].message` | `string` | Full commit message |
| `data[].author_name` | `string` | Name of the commit author |
| `data[].author_email` | `string` | Email of the commit author |
| `data[].authored_date` | `string` | Date the commit was authored |
| `data[].committer_name` | `string` | Name of the committer |
| `data[].committer_email` | `string` | Email of the committer |
| `data[].committed_date` | `string` | Date the commit was committed |
| `data[].trailers` | `object` | Git trailers for the commit |
| `data[].web_url` | `string` | Web URL of the commit |
| `data[].stats` | `object` | Commit statistics |

</details>

## Groups

### Groups List

Get a list of visible groups for the authenticated user.

#### Python SDK

```python
await gitlab.groups.list()
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
    "action": "list"
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `search` | `string` | No | Search for groups by name or path |
| `owned` | `boolean` | No | Limit to groups explicitly owned by the current user |
| `order_by` | `"name" \| "path" \| "id"` | No | Order groups by field |
| `sort` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `path` | `string` |  |
| `full_name` | `string` |  |
| `full_path` | `string` |  |
| `description` | `null \| string` |  |
| `visibility` | `string` |  |
| `web_url` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `created_at` | `string` |  |
| `parent_id` | `null \| integer` |  |
| `organization_id` | `null \| integer` |  |
| `default_branch` | `null \| string` |  |
| `default_branch_protection` | `null \| integer` |  |
| `default_branch_protection_defaults` | `null \| object` |  |
| `share_with_group_lock` | `null \| boolean` |  |
| `require_two_factor_authentication` | `null \| boolean` |  |
| `two_factor_grace_period` | `null \| integer` |  |
| `project_creation_level` | `null \| string` |  |
| `auto_devops_enabled` | `null \| boolean` |  |
| `subgroup_creation_level` | `null \| string` |  |
| `emails_disabled` | `null \| boolean` |  |
| `emails_enabled` | `null \| boolean` |  |
| `mentions_disabled` | `null \| boolean` |  |
| `lfs_enabled` | `null \| boolean` |  |
| `request_access_enabled` | `null \| boolean` |  |
| `shared_runners_setting` | `null \| string` |  |
| `ldap_cn` | `null \| string` |  |
| `ldap_access` | `null \| string` |  |
| `wiki_access_level` | `null \| string` |  |
| `marked_for_deletion_on` | `null \| string` |  |
| `archived` | `null \| boolean` |  |
| `math_rendering_limits_enabled` | `null \| boolean` |  |
| `lock_math_rendering_limits_enabled` | `null \| boolean` |  |
| `max_artifacts_size` | `null \| integer` |  |
| `show_diff_preview_in_email` | `null \| boolean` |  |
| `web_based_commit_signing_enabled` | `null \| boolean` |  |
| `duo_namespace_access_rules` | `null \| array` |  |
| `shared_with_groups` | `null \| array` |  |
| `runners_token` | `null \| string` |  |
| `enabled_git_access_protocol` | `null \| string` |  |
| `prevent_sharing_groups_outside_hierarchy` | `null \| boolean` |  |
| `projects` | `null \| array` |  |
| `shared_projects` | `null \| array` |  |
| `shared_runners_minutes_limit` | `null \| integer` |  |
| `extra_shared_runners_minutes_limit` | `null \| integer` |  |
| `prevent_forking_outside_group` | `null \| boolean` |  |
| `membership_lock` | `null \| boolean` |  |
| `ip_restriction_ranges` | `null \| string` |  |
| `service_access_tokens_expiration_enforced` | `null \| boolean` |  |


</details>

### Groups Get

Get all details of a group.

#### Python SDK

```python
await gitlab.groups.get(
    id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
    "action": "get",
    "params": {
        "id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `id` | `string` | Yes | The ID or URL-encoded path of the group |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `name` | `string` |  |
| `path` | `string` |  |
| `full_name` | `string` |  |
| `full_path` | `string` |  |
| `description` | `null \| string` |  |
| `visibility` | `string` |  |
| `web_url` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `created_at` | `string` |  |
| `parent_id` | `null \| integer` |  |
| `organization_id` | `null \| integer` |  |
| `default_branch` | `null \| string` |  |
| `default_branch_protection` | `null \| integer` |  |
| `default_branch_protection_defaults` | `null \| object` |  |
| `share_with_group_lock` | `null \| boolean` |  |
| `require_two_factor_authentication` | `null \| boolean` |  |
| `two_factor_grace_period` | `null \| integer` |  |
| `project_creation_level` | `null \| string` |  |
| `auto_devops_enabled` | `null \| boolean` |  |
| `subgroup_creation_level` | `null \| string` |  |
| `emails_disabled` | `null \| boolean` |  |
| `emails_enabled` | `null \| boolean` |  |
| `mentions_disabled` | `null \| boolean` |  |
| `lfs_enabled` | `null \| boolean` |  |
| `request_access_enabled` | `null \| boolean` |  |
| `shared_runners_setting` | `null \| string` |  |
| `ldap_cn` | `null \| string` |  |
| `ldap_access` | `null \| string` |  |
| `wiki_access_level` | `null \| string` |  |
| `marked_for_deletion_on` | `null \| string` |  |
| `archived` | `null \| boolean` |  |
| `math_rendering_limits_enabled` | `null \| boolean` |  |
| `lock_math_rendering_limits_enabled` | `null \| boolean` |  |
| `max_artifacts_size` | `null \| integer` |  |
| `show_diff_preview_in_email` | `null \| boolean` |  |
| `web_based_commit_signing_enabled` | `null \| boolean` |  |
| `duo_namespace_access_rules` | `null \| array` |  |
| `shared_with_groups` | `null \| array` |  |
| `runners_token` | `null \| string` |  |
| `enabled_git_access_protocol` | `null \| string` |  |
| `prevent_sharing_groups_outside_hierarchy` | `null \| boolean` |  |
| `projects` | `null \| array` |  |
| `shared_projects` | `null \| array` |  |
| `shared_runners_minutes_limit` | `null \| integer` |  |
| `extra_shared_runners_minutes_limit` | `null \| integer` |  |
| `prevent_forking_outside_group` | `null \| boolean` |  |
| `membership_lock` | `null \| boolean` |  |
| `ip_restriction_ranges` | `null \| string` |  |
| `service_access_tokens_expiration_enforced` | `null \| boolean` |  |


</details>

### Groups Search

Search and filter groups records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.groups.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "groups",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the group |
| `web_url` | `string` | Web URL of the group |
| `name` | `string` | Name of the group |
| `path` | `string` | URL path of the group |
| `description` | `string` | Description of the group |
| `visibility` | `string` | Visibility level of the group |
| `share_with_group_lock` | `boolean` | Whether sharing with other groups is locked |
| `require_two_factor_authentication` | `boolean` | Whether two-factor authentication is required |
| `two_factor_grace_period` | `integer` | Grace period for two-factor authentication |
| `project_creation_level` | `string` | Level required to create projects |
| `auto_devops_enabled` | `boolean` | Whether Auto DevOps is enabled |
| `subgroup_creation_level` | `string` | Level required to create subgroups |
| `emails_disabled` | `boolean` | Whether emails are disabled |
| `emails_enabled` | `boolean` | Whether emails are enabled |
| `mentions_disabled` | `boolean` | Whether mentions are disabled |
| `lfs_enabled` | `boolean` | Whether Git LFS is enabled |
| `default_branch_protection` | `integer` | Default branch protection level |
| `avatar_url` | `string` | URL of the group avatar |
| `request_access_enabled` | `boolean` | Whether access requests are enabled |
| `full_name` | `string` | Full name of the group |
| `full_path` | `string` | Full path of the group |
| `created_at` | `string` | Timestamp when the group was created |
| `parent_id` | `integer` | ID of the parent group |
| `shared_with_groups` | `array` | Groups this group is shared with |
| `projects` | `array` | Projects in the group |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the group |
| `data[].web_url` | `string` | Web URL of the group |
| `data[].name` | `string` | Name of the group |
| `data[].path` | `string` | URL path of the group |
| `data[].description` | `string` | Description of the group |
| `data[].visibility` | `string` | Visibility level of the group |
| `data[].share_with_group_lock` | `boolean` | Whether sharing with other groups is locked |
| `data[].require_two_factor_authentication` | `boolean` | Whether two-factor authentication is required |
| `data[].two_factor_grace_period` | `integer` | Grace period for two-factor authentication |
| `data[].project_creation_level` | `string` | Level required to create projects |
| `data[].auto_devops_enabled` | `boolean` | Whether Auto DevOps is enabled |
| `data[].subgroup_creation_level` | `string` | Level required to create subgroups |
| `data[].emails_disabled` | `boolean` | Whether emails are disabled |
| `data[].emails_enabled` | `boolean` | Whether emails are enabled |
| `data[].mentions_disabled` | `boolean` | Whether mentions are disabled |
| `data[].lfs_enabled` | `boolean` | Whether Git LFS is enabled |
| `data[].default_branch_protection` | `integer` | Default branch protection level |
| `data[].avatar_url` | `string` | URL of the group avatar |
| `data[].request_access_enabled` | `boolean` | Whether access requests are enabled |
| `data[].full_name` | `string` | Full name of the group |
| `data[].full_path` | `string` | Full path of the group |
| `data[].created_at` | `string` | Timestamp when the group was created |
| `data[].parent_id` | `integer` | ID of the parent group |
| `data[].shared_with_groups` | `array` | Groups this group is shared with |
| `data[].projects` | `array` | Projects in the group |

</details>

## Branches

### Branches List

Get a list of repository branches from a project.

#### Python SDK

```python
await gitlab.branches.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `search` | `string` | No | Return list of branches containing the search string |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `merged` | `boolean` |  |
| `protected` | `boolean` |  |
| `default` | `boolean` |  |
| `developers_can_push` | `boolean` |  |
| `developers_can_merge` | `boolean` |  |
| `can_push` | `boolean` |  |
| `web_url` | `string` |  |
| `commit` | `null \| object` |  |


</details>

### Branches Get

Get a single project repository branch.

#### Python SDK

```python
await gitlab.branches.get(
    project_id="<str>",
    branch="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "branch": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `branch` | `string` | Yes | The name of the branch (URL-encoded if it contains special characters) |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `merged` | `boolean` |  |
| `protected` | `boolean` |  |
| `default` | `boolean` |  |
| `developers_can_push` | `boolean` |  |
| `developers_can_merge` | `boolean` |  |
| `can_push` | `boolean` |  |
| `web_url` | `string` |  |
| `commit` | `null \| object` |  |


</details>

### Branches Search

Search and filter branches records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.branches.search(
    query={"filter": {"eq": {"project_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "branches",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"project_id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `project_id` | `integer` | ID of the project the branch belongs to |
| `name` | `string` | Name of the branch |
| `merged` | `boolean` | Whether the branch is merged |
| `protected` | `boolean` | Whether the branch is protected |
| `developers_can_push` | `boolean` | Whether developers can push to the branch |
| `developers_can_merge` | `boolean` | Whether developers can merge into the branch |
| `can_push` | `boolean` | Whether the current user can push |
| `default` | `boolean` | Whether this is the default branch |
| `web_url` | `string` | Web URL of the branch |
| `commit_id` | `string` | SHA of the head commit |
| `commit` | `object` | Head commit details |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].project_id` | `integer` | ID of the project the branch belongs to |
| `data[].name` | `string` | Name of the branch |
| `data[].merged` | `boolean` | Whether the branch is merged |
| `data[].protected` | `boolean` | Whether the branch is protected |
| `data[].developers_can_push` | `boolean` | Whether developers can push to the branch |
| `data[].developers_can_merge` | `boolean` | Whether developers can merge into the branch |
| `data[].can_push` | `boolean` | Whether the current user can push |
| `data[].default` | `boolean` | Whether this is the default branch |
| `data[].web_url` | `string` | Web URL of the branch |
| `data[].commit_id` | `string` | SHA of the head commit |
| `data[].commit` | `object` | Head commit details |

</details>

## Pipelines

### Pipelines List

List pipelines in a project.

#### Python SDK

```python
await gitlab.pipelines.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pipelines",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `status` | `"created" \| "waiting_for_resource" \| "preparing" \| "pending" \| "running" \| "success" \| "failed" \| "canceled" \| "skipped" \| "manual" \| "scheduled"` | No | Filter pipelines by status |
| `ref` | `string` | No | Filter pipelines by ref |
| `order_by` | `"id" \| "status" \| "ref" \| "updated_at" \| "user_id"` | No | Order pipelines by field |
| `sort` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `project_id` | `integer` |  |
| `status` | `string` |  |
| `ref` | `string` |  |
| `sha` | `string` |  |
| `source` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `web_url` | `string` |  |
| `name` | `null \| string` |  |


</details>

### Pipelines Get

Get one pipeline of a project.

#### Python SDK

```python
await gitlab.pipelines.get(
    project_id="<str>",
    pipeline_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pipelines",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "pipeline_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `pipeline_id` | `integer` | Yes | The ID of the pipeline |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `project_id` | `integer` |  |
| `status` | `string` |  |
| `ref` | `string` |  |
| `sha` | `string` |  |
| `source` | `string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `web_url` | `string` |  |
| `name` | `null \| string` |  |


</details>

### Pipelines Search

Search and filter pipelines records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.pipelines.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "pipelines",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the pipeline |
| `iid` | `integer` | Internal ID of the pipeline within the project |
| `project_id` | `integer` | ID of the project |
| `sha` | `string` | SHA of the commit that triggered the pipeline |
| `source` | `string` | Source that triggered the pipeline |
| `ref` | `string` | Branch or tag that triggered the pipeline |
| `status` | `string` | Status of the pipeline |
| `created_at` | `string` | Timestamp when the pipeline was created |
| `updated_at` | `string` | Timestamp when the pipeline was last updated |
| `web_url` | `string` | Web URL of the pipeline |
| `name` | `string` | Name of the pipeline |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the pipeline |
| `data[].iid` | `integer` | Internal ID of the pipeline within the project |
| `data[].project_id` | `integer` | ID of the project |
| `data[].sha` | `string` | SHA of the commit that triggered the pipeline |
| `data[].source` | `string` | Source that triggered the pipeline |
| `data[].ref` | `string` | Branch or tag that triggered the pipeline |
| `data[].status` | `string` | Status of the pipeline |
| `data[].created_at` | `string` | Timestamp when the pipeline was created |
| `data[].updated_at` | `string` | Timestamp when the pipeline was last updated |
| `data[].web_url` | `string` | Web URL of the pipeline |
| `data[].name` | `string` | Name of the pipeline |

</details>

## Group Members

### Group Members List

Gets a list of group members viewable by the authenticated user.

#### Python SDK

```python
await gitlab.group_members.list(
    group_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_members",
    "action": "list",
    "params": {
        "group_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `group_id` | `string` | Yes | The ID or URL-encoded path of the group |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `query` | `string` | No | Filter members by name or username |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `name` | `string` |  |
| `state` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `web_url` | `string` |  |
| `access_level` | `integer` |  |
| `expires_at` | `null \| string` |  |
| `created_at` | `string` |  |
| `locked` | `null \| boolean` |  |
| `membership_state` | `null \| string` |  |
| `public_email` | `null \| string` |  |
| `created_by` | `null \| object` |  |


</details>

### Group Members Get

Get a member of a group.

#### Python SDK

```python
await gitlab.group_members.get(
    group_id="<str>",
    user_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_members",
    "action": "get",
    "params": {
        "group_id": "<str>",
        "user_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `group_id` | `string` | Yes | The ID or URL-encoded path of the group |
| `user_id` | `integer` | Yes | The user ID of the member |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `name` | `string` |  |
| `state` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `web_url` | `string` |  |
| `access_level` | `integer` |  |
| `expires_at` | `null \| string` |  |
| `created_at` | `string` |  |
| `locked` | `null \| boolean` |  |
| `membership_state` | `null \| string` |  |
| `public_email` | `null \| string` |  |
| `created_by` | `null \| object` |  |


</details>

### Group Members Search

Search and filter group members records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.group_members.search(
    query={"filter": {"eq": {"group_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_members",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"group_id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `group_id` | `integer` | ID of the group |
| `id` | `integer` | ID of the member |
| `name` | `string` | Full name of the member |
| `username` | `string` | Username of the member |
| `state` | `string` | State of the member account |
| `membership_state` | `string` | State of the membership |
| `avatar_url` | `string` | URL of the member avatar |
| `web_url` | `string` | Web URL of the member profile |
| `access_level` | `integer` | Access level of the member |
| `created_at` | `string` | Timestamp when the member was added |
| `expires_at` | `string` | Expiration date of the membership |
| `created_by` | `object` | User who added the member |
| `locked` | `boolean` | Whether the member account is locked |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].group_id` | `integer` | ID of the group |
| `data[].id` | `integer` | ID of the member |
| `data[].name` | `string` | Full name of the member |
| `data[].username` | `string` | Username of the member |
| `data[].state` | `string` | State of the member account |
| `data[].membership_state` | `string` | State of the membership |
| `data[].avatar_url` | `string` | URL of the member avatar |
| `data[].web_url` | `string` | Web URL of the member profile |
| `data[].access_level` | `integer` | Access level of the member |
| `data[].created_at` | `string` | Timestamp when the member was added |
| `data[].expires_at` | `string` | Expiration date of the membership |
| `data[].created_by` | `object` | User who added the member |
| `data[].locked` | `boolean` | Whether the member account is locked |

</details>

## Project Members

### Project Members List

Gets a list of project members viewable by the authenticated user.

#### Python SDK

```python
await gitlab.project_members.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_members",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `query` | `string` | No | Filter members by name or username |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `name` | `string` |  |
| `state` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `web_url` | `string` |  |
| `access_level` | `integer` |  |
| `expires_at` | `null \| string` |  |
| `created_at` | `string` |  |
| `locked` | `null \| boolean` |  |
| `membership_state` | `null \| string` |  |
| `public_email` | `null \| string` |  |
| `created_by` | `null \| object` |  |


</details>

### Project Members Get

Get a member of a project.

#### Python SDK

```python
await gitlab.project_members.get(
    project_id="<str>",
    user_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_members",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "user_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `user_id` | `integer` | Yes | The user ID of the member |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `username` | `string` |  |
| `name` | `string` |  |
| `state` | `string` |  |
| `avatar_url` | `null \| string` |  |
| `web_url` | `string` |  |
| `access_level` | `integer` |  |
| `expires_at` | `null \| string` |  |
| `created_at` | `string` |  |
| `locked` | `null \| boolean` |  |
| `membership_state` | `null \| string` |  |
| `public_email` | `null \| string` |  |
| `created_by` | `null \| object` |  |


</details>

### Project Members Search

Search and filter project members records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.project_members.search(
    query={"filter": {"eq": {"project_id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_members",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"project_id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `project_id` | `integer` | ID of the project |
| `id` | `integer` | ID of the member |
| `name` | `string` | Full name of the member |
| `username` | `string` | Username of the member |
| `state` | `string` | State of the member account |
| `membership_state` | `string` | State of the membership |
| `avatar_url` | `string` | URL of the member avatar |
| `web_url` | `string` | Web URL of the member profile |
| `access_level` | `integer` | Access level of the member |
| `created_at` | `string` | Timestamp when the member was added |
| `expires_at` | `string` | Expiration date of the membership |
| `created_by` | `object` | User who added the member |
| `locked` | `boolean` | Whether the member account is locked |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].project_id` | `integer` | ID of the project |
| `data[].id` | `integer` | ID of the member |
| `data[].name` | `string` | Full name of the member |
| `data[].username` | `string` | Username of the member |
| `data[].state` | `string` | State of the member account |
| `data[].membership_state` | `string` | State of the membership |
| `data[].avatar_url` | `string` | URL of the member avatar |
| `data[].web_url` | `string` | Web URL of the member profile |
| `data[].access_level` | `integer` | Access level of the member |
| `data[].created_at` | `string` | Timestamp when the member was added |
| `data[].expires_at` | `string` | Expiration date of the membership |
| `data[].created_by` | `object` | User who added the member |
| `data[].locked` | `boolean` | Whether the member account is locked |

</details>

## Releases

### Releases List

Paginated list of releases for a given project, sorted by released_at.

#### Python SDK

```python
await gitlab.releases.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `order_by` | `"released_at" \| "created_at"` | No | Order by field |
| `sort` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `tag_name` | `string` |  |
| `description` | `null \| string` |  |
| `created_at` | `string` |  |
| `released_at` | `string` |  |
| `author` | `object` |  |
| `commit` | `object` |  |
| `upcoming_release` | `boolean` |  |
| `_links` | `object` |  |
| `assets` | `null \| object` |  |
| `milestones` | `null \| array` |  |
| `evidences` | `null \| array` |  |
| `commit_path` | `null \| string` |  |
| `tag_path` | `null \| string` |  |


</details>

### Releases Get

Get a release for the given tag.

#### Python SDK

```python
await gitlab.releases.get(
    project_id="<str>",
    tag_name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "tag_name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `tag_name` | `string` | Yes | The Git tag the release is associated with |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `tag_name` | `string` |  |
| `description` | `null \| string` |  |
| `created_at` | `string` |  |
| `released_at` | `string` |  |
| `author` | `object` |  |
| `commit` | `object` |  |
| `upcoming_release` | `boolean` |  |
| `_links` | `object` |  |
| `assets` | `null \| object` |  |
| `milestones` | `null \| array` |  |
| `evidences` | `null \| array` |  |
| `commit_path` | `null \| string` |  |
| `tag_path` | `null \| string` |  |


</details>

### Releases Search

Search and filter releases records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.releases.search(
    query={"filter": {"eq": {"name": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "releases",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"name": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` | Name of the release |
| `tag_name` | `string` | Tag name associated with the release |
| `description` | `string` | Description of the release |
| `created_at` | `string` | Timestamp when the release was created |
| `released_at` | `string` | Timestamp when the release was published |
| `upcoming_release` | `boolean` | Whether this is an upcoming release |
| `milestones` | `array` | Milestones associated with the release |
| `commit_path` | `string` | Path to the release commit |
| `tag_path` | `string` | Path to the release tag |
| `assets` | `object` | Assets attached to the release |
| `evidences` | `array` | Evidences collected for the release |
| `_links` | `object` | Related resource links |
| `author` | `object` | Author of the release |
| `author_id` | `integer` | ID of the author |
| `commit` | `object` | Commit associated with the release |
| `commit_id` | `string` | SHA of the associated commit |
| `project_id` | `integer` | ID of the project |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].name` | `string` | Name of the release |
| `data[].tag_name` | `string` | Tag name associated with the release |
| `data[].description` | `string` | Description of the release |
| `data[].created_at` | `string` | Timestamp when the release was created |
| `data[].released_at` | `string` | Timestamp when the release was published |
| `data[].upcoming_release` | `boolean` | Whether this is an upcoming release |
| `data[].milestones` | `array` | Milestones associated with the release |
| `data[].commit_path` | `string` | Path to the release commit |
| `data[].tag_path` | `string` | Path to the release tag |
| `data[].assets` | `object` | Assets attached to the release |
| `data[].evidences` | `array` | Evidences collected for the release |
| `data[]._links` | `object` | Related resource links |
| `data[].author` | `object` | Author of the release |
| `data[].author_id` | `integer` | ID of the author |
| `data[].commit` | `object` | Commit associated with the release |
| `data[].commit_id` | `string` | SHA of the associated commit |
| `data[].project_id` | `integer` | ID of the project |

</details>

## Tags

### Tags List

Get a list of repository tags from a project, sorted by update date and time in descending order.

#### Python SDK

```python
await gitlab.tags.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `search` | `string` | No | Return list of tags matching the search criteria |
| `order_by` | `"name" \| "updated" \| "version"` | No | Return tags ordered by field |
| `sort` | `"asc" \| "desc"` | No | Sort order |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `message` | `null \| string` |  |
| `target` | `string` |  |
| `commit` | `object` |  |
| `release` | `null \| object` |  |
| `protected` | `boolean` |  |
| `created_at` | `null \| string` |  |


</details>

### Tags Get

Get a specific repository tag determined by its name.

#### Python SDK

```python
await gitlab.tags.get(
    project_id="<str>",
    tag_name="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "tag_name": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `tag_name` | `string` | Yes | The name of the tag |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` |  |
| `message` | `null \| string` |  |
| `target` | `string` |  |
| `commit` | `object` |  |
| `release` | `null \| object` |  |
| `protected` | `boolean` |  |
| `created_at` | `null \| string` |  |


</details>

### Tags Search

Search and filter tags records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.tags.search(
    query={"filter": {"eq": {"name": "<str>"}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "tags",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"name": "<str>"}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `name` | `string` | Name of the tag |
| `message` | `string` | Annotation message of the tag |
| `target` | `string` | SHA the tag points to |
| `release` | `object` | Release associated with the tag |
| `protected` | `boolean` | Whether the tag is protected |
| `commit` | `object` | Commit the tag points to |
| `commit_id` | `string` | SHA of the tagged commit |
| `project_id` | `integer` | ID of the project |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].name` | `string` | Name of the tag |
| `data[].message` | `string` | Annotation message of the tag |
| `data[].target` | `string` | SHA the tag points to |
| `data[].release` | `object` | Release associated with the tag |
| `data[].protected` | `boolean` | Whether the tag is protected |
| `data[].commit` | `object` | Commit the tag points to |
| `data[].commit_id` | `string` | SHA of the tagged commit |
| `data[].project_id` | `integer` | ID of the project |

</details>

## Group Milestones

### Group Milestones List

Returns a list of group milestones.

#### Python SDK

```python
await gitlab.group_milestones.list(
    group_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_milestones",
    "action": "list",
    "params": {
        "group_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `group_id` | `string` | Yes | The ID or URL-encoded path of the group |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `state` | `"active" \| "closed"` | No | Filter milestones by state |
| `search` | `string` | No | Search for milestones by title or description |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `due_date` | `null \| string` |  |
| `start_date` | `null \| string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `web_url` | `string` |  |
| `expired` | `null \| boolean` |  |
| `group_id` | `null \| integer` |  |
| `project_id` | `null \| integer` |  |


</details>

### Group Milestones Get

Get a single group milestone.

#### Python SDK

```python
await gitlab.group_milestones.get(
    group_id="<str>",
    milestone_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_milestones",
    "action": "get",
    "params": {
        "group_id": "<str>",
        "milestone_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `group_id` | `string` | Yes | The ID or URL-encoded path of the group |
| `milestone_id` | `integer` | Yes | The ID of the milestone |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `due_date` | `null \| string` |  |
| `start_date` | `null \| string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `web_url` | `string` |  |
| `expired` | `null \| boolean` |  |
| `group_id` | `null \| integer` |  |
| `project_id` | `null \| integer` |  |


</details>

### Group Milestones Search

Search and filter group milestones records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.group_milestones.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "group_milestones",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the milestone |
| `iid` | `integer` | Internal ID of the milestone within the group |
| `group_id` | `integer` | ID of the group |
| `title` | `string` | Title of the milestone |
| `description` | `string` | Description of the milestone |
| `state` | `string` | State of the milestone |
| `created_at` | `string` | Timestamp when the milestone was created |
| `updated_at` | `string` | Timestamp when the milestone was last updated |
| `due_date` | `string` | Due date of the milestone |
| `start_date` | `string` | Start date of the milestone |
| `expired` | `boolean` | Whether the milestone is expired |
| `web_url` | `string` | Web URL of the milestone |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the milestone |
| `data[].iid` | `integer` | Internal ID of the milestone within the group |
| `data[].group_id` | `integer` | ID of the group |
| `data[].title` | `string` | Title of the milestone |
| `data[].description` | `string` | Description of the milestone |
| `data[].state` | `string` | State of the milestone |
| `data[].created_at` | `string` | Timestamp when the milestone was created |
| `data[].updated_at` | `string` | Timestamp when the milestone was last updated |
| `data[].due_date` | `string` | Due date of the milestone |
| `data[].start_date` | `string` | Start date of the milestone |
| `data[].expired` | `boolean` | Whether the milestone is expired |
| `data[].web_url` | `string` | Web URL of the milestone |

</details>

## Project Milestones

### Project Milestones List

Returns a list of project milestones.

#### Python SDK

```python
await gitlab.project_milestones.list(
    project_id="<str>"
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_milestones",
    "action": "list",
    "params": {
        "project_id": "<str>"
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `page` | `integer` | No | Page number |
| `per_page` | `integer` | No | Number of items per page |
| `state` | `"active" \| "closed"` | No | Filter milestones by state |
| `search` | `string` | No | Search for milestones by title or description |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `due_date` | `null \| string` |  |
| `start_date` | `null \| string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `web_url` | `string` |  |
| `expired` | `null \| boolean` |  |
| `group_id` | `null \| integer` |  |
| `project_id` | `null \| integer` |  |


</details>

### Project Milestones Get

Get a single project milestone.

#### Python SDK

```python
await gitlab.project_milestones.get(
    project_id="<str>",
    milestone_id=0
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_milestones",
    "action": "get",
    "params": {
        "project_id": "<str>",
        "milestone_id": 0
    }
}'
```


#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `project_id` | `string` | Yes | The ID or URL-encoded path of the project |
| `milestone_id` | `integer` | Yes | The ID of the milestone |


<details>
<summary><b>Response Schema</b></summary>

#### Records

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` |  |
| `iid` | `integer` |  |
| `title` | `string` |  |
| `description` | `null \| string` |  |
| `state` | `string` |  |
| `due_date` | `null \| string` |  |
| `start_date` | `null \| string` |  |
| `created_at` | `string` |  |
| `updated_at` | `string` |  |
| `web_url` | `string` |  |
| `expired` | `null \| boolean` |  |
| `group_id` | `null \| integer` |  |
| `project_id` | `null \| integer` |  |


</details>

### Project Milestones Search

Search and filter project milestones records powered by Airbyte's data sync. This often provides additional fields and operators beyond what the API natively supports, making it easier to narrow down results before performing further operations. Only available in hosted mode.

#### Python SDK

```python
await gitlab.project_milestones.search(
    query={"filter": {"eq": {"id": 0}}}
)
```

#### API

```bash
curl --location 'https://api.airbyte.ai/api/v1/integrations/connectors/{your_connector_id}/execute' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer {your_auth_token}' \
--data '{
    "entity": "project_milestones",
    "action": "search",
    "params": {
        "query": {"filter": {"eq": {"id": 0}}}
    }
}'
```

#### Parameters

| Parameter Name | Type | Required | Description |
|----------------|------|----------|-------------|
| `query` | `object` | Yes | Filter and sort conditions. Supports operators: eq, neq, gt, gte, lt, lte, in, like, fuzzy, keyword, not, and, or |
| `query.filter` | `object` | No | Filter conditions |
| `query.sort` | `array` | No | Sort conditions |
| `limit` | `integer` | No | Maximum results to return (default 1000) |
| `cursor` | `string` | No | Pagination cursor from previous response's `meta.cursor` |
| `fields` | `array` | No | Field paths to include in results |

#### Searchable Fields

| Field Name | Type | Description |
|------------|------|-------------|
| `id` | `integer` | ID of the milestone |
| `iid` | `integer` | Internal ID of the milestone within the project |
| `project_id` | `integer` | ID of the project |
| `title` | `string` | Title of the milestone |
| `description` | `string` | Description of the milestone |
| `state` | `string` | State of the milestone |
| `created_at` | `string` | Timestamp when the milestone was created |
| `updated_at` | `string` | Timestamp when the milestone was last updated |
| `due_date` | `string` | Due date of the milestone |
| `start_date` | `string` | Start date of the milestone |
| `expired` | `boolean` | Whether the milestone is expired |
| `web_url` | `string` | Web URL of the milestone |

<details>
<summary><b>Response Schema</b></summary>

| Field Name | Type | Description |
|------------|------|-------------|
| `data` | `array` | List of matching records |
| `meta` | `object` | Pagination metadata |
| `meta.has_more` | `boolean` | Whether additional pages are available |
| `meta.cursor` | `string \| null` | Cursor for next page of results |
| `meta.took_ms` | `number \| null` | Query execution time in milliseconds |
| `data[].id` | `integer` | ID of the milestone |
| `data[].iid` | `integer` | Internal ID of the milestone within the project |
| `data[].project_id` | `integer` | ID of the project |
| `data[].title` | `string` | Title of the milestone |
| `data[].description` | `string` | Description of the milestone |
| `data[].state` | `string` | State of the milestone |
| `data[].created_at` | `string` | Timestamp when the milestone was created |
| `data[].updated_at` | `string` | Timestamp when the milestone was last updated |
| `data[].due_date` | `string` | Due date of the milestone |
| `data[].start_date` | `string` | Start date of the milestone |
| `data[].expired` | `boolean` | Whether the milestone is expired |
| `data[].web_url` | `string` | Web URL of the milestone |

</details>

