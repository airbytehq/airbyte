export default {
  "airbyte-api-content-docs": [
    {
      type: "category",
      label: "workspace",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-workspace",
          label: "Creates a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-workspace-if-not-exist",
          label:
            "Creates a workspace with an explicit workspace ID. This should be use in acceptance tests only.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-workspace",
          label: "Deletes a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-workspaces-paginated",
          label:
            "List workspaces by given workspace IDs registered in the current Airbyte deployment. This function also supports pagination.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-workspaces-in-organization",
          label:
            "List workspaces under the given org id. This function also supports searching by keyword and pagination.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-workspaces-by-user",
          label:
            "List workspaces by a given user id. The function also supports searching by keyword and pagination.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-available-dbt-jobs-for-workspace",
          label:
            "Calls the dbt Cloud `List Accounts` and `List jobs` APIs to get the list of available jobs for the dbt auth token associated with the requested workspace config.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-workspace",
          label: "Find workspace by ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-workspace-by-slug",
          label: "Find workspace by slug",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-workspace-by-connection-id",
          label: "Find workspace by connection id",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-workspace-by-connection-id-with-tombstone",
          label: "Find workspace by connection id including the tombstone ones",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-organization-info",
          label:
            "Retrieve a workspace's basic organization info that is accessible for all workspace members, regardless of organization membership.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-workspace",
          label: "Update workspace state",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-workspace-name",
          label: "Update workspace name",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-workspace-organization",
          label: "Update workspace organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-workspace-usage",
          label: "Get usage for a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-workspace-feedback",
          label: "Update workspace feedback state",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "source_definition",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "update-source-definition",
          label: "Update a sourceDefinition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-source-definitions",
          label:
            "List all the sourceDefinitions the current Airbyte deployment is configured to use",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-latest-source-definitions",
          label: "List the latest sourceDefinitions Airbyte supports",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source-definition",
          label: "Get source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-source-definition",
          label: "Delete a source definition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-private-source-definitions",
          label:
            "List all private, non-custom sourceDefinitions, and for each indicate whether the given workspace has a grant for using the definition. Used by admins to view and modify a given workspace's grants.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-source-definitions-for-workspace",
          label:
            "List all the sourceDefinitions the given workspace is configured to use",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-enterprise-source-stubs",
          label:
            "List all enterprise source connector stubs from a specified GCS bucket.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-enterprise-source-stubs-for-workspace",
          label:
            "List all enterprise source connector stubs for a specified workspace.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-custom-source-definition",
          label:
            "Creates a custom sourceDefinition for the given workspace or organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source-definition-for-workspace",
          label:
            "Get a sourceDefinition that is configured for the given workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source-definition-for-scope",
          label:
            "Get a sourceDefinition that is configured for the given workspace or organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "grant-source-definition",
          label:
            "grant a private, non-custom sourceDefinition to a given workspace or organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "revoke-source-definition",
          label:
            "revoke a grant to a private, non-custom sourceDefinition from a given workspace or organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "source_definition_specification",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-source-definition-specification",
          label: "Get specification for a SourceDefinition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-specification-for-source-id",
          label: "Get specification for a source.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "source",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-source",
          label: "Create a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-source",
          label: "Update a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "partial-update-source",
          label: "Partially update a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "upgrade-source-version",
          label: "Upgrade a source to the latest version",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-sources-for-workspace",
          label: "List sources for workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-sources-for-workspace-paginated",
          label: "List sources for workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source",
          label: "Get source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-most-recent-source-actor-catalog",
          label: "Get most recent ActorCatalog for source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "search-sources",
          label: "Search sources",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-source",
          label: "Delete a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "check-connection-to-source",
          label: "Check connection to the source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "check-connection-to-source-for-update",
          label: "Check connection for a proposed update to a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "discover-schema-for-source",
          label: "Discover the schema catalog of the source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "apply-schema-change-for-source",
          label:
            "Auto propagate the change on a catalog to a catalog saved in the DB. It will fetch all the connections linked to a source id and apply the provided diff to their catalog.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "write-discover-catalog-result",
          label:
            "Should only be called from job pods, to write result from discover activity back to DB.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "destination_definition",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "update-destination-definition",
          label: "Update destinationDefinition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-destination-definitions",
          label:
            "List all the destinationDefinitions the current Airbyte deployment is configured to use",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-latest-destination-definitions",
          label: "List the latest destinationDefinitions Airbyte supports",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-destination-definition",
          label: "Get destinationDefinition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-destination-definition",
          label: "Delete a destination definition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-private-destination-definitions",
          label:
            "List all private, non-custom destinationDefinitions, and for each indicate whether the given workspace has a grant for using the definition. Used by admins to view and modify a given workspace's grants.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-destination-definitions-for-workspace",
          label:
            "List all the destinationDefinitions the given workspace is configured to use",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-enterprise-destination-stubs-for-workspace",
          label:
            "List all enterprise destination connector stubs for a specified workspace.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-custom-destination-definition",
          label:
            "Creates a custom destinationDefinition for the given workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-destination-definition-for-workspace",
          label:
            "Get a destinationDefinition that is configured for the given workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-destination-definition-for-scope",
          label:
            "Get a destinationDefinition that is configured for the given scope",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "grant-destination-definition",
          label:
            "grant a private, non-custom destinationDefinition to a given workspace or organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "revoke-destination-definition",
          label:
            "revoke a grant to a private, non-custom destinationDefinition from a given workspace or organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "destination_definition_specification",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-destination-definition-specification",
          label: "Get specification for a destinationDefinition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-specification-for-destination-id",
          label: "Get specification for a destination",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "destination",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "write-destination-discover-catalog-result",
          label:
            "Should only be called from job pods, to write result from destination discover activity back to DB.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-destination",
          label: "Create a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-destination",
          label: "Update a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "partial-update-destination",
          label: "Update a destination partially",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "upgrade-destination-version",
          label: "Upgrade a destination to the latest version",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-destinations-for-workspace",
          label: "List configured destinations for a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-destinations-for-workspaces-paginated",
          label: "List configured destinations for a workspace. Pginated",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-destination",
          label: "Get configured destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "discover-catalog-for-destination",
          label: "Discover the catalog for a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-catalog-for-connection",
          label: "Get the destination catalog for a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "search-destinations",
          label: "Search destinations",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "check-connection-to-destination",
          label: "Check connection to the destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "check-connection-to-destination-for-update",
          label: "Check connection for a proposed update to a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-destination",
          label: "Delete the destination",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "connection",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-connection",
          label: "Create a connection between a source and a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-connection",
          label: "Update a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-connection-with-reason",
          label: "Update a connection with reason",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connections-for-workspace",
          label: "Returns all connections for a workspace.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connections-for-workspaces-paginated",
          label: "Returns all connections for a workspace. Paginated.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-all-connections-for-workspace",
          label:
            "Returns all connections for a workspace, including deleted connections.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-statuses",
          label: "Get the status of multiple connections",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-sync-progress",
          label: "Get progress information of the current sync of a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-uptime-history",
          label: "Get the uptime history of a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-data-history",
          label: "Get the data history of a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-stream-history",
          label: "Get the history of a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-event",
          label:
            "Get a single event (including details) in a connection by given event ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connection-events",
          label:
            "List most recent events in a connection (optional filters may apply)",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connection-events-minimal",
          label:
            "List all events in a given time span in a minimal representation",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "backfill-connection-events",
          label: "Backfill events for a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connection-events-for-job",
          label: "List all connection events for a given job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-last-job-per-stream",
          label:
            "Get a summary of the last completed job for each indicated stream in the connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection",
          label: "Get a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-for-job",
          label: "Get a connection for a given jobId",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connections-by-actor-definition",
          label: "List all connections that use the provided actor definition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "apply-schema-change-for-connection",
          label:
            "Auto propagate the change on a catalog to a catalog saved in the DB for the given connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "postprocess-discovered-catalog-for-connection",
          label:
            "Generate the diff between stored catalog for the connection and catalog provided and postprocess as necessary",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connection-context",
          label:
            "Retrieves the domain ids for all objects related to a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "search-connections",
          label: "Search connections",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-connection",
          label: "Delete a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "sync-connection",
          label: "Trigger a manual sync of the connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "reset-connection",
          label:
            "Reset the data for the connection. Deletes data generated by the connection in the destination. Resets any cursors back to initial state.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "clear-connection",
          label:
            "Clear the data for the connection. Deletes data generated by the connection in the destination. Clear any cursors back to initial state.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "auto-disable-connection",
          label:
            "Sets connection to inactive if it has met any of the auto-disable conditions (i.e. it hits the max number of consecutive job failures or if it hits the max number of days with only failed jobs). Additionally, notifications will be sent if a connection is disabled or warned if it has reached halfway to disable limits. This endpoint is only able to inactivate connections with more than one non-cancelled job.\n",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "clear-connection-stream",
          label:
            "Clear the data for a specific stream in the connection. Deletes data generated by the stream in the destination. Clear any cursors back to initial state.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "reset-connection-stream",
          label:
            "Reset the data for a specific stream in the connection. Deletes data generated by the stream in the destination. Resets any cursors back to initial state.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "refresh-connection-stream",
          label:
            "refresh the data for specific streams in the connection. If no stream is specify or the list of stream is empy, all the streams will be refreshed. Resets any cursors back to initial state.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "destination_oauth",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-destination-o-auth-consent",
          label:
            "Given a destination connector definition ID, return the URL to the consent screen where to redirect the user to.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "complete-destination-o-auth",
          label:
            "Given a destination def ID generate an access/refresh token etc.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "set-instancewide-destination-oauth-params",
          label:
            "Sets instancewide variables to be used for the oauth flow when creating this destination. When set, these variables will be injected into a connector's configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company's Google Ads developer_token, client_id, and client_secret without the user having to know about these variables.\n",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "source_oauth",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "set-instancewide-source-oauth-params",
          label:
            "Sets instancewide variables to be used for the oauth flow when creating this source. When set, these variables will be injected into a connector's configuration before any interaction with the connector image itself. This enables running oauth flows with consistent variables e.g: the company's Google Ads developer_token, client_id, and client_secret without the user having to know about these variables.\n",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source-o-auth-consent",
          label:
            "Given a source connector definition ID, return the URL to the consent screen where to redirect the user to.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-embedded-source-o-auth-consent",
          label:
            "Given a source connector definition ID, return the URL to the consent screen where to redirect the user to. This endpoint is specific for the embedded widget, and does not allow configuring the oAuthInputConfiguration for security purposes.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "complete-source-o-auth",
          label: "Given a source def ID generate an access/refresh token etc.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "revoke-source-o-auth-tokens",
          label:
            "Given a source definition ID and workspace ID revoke access/refresh token etc.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "web_backend",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "web-backend-check-updates",
          label:
            "Returns a summary of source and destination definitions that could be updated.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-validate-mappers",
          label:
            "Validates a draft set of mappers against a connection's configured streams",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-list-connections-for-workspace",
          label: "Returns all non-deleted connections for a workspace.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-get-connection-status-counts",
          label: "Returns aggregated connection status counts for a workspace.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-get-connection",
          label: "Get a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-create-connection",
          label: "Create a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-update-connection",
          label: "Update a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-describe-cron-expression",
          label:
            "Returns a human-readable description of a CronTrigger expression",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-state-type",
          label: "Fetch the current state type for a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "web-backend-get-workspace-state",
          label: "Returns the current state of a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-webapp-config",
          label: "Fetch webapp configuration",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "health",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-health-check",
          label: "Health Check",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "attempt",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "job-success-with-attempt-number",
          label: "For worker to mark an attempt as successful.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-new-attempt-number",
          label: "For worker to create a new attempt number.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "save-stream-metadata",
          label: "Save stream level attempt information",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "save-stats",
          label: "For worker to set sync stats of a running attempt.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "save-sync-config",
          label: "For worker to save the AttemptSyncConfig for an attempt.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "fail-attempt",
          label:
            "Fails an attempt with a failure summary and if provided a sync output.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-attempt-combined-stats",
          label: "For retrieving combined stats for a single attempt",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-attempt-for-job",
          label: "Retrieves an attempt with logs for a job and attempt number.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "state",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-state",
          label: "Fetch the current state for a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-or-update-state",
          label: "Create or update the state for a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-or-update-state-safe",
          label:
            "Create or update the state for a connection. Throws error if a sync is currently running when this is called.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "actor_definition_version",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-actor-definition-version-for-source-id",
          label: "Get actor definition version for a source.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "resolve-actor-definition-version-by-tag",
          label: "Resolve an actor definition version by version tag.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-actor-definition-version-default",
          label: "Get the default actor definition version for the actor.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-actor-definition-version-for-destination-id",
          label: "Get actor definition version for a destination.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "user",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-user",
          label: "Find Airbyte user by internal user ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-user-by-auth-id",
          label: "Find Airbyte user by auth id",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-user-by-email",
          label: "Find Airbyte user by email",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-or-create-user-by-auth-id",
          label:
            "Find Airbyte user by auth id. If not existed, will create a user.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-user",
          label: "Update user state",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-user",
          label: "Deletes a user",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-access-info-by-workspace-id",
          label: "List user access info for a particular workspace.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-users-in-organization",
          label: "List all users with permissions of the given org",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-instance-admin-users",
          label:
            "List all users with instance admin permissions. Only instance admin has permission to call this.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "permission",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-permission",
          label: "Creates a permission resource",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-permission",
          label: "Find a permission by ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "check-permissions",
          label: "Check permissions for user",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "check-permissions-across-multiple-workspaces",
          label: "Check permissions for user across workspaces",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-permission",
          label: "Updates a permission resource",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-permission",
          label: "Deletes a permission resource",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-user-from-workspace",
          label:
            "Deletes all workspace-level permissions for a particular user and workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-permissions-by-user",
          label: "List permissions a user has access to",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "organization",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-organization",
          label: "Get an organization info",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-organization",
          label: "Create an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-organization",
          label: "Update an organization info",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-organization",
          label: "Delete an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-organizations-by-user",
          label:
            "List organizations by a given user id. The function also supports searching by keyword and pagination.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-organization-usage",
          label: "Get usage for an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-organization-summaries",
          label:
            "Retrieve a paginated list of organizations with an optional filter, containing a summary of various org data",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-org-info",
          label:
            "Retrieve an organization's basic organization info that is accessible for all organization members.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "organization_payment_config",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-organization-payment-config",
          label: "Get an organization payment config",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "update-organization-payment-config",
          label: "Create or update an organization payment config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "end-grace-period",
          label: "End a grace period for an organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "deployment_metadata",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-deployment-metadata",
          label: "Provides the Airbyte deployment metadata.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "applications",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-applications",
          label: "Returns all Applications for a User.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-application",
          label: "Deletes an Application.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-application",
          label: "Creates a new Application.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "application-token-request",
          label: "Grant an Access Token for an Application.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "scoped_configuration",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-scoped-configurations-list",
          label: "Get all scoped configurations with a given key",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-scoped-configuration-context",
          label: "Get related configurations for a given scope",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-scoped-configuration",
          label: "Create a new scoped configuration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-scoped-configuration-by-id",
          label: "Get a scoped configuration by ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-scoped-configuration",
          label: "Update a scoped configuration by ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-scoped-configuration",
          label: "Delete a scoped configuration by ID",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "public",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-documentation",
          label: "Root path, currently returns a redirect to the documentation",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-get-health-check",
          label: "Health Check",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-list-config-template",
          label: "List config templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-config-template",
          label: "Create config template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-create-connection-template",
          label: "Create connection template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-update-config-template",
          label: "Update a config template",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-get-config-template",
          label: "Get a Config Template by id.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-list-applications",
          label: "List Applications",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-application",
          label: "Create an Application",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-application",
          label: "Get an Application detail",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-application",
          label: "Deletes an Application",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-get-access-token",
          label: "Get an Access Token",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-jobs",
          label: "List Jobs by sync type",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-job",
          label: "Trigger a sync or reset job of a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job",
          label: "Get Job status and details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-cancel-job",
          label: "Cancel a running Job",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-list-regions",
          label: "List regions",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-region",
          label: "Create a region",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-region",
          label: "Get a region",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-region",
          label: "Update a region",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-region",
          label: "Delete a region",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-list-dataplanes",
          label: "List dataplanes",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-dataplane",
          label: "Create a dataplane",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-dataplane",
          label: "Get a dataplane",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-dataplane",
          label: "Update a dataplane",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-dataplane",
          label: "Delete a dataplane",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "list-connector-definitions",
          label: "List connector definitions",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-list-declarative-source-definitions",
          label: "List declarative source definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-declarative-source-definition",
          label: "Create a declarative source definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-declarative-source-definition",
          label: "Get declarative source definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-declarative-source-definition",
          label: "Update declarative source definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-declarative-source-definition",
          label: "Delete a declarative source definition.",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-list-source-definitions",
          label: "List source definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-source-definition",
          label: "Create a source definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-source-definition",
          label: "Get source definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-source-definition",
          label: "Update source definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-source-definition",
          label: "Delete a source definition.",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-list-destination-definitions",
          label: "List destination definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-destination-definition",
          label: "Create a destination definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-destination-definition",
          label: "Get destination definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-destination-definition",
          label: "Update destination definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-destination-definition",
          label: "Delete a destination definition.",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "list-sources",
          label: "List sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-source",
          label: "Create a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-source",
          label: "Get Source details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "patch-source",
          label: "Update a Source",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "put-source",
          label: "Update a Source and fully overwrite it",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-source",
          label: "Delete a Source",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "list-destinations",
          label: "List destinations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-destination",
          label: "Create a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-destination",
          label: "Get Destination details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-destination",
          label: "Delete a Destination",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "patch-destination",
          label: "Update a Destination",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "put-destination",
          label: "Update a Destination and fully overwrite it",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "oauth-callback",
          label: "Receive OAuth callbacks",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "initiate-o-auth",
          label: "Initiate OAuth for a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-create-connection",
          label: "Create a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connections",
          label: "List connections",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-get-connection",
          label: "Get Connection details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "patch-connection",
          label: "Update Connection details",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-connection",
          label: "Delete a Connection",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "get-stream-properties",
          label: "Get stream properties",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-list-workspaces",
          label: "List workspaces",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-workspace",
          label: "Create a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-workspace",
          label: "Get Workspace details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-workspace",
          label: "Update a workspace",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-workspace",
          label: "Delete a Workspace",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "create-or-update-workspace-o-auth-credentials",
          label:
            "Create OAuth override credentials for a workspace and source type.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-get-permission",
          label: "Get Permission details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-permission",
          label: "Update a permission",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-permission",
          label: "Delete a Permission",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-list-permissions-by-user-id",
          label: "List Permissions by user id",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-permission",
          label: "Create a permission",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-list-organizations-for-user",
          label: "List all organizations for a user",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-or-update-organization-o-auth-credentials",
          label:
            "Create OAuth override credentials for an organization and source type.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-list-users-within-an-organization",
          label: "List all users within an organization",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-list-tags",
          label: "List all tags",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-tag",
          label: "Create a tag",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-tag",
          label: "Get a tag",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-tag",
          label: "Delete a tag",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-update-tag",
          label: "Update a tag",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "get-embedded-widget",
          label: "Get a widget token for Airbyte Embedded",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "generate-embedded-scoped-token",
          label: "Generate a scoped token for Airbyte Embedded",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-embedded-organizations-by-user",
          label:
            "List organizations that a user has access to that have embedded enabled.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "list-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-source",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source",
          label: "Get Source",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "partial_user_configs",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-partial-user-config",
          label: "Get details of a specific partial user config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-partial-user-config",
          label: "Create a partial user config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-partial-user-configs",
          label: "List partial user configs",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-partial-user-config",
          label: "Update a partial user config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-partial-user-config",
          label: "Tombstone a partial user config",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "embedded",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-config-templates",
          label: "List all config templates available to a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-config-template",
          label: "Get details of a specific config template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-partial-user-config",
          label: "Get details of a specific partial user config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-partial-user-config",
          label: "Create a partial user config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-partial-user-configs",
          label: "List partial user configs",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-partial-user-config",
          label: "Update a partial user config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-partial-user-config",
          label: "Tombstone a partial user config",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "public_health",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-get-health-check",
          label: "Health Check",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_jobs",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-jobs",
          label: "List Jobs by sync type",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-job",
          label: "Trigger a sync or reset job of a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job",
          label: "Get Job status and details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-cancel-job",
          label: "Cancel a running Job",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Jobs",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-jobs",
          label: "List Jobs by sync type",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-job",
          label: "Trigger a sync or reset job of a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job",
          label: "Get Job status and details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-cancel-job",
          label: "Cancel a running Job",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "entitlements",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "check-entitlement",
          label:
            "Determine whether the organization is entitled to the specified resource",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-entitlements",
          label: "Gets a list of entitlements for the organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "orchestration",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-orchestration",
          label: "Get a single orchestration by id",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-orchestrations-for-workspace",
          label: "Returns all orchestrations for a workspace.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-orchestration",
          label: "Create an orchestration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-orchestration",
          label: "Delete an orchestration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-orchestration",
          label: "Update an orchestration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "run-orchestration",
          label: "Start an orchestration",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Sources",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-sources",
          label: "List sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-source",
          label: "Create a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-source",
          label: "Get Source details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "patch-source",
          label: "Update a Source",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "put-source",
          label: "Update a Source and fully overwrite it",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-source",
          label: "Delete a Source",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "initiate-o-auth",
          label: "Initiate OAuth for a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-source",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source",
          label: "Get Source",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "internal",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-workspace-if-not-exist",
          label:
            "Creates a workspace with an explicit workspace ID. This should be use in acceptance tests only.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "write-discover-catalog-result",
          label:
            "Should only be called from job pods, to write result from discover activity back to DB.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "write-destination-discover-catalog-result",
          label:
            "Should only be called from job pods, to write result from destination discover activity back to DB.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-or-update-state",
          label: "Create or update the state for a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "auto-disable-connection",
          label:
            "Sets connection to inactive if it has met any of the auto-disable conditions (i.e. it hits the max number of consecutive job failures or if it hits the max number of days with only failed jobs). Additionally, notifications will be sent if a connection is disabled or warned if it has reached halfway to disable limits. This endpoint is only able to inactivate connections with more than one non-cancelled job.\n",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-job",
          label:
            "Creates a new job for a given connection. If a job is already running for the connection, it will be stopped and a new job will be created.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "job-success-with-attempt-number",
          label: "For worker to mark an attempt as successful.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-last-replication-job-with-cancel",
          label:
            "Get the latest job including the cancel jobs. This is used for scheduling in order to make sure that we don't immediately start a new job after a cancel.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job-input",
          label:
            "Get the job input in order to be able to start a synchronization.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "fail-non-terminal-jobs",
          label: "Fails all non-terminal jobs for a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "report-job-start",
          label: "For worker to report when a job starts.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-webhook-config",
          label: "Get a webhook config for a job.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "job-failure",
          label: "Marks a job as failed",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-stream-reset-records-for-job",
          label: "Deletes all stream reset records for the specified job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "explain-job",
          label:
            "Returns a LLM generated description of the result of a given job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "evaluate-outlier",
          label: "evaluate if a job is an outlier",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "finalize-job",
          label: "finalizes a job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-new-attempt-number",
          label: "For worker to create a new attempt number.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "save-stream-metadata",
          label: "Save stream level attempt information",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "save-stats",
          label: "For worker to set sync stats of a running attempt.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "save-sync-config",
          label: "For worker to save the AttemptSyncConfig for an attempt.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "fail-attempt",
          label:
            "Fails an attempt with a failure summary and if provided a sync output.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-attempt-combined-stats",
          label: "For retrieving combined stats for a single attempt",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-attempt-for-job",
          label: "Retrieves an attempt with logs for a job and attempt number.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "did-previous-job-succeed",
          label:
            "Returns whether the job preceding the specified job succeeded",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "persist-job-cancellation",
          label:
            "Persists the cancellation of a job and kicks off any post processing (e.g notifications).",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "run-check-command",
          label: "Run a Check command for a Connector",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "run-discover-command",
          label: "Run a Discover command for a Connector",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "run-replicate-command",
          label: "Run a Replicate command for a Connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-command",
          label: "Get the a command record",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "cloud-only",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-workspace-usage",
          label: "Get usage for a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-customer-portal-link",
          label: "Get a link to the customer portal",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "backfill-usage",
          label: "Backfill usage",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "handle-webhook",
          label:
            "Handle an external billing event (ie a webhook from an external payment provider service)",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-past-invoices",
          label: "Get a list of past invoices of the customer",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-payment-information",
          label:
            "Get a summary of payment information for a specific organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-subscription-info",
          label:
            "Get the current information about the organization's subscription",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-organization-trial-status",
          label: "Get the current trial status of an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "cancel-subscription",
          label: "Schedule canceling the subscription of an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "unschedule-cancel-subscription",
          label:
            "Unschedule a scheduled cancelation of the subscription of an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "disable-delinquent-workspaces",
          label:
            "Disable connections in workspaces that are delinquent in payment",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-organization-payment-config",
          label: "Get an organization payment config",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "update-organization-payment-config",
          label: "Create or update an organization payment config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "end-grace-period",
          label: "End a grace period for an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-organization-usage",
          label: "Get usage for an organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "notifications",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "try-notification-config",
          label: "Try sending a notifications; to be deprecated",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "try-notification-webhook-config",
          label: "Try sending a notifications to webhook",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "declarative_source_definitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-declarative-source-definition-manifest",
          label:
            "Create a declarative manifest to be used by the specified source definition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-declarative-manifest-version",
          label: "Update the declarative manifest version for a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-declarative-manifests",
          label:
            "List all available declarative manifest versions of a declarative source definition",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "connector_builder_project",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-connector-builder-project",
          label: "Create new connector builder project",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "publish-connector-builder-project",
          label: "Publish a connector to the workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-declarative-manifest-base-image",
          label: "Get the base image for the declarative manifest",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-connector-builder-project",
          label: "Update connector builder project",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-connector-builder-project",
          label: "Deletes connector builder project",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connector-builder-projects",
          label: "List connector builder projects for workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-builder-project",
          label: "Get a connector builder project with draft manifest",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-builder-project-id-for-definition-id",
          label: "Get a connector builder project by source definition ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-connector-builder-project-testing-values",
          label:
            "Submit a set of testing values to persist for a connector builder project",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "read-connector-builder-project-stream",
          label:
            "Reads the target stream of the connector builder project using the persisted testing values",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "full-resolve-manifest-builder-project",
          label:
            "Given a JSON manifest, returns a JSON manifest with all dynamic streams and all of the $refs and $parameters resolved and flattened",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "resolve-manifest-builder-project",
          label:
            "Given a JSON manifest, returns a JSON manifest with all of the $refs and $parameters resolved and flattened",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-builder-capabilities",
          label: "Get connector builder capabilities",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-forked-connector-builder-project",
          label:
            "Creates a new builder project that is a fork of an existing source definition",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "check-contribution",
          label: "Checks if a connector being contributed already exists",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "generate-contribution",
          label: "Generates a connector module and pushes it to Github as a PR",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-builder-project-o-auth-consent",
          label:
            "Given a connector builder project ID, return the URL to the consent screen where to redirect the user to.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "complete-connector-builder-project-oauth",
          label:
            "Given a builder project Id generate an access/refresh token etc.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "connector_builder_assist",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "assist-v-1-process",
          label: "Assist server access point",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "assist-v-1-warm",
          label: "Assist server warming access point",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "connector_documentation",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-connector-documentation",
          label: "Get the documentation for a connector",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "operation",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "check-operation",
          label: "Check if an operation to be created is valid",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-operation",
          label:
            "Create an operation to be applied as part of a connection pipeline",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-operation",
          label: "Update an operation",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-operations-for-connection",
          label: "Returns all operations for a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-operation",
          label: "Returns an operation",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-operation",
          label: "Delete an operation",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "scheduler",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "execute-source-check-connection",
          label: "Run check connection for a given source configuration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "execute-source-discover-schema",
          label:
            "Run discover schema for a given source a source configuration",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "execute-destination-check-connection",
          label: "Run check connection for a given destination configuration",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "jobs",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-job",
          label:
            "Creates a new job for a given connection. If a job is already running for the connection, it will be stopped and a new job will be created.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "job-success-with-attempt-number",
          label: "For worker to mark an attempt as successful.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-jobs-for",
          label:
            "Returns recent jobs for a connection. Jobs are returned in descending order by createdAt.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-jobs-for-workspaces",
          label:
            "Returns recent jobs for a connection. Jobs are returned in descending order by createdAt.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job-info",
          label: "Get information about a job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-last-replication-job",
          label: "Get the latest job not including the cancel jobs.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-last-replication-job-with-cancel",
          label:
            "Get the latest job including the cancel jobs. This is used for scheduling in order to make sure that we don't immediately start a new job after a cancel.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job-info-without-logs",
          label: "Get information about a job excluding logs",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job-info-light",
          label: "Get information about a job excluding attempt info and logs",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "cancel-job",
          label: "Cancels a job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job-debug-info",
          label: "Gets all information needed to debug this job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-job-input",
          label:
            "Get the job input in order to be able to start a synchronization.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "fail-non-terminal-jobs",
          label: "Fails all non-terminal jobs for a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "report-job-start",
          label: "For worker to report when a job starts.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-webhook-config",
          label: "Get a webhook config for a job.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "job-failure",
          label: "Marks a job as failed",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-stream-reset-records-for-job",
          label: "Deletes all stream reset records for the specified job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "explain-job",
          label:
            "Returns a LLM generated description of the result of a given job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "evaluate-outlier",
          label: "evaluate if a job is an outlier",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "finalize-job",
          label: "finalizes a job",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "did-previous-job-succeed",
          label:
            "Returns whether the job preceding the specified job succeeded",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "persist-job-cancellation",
          label:
            "Persists the cancellation of a job and kicks off any post processing (e.g notifications).",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "secrets_persistence_config",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-secrets-persistence-config",
          label: "Get secrets persistence config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-or-update-secrets-persistence-config",
          label: "Create or update secrets persistence config",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "secret_storage",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-secret-storage",
          label: "Create secret storage",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-secret-storage",
          label: "List all secret storages for a given scope",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-secret-storage",
          label: "Delete secret storage by its id",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-secret-storage",
          label: "Get secret storage by its id",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "migrate-secret-storage",
          label: "Migrate from one secret storage to another",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "openapi",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-open-api-spec",
          label: "Returns the openapi specification",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "stream_statuses",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-stream-statuses",
          label:
            "Gets a list of stream statuses filtered by parameters (with AND semantics).",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-stream-statuses-by-run-state",
          label:
            "Gets a list of the latest stream status for each stream and run state for a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-stream-status",
          label: "Creates a stream status.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-stream-status",
          label: "Updates a stream status.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "streams",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-stream-statuses",
          label:
            "Gets a list of stream statuses filtered by parameters (with AND semantics).",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-stream-statuses-by-run-state",
          label:
            "Gets a list of the latest stream status for each stream and run state for a connection.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-stream-status",
          label: "Creates a stream status.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-stream-status",
          label: "Updates a stream status.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "instance_configuration",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-instance-configuration",
          label: "Get instance configuration",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "setup-instance-configuration",
          label: "Setup an instance with user and organization information.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "license-info",
          label: "Fetch license limits and usage",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "job_retry_states",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-or-update",
          label: "Creates or updates a retry state for a job.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get",
          label: "Gets a retry state.",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "billing",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-customer-portal-link",
          label: "Get a link to the customer portal",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "backfill-usage",
          label: "Backfill usage",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "handle-webhook",
          label:
            "Handle an external billing event (ie a webhook from an external payment provider service)",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-past-invoices",
          label: "Get a list of past invoices of the customer",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-payment-information",
          label:
            "Get a summary of payment information for a specific organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-subscription-info",
          label:
            "Get the current information about the organization's subscription",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-organization-trial-status",
          label: "Get the current trial status of an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "cancel-subscription",
          label: "Schedule canceling the subscription of an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "unschedule-cancel-subscription",
          label:
            "Unschedule a scheduled cancelation of the subscription of an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "disable-delinquent-workspaces",
          label:
            "Disable connections in workspaces that are delinquent in payment",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-organization-payment-config",
          label: "Get an organization payment config",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "update-organization-payment-config",
          label: "Create or update an organization payment config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "end-grace-period",
          label: "End a grace period for an organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "admin-api",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-organization-payment-config",
          label: "Get an organization payment config",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "update-organization-payment-config",
          label: "Create or update an organization payment config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "end-grace-period",
          label: "End a grace period for an organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "connector_rollout",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-connector-rollouts-list",
          label:
            "Get all connector rollouts matching the provided actor definition ID & docker image version",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-rollouts-list-by-actor-definition-id",
          label:
            "Get all connector rollouts matching the provided actor definition ID",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-rollouts-list-all",
          label: "Get all connector rollouts",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-rollout-by-id",
          label: "Get a connector rollout by actor definition ID and version",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-connector-rollout-actor-sync-info",
          label:
            "Get a list of actors pinned to a release candidate, and information about their syncs",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "start-connector-rollout",
          label:
            "Start a connector rollout by ID. This will update the state of the rollout from INITIALIZED to WORKFLOW_STARTED, and add the Temporal run ID of the workflow to the rollout entry.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "do-connector-rollout",
          label:
            "Roll out a release candidate. This will pin the actors to the release candidate version ID.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-connector-rollout-state",
          label: "Update rollout state",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "finalize-connector-rollout",
          label:
            "Finalize a connector rollout by ID. This will unpin all actors that have been pinned to the release candidate version.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "manual-start-connector-rollout",
          label:
            "Manually start a connector rollout workflow. This will update the state of the rollout from INITIALIZED to WORKFLOW_STARTED, and add the Temporal run ID of the workflow to the rollout entry.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "manual-do-connector-rollout",
          label:
            "Manually roll out a release candidate. This will pin the actors to the release candidate version ID.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "manual-finalize-connector-rollout",
          label:
            "Manually finalize a connector rollout by ID. This will unpin all actors that have been pinned to the release candidate version.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "manual-pause-connector-rollout",
          label: "Update rollout state to paused",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "user_invitation",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-user-invitation",
          label: "Create a user invitation",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-user-invitation",
          label:
            "Get a user invitation by its unique code (not primary key ID)",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "list-pending-invitations",
          label: "List pending invitations",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "accept-user-invitation",
          label: "Accept a user invitation",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "decline-user-invitation",
          label: "Decline a user invitation",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "cancel-user-invitation",
          label: "Cancel a user invitation",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "tag",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-tags",
          label: "List tags in a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-tag",
          label: "Update a tag",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-tag",
          label: "Delete a tag",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-tag",
          label: "Create a tag",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "diagnostic_tool",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "generate-diagnostic-report",
          label: "Generate a diagnostic report",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "signal",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "signal",
          label: "Signal that an operation is terminal",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "command",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "run-check-command",
          label: "Run a Check command for a Connector",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "run-discover-command",
          label: "Run a Discover command for a Connector",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "run-replicate-command",
          label: "Run a Replicate command for a Connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-check-command-output",
          label: "Get the status of a check command",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-discover-command-output",
          label: "Get the status of a discover command",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-replicate-command-output",
          label: "Get the status of a replicate command",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-command-status",
          label: "Get the status of command",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-command",
          label: "Get the a command record",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "cancel-command",
          label: "Get the status of command",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "workload_output",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "write-workload-output",
          label: "Write the output of a workload",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "dataplane_group",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-dataplane-group",
          label: "Create a dataplane group",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-dataplane-group",
          label: "Update a dataplane group",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-dataplane-group",
          label: "Delete a dataplane group",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-dataplane-groups",
          label: "List dataplane groups for the organization",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "dataplane",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "create-dataplane",
          label: "Create a dataplane",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-dataplane",
          label: "Update a dataplane",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-dataplane",
          label: "Delete a dataplane",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-dataplanes",
          label: "List dataplanes for the dataplane group",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-dataplane-token",
          label: "Get a token for dataplane requests",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "heartbeat-dataplane",
          label: "For a dataplane to signal it is still alive",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "initialize-dataplane",
          label:
            "Returns information needed for dataplane startup and initialization (groups, queues, AuthN identify, etc.)",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "config_template",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-config-templates",
          label: "List all config templates available to a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-config-template",
          label: "Get details of a specific config template",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "sso_config",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-sso-config",
          label: "Retrieve the sso config for an organization",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "create-sso-config",
          label: "Onboard a cloud customer to SSO",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "delete-sso-config",
          label: "Remove an SSO config",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "update-sso-credentials",
          label: "Update a client id and client secret for an SSO IDP",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "public_root",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-documentation",
          label: "Root path, currently returns a redirect to the documentation",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_config_templates",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-config-template",
          label: "List config templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-config-template",
          label: "Create config template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-update-config-template",
          label: "Update a config template",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-get-config-template",
          label: "Get a Config Template by id.",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "ConfigTemplates",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-config-template",
          label: "List config templates",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-config-template",
          label: "Create config template",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-update-config-template",
          label: "Update a config template",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-get-config-template",
          label: "Get a Config Template by id.",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_connection_templates",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-create-connection-template",
          label: "Create connection template",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "ConnectionTemplates",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-create-connection-template",
          label: "Create connection template",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "public_applications",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-applications",
          label: "List Applications",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-application",
          label: "Create an Application",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-application",
          label: "Get an Application detail",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-application",
          label: "Deletes an Application",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-get-access-token",
          label: "Get an Access Token",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Applications",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-applications",
          label: "List Applications",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-application",
          label: "Create an Application",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-application",
          label: "Get an Application detail",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-application",
          label: "Deletes an Application",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-get-access-token",
          label: "Get an Access Token",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "public_regions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-regions",
          label: "List regions",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-region",
          label: "Create a region",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-region",
          label: "Get a region",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-region",
          label: "Update a region",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-region",
          label: "Delete a region",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Regions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-regions",
          label: "List regions",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-region",
          label: "Create a region",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-region",
          label: "Get a region",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-region",
          label: "Update a region",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-region",
          label: "Delete a region",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "public_dataplanes",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-dataplanes",
          label: "List dataplanes",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-dataplane",
          label: "Create a dataplane",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-dataplane",
          label: "Get a dataplane",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-dataplane",
          label: "Update a dataplane",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-dataplane",
          label: "Delete a dataplane",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Dataplanes",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-dataplanes",
          label: "List dataplanes",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-dataplane",
          label: "Create a dataplane",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-dataplane",
          label: "Get a dataplane",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-dataplane",
          label: "Update a dataplane",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-dataplane",
          label: "Delete a dataplane",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "public_connector_definitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-connector-definitions",
          label: "List connector definitions",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "ConnectorDefinitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-connector-definitions",
          label: "List connector definitions",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_declarative_source_definitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-declarative-source-definitions",
          label: "List declarative source definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-declarative-source-definition",
          label: "Create a declarative source definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-declarative-source-definition",
          label: "Get declarative source definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-declarative-source-definition",
          label: "Update declarative source definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-declarative-source-definition",
          label: "Delete a declarative source definition.",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "DeclarativeSourceDefinitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-declarative-source-definitions",
          label: "List declarative source definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-declarative-source-definition",
          label: "Create a declarative source definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-declarative-source-definition",
          label: "Get declarative source definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-declarative-source-definition",
          label: "Update declarative source definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-declarative-source-definition",
          label: "Delete a declarative source definition.",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "public_source_definitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-source-definitions",
          label: "List source definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-source-definition",
          label: "Create a source definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-source-definition",
          label: "Get source definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-source-definition",
          label: "Update source definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-source-definition",
          label: "Delete a source definition.",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "SourceDefinitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-source-definitions",
          label: "List source definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-source-definition",
          label: "Create a source definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-source-definition",
          label: "Get source definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-source-definition",
          label: "Update source definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-source-definition",
          label: "Delete a source definition.",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "public_destination_definitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-destination-definitions",
          label: "List destination definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-destination-definition",
          label: "Create a destination definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-destination-definition",
          label: "Get destination definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-destination-definition",
          label: "Update destination definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-destination-definition",
          label: "Delete a destination definition.",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "DestinationDefinitions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-destination-definitions",
          label: "List destination definitions.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-destination-definition",
          label: "Create a destination definition.",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-destination-definition",
          label: "Get destination definition details.",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-destination-definition",
          label: "Update destination definition details.",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-destination-definition",
          label: "Delete a destination definition.",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "public_sources",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-sources",
          label: "List sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-source",
          label: "Create a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-source",
          label: "Get Source details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "patch-source",
          label: "Update a Source",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "put-source",
          label: "Update a Source and fully overwrite it",
          className: "api-method put",
        },
        {
          type: "doc",
          id: "public-delete-source",
          label: "Delete a Source",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "initiate-o-auth",
          label: "Initiate OAuth for a source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-sources",
          label: "List Sources",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-source",
          label: "Create Source",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "get-source",
          label: "Get Source",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_destinations",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-destinations",
          label: "List destinations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-destination",
          label: "Create a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-destination",
          label: "Get Destination details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-destination",
          label: "Delete a Destination",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "patch-destination",
          label: "Update a Destination",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "put-destination",
          label: "Update a Destination and fully overwrite it",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "Destinations",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "list-destinations",
          label: "List destinations",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-destination",
          label: "Create a destination",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-destination",
          label: "Get Destination details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-destination",
          label: "Delete a Destination",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "patch-destination",
          label: "Update a Destination",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "put-destination",
          label: "Update a Destination and fully overwrite it",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "public_oauth",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "oauth-callback",
          label: "Receive OAuth callbacks",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "OAuth",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "oauth-callback",
          label: "Receive OAuth callbacks",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_connections",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-create-connection",
          label: "Create a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connections",
          label: "List connections",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-get-connection",
          label: "Get Connection details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "patch-connection",
          label: "Update Connection details",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-connection",
          label: "Delete a Connection",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "Connections",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-create-connection",
          label: "Create a connection",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-connections",
          label: "List connections",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-get-connection",
          label: "Get Connection details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "patch-connection",
          label: "Update Connection details",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-connection",
          label: "Delete a Connection",
          className: "api-method delete",
        },
      ],
    },
    {
      type: "category",
      label: "public_streams",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-stream-properties",
          label: "Get stream properties",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Streams",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-stream-properties",
          label: "Get stream properties",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_workspaces",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-workspaces",
          label: "List workspaces",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-workspace",
          label: "Create a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-workspace",
          label: "Get Workspace details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-workspace",
          label: "Update a workspace",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-workspace",
          label: "Delete a Workspace",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "create-or-update-workspace-o-auth-credentials",
          label:
            "Create OAuth override credentials for a workspace and source type.",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "Workspaces",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-workspaces",
          label: "List workspaces",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-workspace",
          label: "Create a workspace",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-workspace",
          label: "Get Workspace details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-workspace",
          label: "Update a workspace",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-workspace",
          label: "Delete a Workspace",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "create-or-update-workspace-o-auth-credentials",
          label:
            "Create OAuth override credentials for a workspace and source type.",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "public_permissions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-get-permission",
          label: "Get Permission details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-permission",
          label: "Update a permission",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-permission",
          label: "Delete a Permission",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-list-permissions-by-user-id",
          label: "List Permissions by user id",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-permission",
          label: "Create a permission",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "Permissions",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-get-permission",
          label: "Get Permission details",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-update-permission",
          label: "Update a permission",
          className: "api-method patch",
        },
        {
          type: "doc",
          id: "public-delete-permission",
          label: "Delete a Permission",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-list-permissions-by-user-id",
          label: "List Permissions by user id",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-permission",
          label: "Create a permission",
          className: "api-method post",
        },
      ],
    },
    {
      type: "category",
      label: "public_organizations",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-organizations-for-user",
          label: "List all organizations for a user",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-or-update-organization-o-auth-credentials",
          label:
            "Create OAuth override credentials for an organization and source type.",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "Organizations",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-organizations-for-user",
          label: "List all organizations for a user",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "create-or-update-organization-o-auth-credentials",
          label:
            "Create OAuth override credentials for an organization and source type.",
          className: "api-method put",
        },
      ],
    },
    {
      type: "category",
      label: "public_users",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-users-within-an-organization",
          label: "List all users within an organization",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "Users",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-users-within-an-organization",
          label: "List all users within an organization",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "public_tags",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-tags",
          label: "List all tags",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-tag",
          label: "Create a tag",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-tag",
          label: "Get a tag",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-tag",
          label: "Delete a tag",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-update-tag",
          label: "Update a tag",
          className: "api-method patch",
        },
      ],
    },
    {
      type: "category",
      label: "Tags",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "public-list-tags",
          label: "List all tags",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-create-tag",
          label: "Create a tag",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "public-get-tag",
          label: "Get a tag",
          className: "api-method get",
        },
        {
          type: "doc",
          id: "public-delete-tag",
          label: "Delete a tag",
          className: "api-method delete",
        },
        {
          type: "doc",
          id: "public-update-tag",
          label: "Update a tag",
          className: "api-method patch",
        },
      ],
    },
    {
      type: "category",
      label: "embedded_widget",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-embedded-widget",
          label: "Get a widget token for Airbyte Embedded",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "generate-embedded-scoped-token",
          label: "Generate a scoped token for Airbyte Embedded",
          className: "api-method post",
        },
        {
          type: "doc",
          id: "list-embedded-organizations-by-user",
          label:
            "List organizations that a user has access to that have embedded enabled.",
          className: "api-method get",
        },
      ],
    },
    {
      type: "category",
      label: "service_accounts",
      collapsible: true,
      collapsed: true,
      items: [
        {
          type: "doc",
          id: "get-service-account-token",
          label: "Get an access token for a service account.",
          className: "api-method post",
        },
      ],
    },
  ],
};
