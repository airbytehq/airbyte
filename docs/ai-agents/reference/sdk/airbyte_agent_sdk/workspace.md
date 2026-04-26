---
id: airbyte_agent_sdk-workspace
title: airbyte_agent_sdk.workspace
---

Module airbyte_agent_sdk.workspace
==================================
Workspace — top-level entry point for hosted-mode workspace operations.

Classes
-------

<a id="Workspace"></a>

`Workspace(*, client_id: str | None = None, client_secret: str | None = None, workspace_name: str | None = None, organization_id: str | None = None)`
:   Top-level entry point for Airbyte hosted-mode workspace operations.
    
    Provides workspace-level methods: `ask`, list/create/delete connectors,
    get a connector executor, and workflow/automation CRUD. Use `Workspace`
    when you want to operate against a whole workspace (many connectors,
    workflows, automations); use [`connect()`](index.md#connect) when you already
    know which connector you want to execute.
    
    Example:
        ```python
        import asyncio
        from airbyte_agent_sdk import Workspace
    
        async def main():
            async with Workspace(
                client_id="your_client_id",
                client_secret="your_client_secret",
                workspace_name="my-workspace",
            ) as ws:
                result = await ws.ask("list my recent customers")
                connectors = await ws.list_connectors()
                print(result.outcome, len(connectors))
    
        asyncio.run(main())
        ```
    
    Args:
        client_id: Airbyte OAuth client ID (or set `AIRBYTE_CLIENT_ID`).
        client_secret: Airbyte OAuth client secret (or set
            `AIRBYTE_CLIENT_SECRET`).
        workspace_name: Workspace name for scoping operations. Defaults to
            `"default"`.
        organization_id: Optional org ID for multi-org routing.
    
    Raises:
        ValueError: If `client_id`/`client_secret` are not supplied and no
            `AIRBYTE_CLIENT_ID`/`AIRBYTE_CLIENT_SECRET` env vars are set.

    ### Methods

    `ask(self, prompt: str) ‑> airbyte_agent_sdk.executor.models.AskResult`
    :   Ask a natural-language question across all connectors.

    `close(self)`
    :   Close the cloud client.

    `create_automation(self, workflow_id: str, *, trigger_type: str = 'schedule', enabled: bool = True, cron_expression: str | None = None, timezone: str | None = None, completion_webhook_url: str | None = None) ‑> airbyte_agent_sdk.executor.models.AutomationInfo`
    :   Create an automation on a workflow.

    `create_connector(self, *, definition_id: str, credentials: dict[str, Any] | None = None, name: str | None = None, replication_config: dict[str, Any] | None = None, source_template_id: str | None = None) ‑> str`
    :   Create a new connector, returns the connector ID.

    `create_workflow(self, name: str, *, tasks: list[dict[str, Any]] | None = None) ‑> airbyte_agent_sdk.executor.models.WorkflowInfo`
    :   Create a workflow in this workspace.

    `delete_automation(self, workflow_id: str, automation_id: str) ‑> None`
    :   Delete an automation.

    `delete_connector(self, connector_id: str) ‑> None`
    :   Delete a connector.

    `delete_workflow(self, workflow_id: str) ‑> None`
    :   Delete a workflow.

    `get_automation(self, workflow_id: str, automation_id: str) ‑> airbyte_agent_sdk.executor.models.AutomationInfo`
    :   Get a single automation.

    `get_connector(self, *, connector_id: str | None = None, name: str | None = None) ‑> airbyte_agent_sdk.executor.hosted_executor.HostedExecutor`
    :   Get a HostedExecutor for a specific connector.
        
        Provide exactly one of connector_id or name:
        - connector_id: Direct lookup, no API call needed.
        - name: Resolves connector slug (e.g. "stripe") to the single instance
          of that type in this workspace. Raises ValueError if 0 or >1 found.
        
        Creates an independent HostedExecutor with its own AirbyteCloudClient.
        The caller is responsible for closing the executor when done.
        
        Example:
            stripe = await ws.get_connector(name="stripe")
            try:
                result = await stripe.execute(...)
            finally:
                await stripe.close()

    `get_workflow(self, workflow_id: str) ‑> airbyte_agent_sdk.executor.models.WorkflowInfo`
    :   Get a single workflow by ID.

    `list_automations(self, workflow_id: str) ‑> list[airbyte_agent_sdk.executor.models.AutomationInfo]`
    :   List automations for a workflow.

    `list_connectors(self) ‑> list[airbyte_agent_sdk.executor.models.ConnectorInfo]`
    :   List connector instances in this workspace.

    `list_workflows(self) ‑> list[airbyte_agent_sdk.executor.models.WorkflowInfo]`
    :   List workflows in this workspace.

    `update_automation(self, workflow_id: str, automation_id: str, *, enabled: bool | None = None, trigger_type: str | None = None, cron_expression: str | None = None, timezone: str | None = None, completion_webhook_url: str | None = None) ‑> airbyte_agent_sdk.executor.models.AutomationInfo`
    :   Update an automation.

    `update_workflow(self, workflow_id: str, *, name: str | None = None) ‑> airbyte_agent_sdk.executor.models.WorkflowInfo`
    :   Update a workflow.