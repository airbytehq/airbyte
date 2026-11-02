# Airbyte Databases Data Catalog

This catalog lists tables in Airbyte's Config and Jobs databases.

<HashRedirect
redirects={{
    active_declarative_manifest: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_catalog: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_catalog_fetch_event: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_definition: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_definition_breaking_change: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_definition_config_injection: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_definition_version: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_definition_workspace_grant: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    actor_oauth_parameter: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    connector_builder_project: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    connector_rollout: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    declarative_manifest: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    declarative_manifest_image_version: "/platform/understanding-airbyte/database-data-catalog/config-database-connectors",
    connection: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    connection_operation: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    connection_tag: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    connection_timeline_event: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    notification_configuration: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    operation: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    schema_management: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    state: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    stream_generation: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    stream_refreshes: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    stream_reset: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    tag: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    workload: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    workload_label: "/platform/understanding-airbyte/database-data-catalog/config-database-connections",
    airbyte_configs_migrations: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    application: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    auth_refresh_token: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    auth_user: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    dataplane: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    dataplane_group: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    organization: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    organization_email_domain: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    organization_payment_config: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    permission: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    scoped_configuration: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    secret_persistence_config: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    sso_config: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    user: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    user_invitation: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    workspace: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    workspace_service_account: "/platform/understanding-airbyte/database-data-catalog/config-database-organizations",
    jobs: "/platform/understanding-airbyte/database-data-catalog/jobs-database",
    attempts: "/platform/understanding-airbyte/database-data-catalog/jobs-database",
    airbyte_metadata: "/platform/understanding-airbyte/database-data-catalog/jobs-database",
    airbyte_jobs_migrations: "/platform/understanding-airbyte/database-data-catalog/jobs-database",
    normalization_summaries: "/platform/understanding-airbyte/database-data-catalog/jobs-database"
  }}
/>

## Config Database

- [Config Database: connectors and definitions](/platform/understanding-airbyte/database-data-catalog/config-database-connectors):
  [`active_declarative_manifest`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#active_declarative_manifest), [`actor`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor), [`actor_catalog`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_catalog),
  [`actor_catalog_fetch_event`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_catalog_fetch_event), [`actor_definition`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_definition), [`actor_definition_breaking_change`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_definition_breaking_change),
  [`actor_definition_config_injection`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_definition_config_injection), [`actor_definition_version`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_definition_version), [`actor_definition_workspace_grant`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_definition_workspace_grant),
  [`actor_oauth_parameter`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#actor_oauth_parameter), [`connector_builder_project`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#connector_builder_project), [`connector_rollout`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#connector_rollout),
  [`declarative_manifest`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#declarative_manifest), [`declarative_manifest_image_version`](/platform/understanding-airbyte/database-data-catalog/config-database-connectors#declarative_manifest_image_version)
- [Config Database: connections and syncs](/platform/understanding-airbyte/database-data-catalog/config-database-connections):
  [`connection`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#connection), [`connection_operation`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#connection_operation), [`connection_tag`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#connection_tag),
  [`connection_timeline_event`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#connection_timeline_event), [`notification_configuration`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#notification_configuration), [`operation`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#operation),
  [`schema_management`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#schema_management), [`state`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#state), [`stream_generation`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#stream_generation),
  [`stream_refreshes`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#stream_refreshes), [`stream_reset`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#stream_reset), [`tag`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#tag),
  [`workload`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#workload), [`workload_label`](/platform/understanding-airbyte/database-data-catalog/config-database-connections#workload_label)
- [Config Database: organizations, workspaces, and access](/platform/understanding-airbyte/database-data-catalog/config-database-organizations):
  [`airbyte_configs_migrations`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#airbyte_configs_migrations), [`application`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#application), [`auth_refresh_token`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#auth_refresh_token),
  [`auth_user`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#auth_user), [`dataplane`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#dataplane), [`dataplane_group`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#dataplane_group),
  [`organization`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#organization), [`organization_email_domain`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#organization_email_domain), [`organization_payment_config`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#organization_payment_config),
  [`permission`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#permission), [`scoped_configuration`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#scoped_configuration), [`secret_persistence_config`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#secret_persistence_config),
  [`sso_config`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#sso_config), [`user`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#user), [`user_invitation`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#user_invitation),
  [`workspace`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#workspace), [`workspace_service_account`](/platform/understanding-airbyte/database-data-catalog/config-database-organizations#workspace_service_account)

## Jobs Database

- [Jobs Database](/platform/understanding-airbyte/database-data-catalog/jobs-database):
  [`jobs`](/platform/understanding-airbyte/database-data-catalog/jobs-database#jobs), [`attempts`](/platform/understanding-airbyte/database-data-catalog/jobs-database#attempts), [`airbyte_metadata`](/platform/understanding-airbyte/database-data-catalog/jobs-database#airbyte_metadata),
  [`airbyte_jobs_migrations`](/platform/understanding-airbyte/database-data-catalog/jobs-database#airbyte_jobs_migrations), [`normalization_summaries`](/platform/understanding-airbyte/database-data-catalog/jobs-database#normalization_summaries)
