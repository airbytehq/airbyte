---
products: cloud-teams
sidebar_label: Audit logs
---

# Audit logs

Audit logs record who did what in your Airbyte organization. Every time someone creates a connection, changes a permission, updates a source, or modifies your single sign-on configuration, Airbyte writes an entry that captures the person responsible, the operation they performed, when it happened, and whether it succeeded.

Use audit logs to investigate unexpected changes, review administrative activity, and demonstrate to auditors that you have a record of configuration and access changes in Airbyte.

Audit logging is available in Pro and Enterprise Flex. Only organization admins can view audit logs.

## Audit logs aren't sync logs

Airbyte produces several kinds of logs, and audit logs are the narrowest of them. They only describe management activity, never the data your connections move.

| Log type | What it contains | Where you find it |
| --- | --- | --- |
| Audit logs | Management operations: who changed a workspace, connection, connector, user, permission, or setting | **Organization settings** > **Audit logs** |
| Sync logs (job logs) | What happened during one sync, check, or discover job, including connector output | A connection's [Timeline](/platform/cloud/managing-airbyte-cloud/review-connection-timeline) |
| Data plane logs | Platform logs your Airbyte data plane pods write to stdout, if you run your own data planes in Enterprise Flex | Your own observability stack. See [Collect logs from a Flex data plane](/platform/enterprise-flex/log-collection). |

Audit logs never contain the records your connections read or write. If you need to troubleshoot a failing sync, use the connection's sync logs instead.

## View your audit logs

1. In the navigation bar, click **Organization settings** > **Audit logs**.

2. Set **Start time (UTC)** and **End time (UTC)** to the period you want to review. All timestamps and filters use UTC.

3. Optionally narrow the results with these filters.

   | Filter | Description |
   | --- | --- |
   | Workspace | Only show operations that affected one workspace |
   | Actor | Only show operations performed by one person. Match on their email address or user ID |
   | Operation | Only show one type of operation, like `deleteWorkspace` |
   | Status | Only show operations that succeeded or failed |
   | Search | Match text in the operation, actor, or error message |

4. Click any row to see the complete entry as JSON, including the request and response summaries. You can copy this JSON if you need to attach it to an audit or ticket.

Airbyte shows 50 entries at a time, newest first. Use **Next** and **Previous** to move between pages.

## What Airbyte records

Each entry contains the following fields.

| Field | Description |
| --- | --- |
| `id` | Unique identifier for this entry |
| `timestamp` | When the operation occurred, in epoch milliseconds |
| `actor` | The person who performed the operation: their user ID, email address, IP address, and user agent |
| `operation` | The operation they performed, like `createSource` or `deletePermission` |
| `request` | A summary of the request, with sensitive fields removed |
| `response` | A summary of the response, with sensitive fields removed |
| `success` | Whether the operation succeeded |
| `errorMessage` | Why the operation failed, if it failed |
| `organizationId` | The organization the operation belongs to |
| `workspaceId` | The workspace the operation affected, if it affected one |

A typical entry looks like this.

```json
{
  "id": "8478fcbd-d369-4bda-8d9b-b782cea5ad40",
  "timestamp": 1746724563299,
  "actor": {
    "actorId": "1c26c465-58a8-43e6-8fc0-2252b7c8a9e2",
    "email": "user@example.com",
    "ipAddress": "192.0.2.0",
    "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
  },
  "operation": "deleteWorkspace",
  "request": "<request summary>",
  "response": "<response summary>",
  "success": true,
  "errorMessage": null,
  "organizationId": "b0b8b7b2-7e1c-4a9f-9f0e-3f1a0a6a1f11",
  "workspaceId": "0a9f2e1d-5c3b-4a77-9b21-6a7c1d2e3f44"
}
```

Airbyte audits operations that change your organization, including the following.

- Workspaces and organizations: creating, renaming, moving, and deleting them
- Sources and destinations: creating, updating, deleting, and upgrading connector versions
- Connections: creating, updating, and deleting them
- Users and access: adding and removing users, changing roles and permissions, and managing user groups
- Identity and security settings: single sign-on configuration, SCIM provisioning, and domain verification

To see exactly which operations Airbyte records for your organization, open the **Operation** filter on the **Audit logs** page.

## What Airbyte doesn't record

Audit logs deliberately omit sensitive material. Airbyte doesn't record the following.

- **Credentials and secrets**. Airbyte never writes connector configurations to an audit log. For sources and destinations, entries contain only identifying fields, like the source ID, name, and definition ID. Values such as `connectionConfiguration` and `secretId` are omitted, and a new secret-bearing field is omitted by default rather than logged. Airbyte also masks the client secret in single sign-on entries.
- **Your data**. Audit logs contain no records, no rows, and no schema contents from your sources and destinations.
- **Request and response bodies for some operations**. Where a body is large or sensitive, the entry records the actor and the operation without the body.
- **Activity in your data planes**. Audit logs cover the Airbyte control plane. Syncs produce their own logs, and if you run Enterprise Flex data planes in your own infrastructure, those logs stay with you.

## Storage and data residency

Airbyte stores audit logs in the Cloud control plane, in storage Airbyte manages and secures. Audit logs describe control plane activity, so the control plane writes and retains them. You can't redirect them to your own bucket, and they aren't written to any data plane you run yourself.

Airbyte retains audit log entries for 365 days, then deletes them. Export anything you need to keep for longer before it ages out.

Because entries describe management operations rather than the data you move, they contain organization, workspace, connector, and user metadata, but none of the records that pass through your connections. Data your connections move continues to be governed by the [region](/platform/cloud/managing-airbyte-cloud/manage-data-residency) you choose for each workspace, and, in Enterprise Flex, the [data plane](/platform/enterprise-flex/data-plane) that runs it.
