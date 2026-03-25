# Destination: Microsoft OneLake

## Overview

The Microsoft OneLake destination connector writes data from Airbyte into a **Microsoft Fabric Lakehouse** using the OneLake endpoint. It supports CSV and JSONL output formats and authenticates via either a **Service Principal (Entra ID)** or **Managed Identity**.

| Feature | Supported |
|---|---|
| Full Refresh (Overwrite) | ✅ |
| Append | ✅ |
| Incremental (Deduped) | ❌ |
| Normalization | ❌ |
| dbt | ❌ |

---

## Prerequisites

Before connecting, ensure you have:

- A **Microsoft Fabric workspace** with at least one Lakehouse item created.
- An **Azure Entra ID (AAD) Service Principal** with the **Storage Blob Data Contributor** role on the Fabric workspace, **or** a **Managed Identity** assigned to the host running Airbyte with equivalent permissions.
- The **OneLake endpoint** enabled on your Fabric tenant (enabled by default: `onelake.dfs.fabric.microsoft.com`).

### Self-Managed Note

When running Airbyte OSS, ensure your instance can reach `onelake.dfs.fabric.microsoft.com` over HTTPS (port 443). If you are using Managed Identity, the host VM or Kubernetes node must have a managed identity assigned with the appropriate Fabric permissions.


---

## Setup Guide

### Step 1: Create a Lakehouse in Microsoft Fabric

1. Go to [Microsoft Fabric](https://app.fabric.microsoft.com) and open your workspace.
2. Click **New** → **Lakehouse** and give it a name (e.g., `lakehouse_raw`).
3. Note the **Workspace name or GUID** from the URL. If the workspace name contains spaces, use the GUID instead.
4. Note the **Lakehouse item path** — this is typically `YourLakehouse.Lakehouse`.

### Step 2: Configure Authentication

Choose one of the two supported authentication methods:

#### Option A: Service Principal (Entra ID)

1. In the [Azure Portal](https://portal.azure.com), navigate to **Entra ID** → **App registrations** → **New registration**.
2. Register an app and copy the **Tenant ID**, **Client ID**, and create a **Client Secret** under **Certificates & secrets**.
3. In Microsoft Fabric, go to your workspace **Settings** → **Manage access** and grant the service principal the **Contributor** role.

#### Option B: Managed Identity

1. Assign a **System-assigned** or **User-assigned** Managed Identity to the host running Airbyte (VM or AKS node).
2. In Microsoft Fabric, grant the managed identity the **Contributor** role in workspace access settings.
3. For user-assigned identities, note the identity's **Client ID**.

### Step 3: Connect in Airbyte

1. In Airbyte, go to **Destinations** → **New Destination** → **Microsoft OneLake**.
2. Fill in the fields as described in the [Configuration Reference](#configuration-reference) below.
3. Click **Test Connection** to validate.

---

## Configuration Reference

### OneLake Endpoint Domain Name

The OneLake DFS endpoint. Leave this as the default value unless you are connecting to a sovereign cloud or private endpoint.

**Default:** `onelake.dfs.fabric.microsoft.com`

---

### Fabric Workspace Name or GUID

The name or GUID of your Microsoft Fabric workspace. If the workspace name contains spaces, use the GUID instead.

**Where to find it:** Open your Fabric workspace in the browser. The URL contains the workspace GUID: `https://app.fabric.microsoft.com/groups/<WORKSPACE_GUID>/...`

**Examples:** `myworkspace`, `12345678-aaaa-bbbb-cccc-123456789012`

---

### Lakehouse Item Path

The target Lakehouse within your workspace. This is the Fabric item that will receive your data under its **Files** section.

**Format:** `LakehouseName.Lakehouse` or just the Lakehouse name if it has no spaces.

**Examples:** `MyLakehouse.Lakehouse`, `lakehouse_raw`

---

### Output Format

The file format used for data written to OneLake. Choose between:

| Format | Description |
|---|---|
| **CSV** | Comma-separated values. Supports optional root-level flattening of nested JSON fields. |
| **JSONL** | Newline-delimited JSON. Each record is written as a single JSON object per line. Supports optional root-level flattening. |

**Flattening options:**
- `No flattening` — nested objects are preserved as JSON strings inside the output.
- `Root level flattening` — top-level nested fields are expanded into separate columns/keys.

---

### Use Managed Identity

Toggle this **on** to authenticate using the Azure Managed Identity of the host running Airbyte, instead of a Service Principal.

- Requires the identity to have **Storage Blob Data Contributor** (or equivalent) permissions on the Fabric workspace.
- When enabled, the **Azure Client Secret** field is not required.

**Default:** `false`

---

### Managed Identity Client ID (optional)

Only required when using a **User-Assigned Managed Identity**. Leave empty if using a System-Assigned Managed Identity.

This is the **Client ID** of the user-assigned identity, found in the Azure Portal under **Managed Identities**.

---

### Azure Tenant ID

The **Directory (Tenant) ID** of your Azure Entra ID. Required when authenticating via Service Principal.

**Where to find it:** Azure Portal → Entra ID → Overview → **Tenant ID**.

**Example:** `12345678-1234-1234-1234-123456789012`

---

### Azure Client ID

The **Application (Client) ID** of your registered Entra ID app (Service Principal). Required when authenticating via Service Principal.

**Where to find it:** Azure Portal → Entra ID → App registrations → your app → **Application (client) ID**.

**Example:** `87654321-4321-4321-4321-210987654321`

---

### Azure Client Secret

The client secret generated for your Entra ID app. Required when **Use Managed Identity** is off.

**Where to find it:** Azure Portal → Entra ID → App registrations → your app → **Certificates & secrets** → **Client secrets**.

> ⚠️ Treat this value as a password. It is stored encrypted by Airbyte.

---

### Target Object Size (MB)

The maximum size (in megabytes) of each output file before the connector starts writing to a new file (spilling). Set to `0` to disable size-based splitting.

**Default:** `500` MB

---

### Output Path Format

Controls the directory structure inside the Lakehouse **Files** section where data is written. Supports the following template variables:

| Variable | Description |
|---|---|
| `${NAMESPACE}` | The source namespace (schema) |
| `${STREAM_NAME}` | The name of the stream (table) |
| `${YEAR}` | Current year |
| `${MONTH}` | Current month |
| `${DAY}` | Current day |

**Example:** `${NAMESPACE}/${STREAM_NAME}/`

Leave empty to use the default path structure.

---

### File Name Pattern

Controls how output files are named. Supports the following template variables:

| Variable | Description |
|---|---|
| `{date}` | Date of the sync |
| `{timestamp}` | Unix timestamp of the sync |
| `{part_number}` | File part number (for spilled files) |
| `{format_extension}` | File extension based on output format (`.csv`, `.jsonl`) |

**Example:** `{date}_{timestamp}_{part_number}{format_extension}`

Leave empty to use default naming.

---

## Supported Sync Modes

| Sync Mode | Supported |
|---|---|
| Full Refresh — Overwrite | ✅ |
| Full Refresh — Append | ✅ |
| Incremental — Append | ✅ |
| Incremental — Deduped | ❌ |

---

## Output File Structure

Data is written to the **Files** section of the target Lakehouse, not the Tables section. The path structure follows the **Output Path Format** configuration.

Example output path with default settings:

```
Files/
└── <namespace>/
    └── <stream_name>/
        └── <timestamp>_<part>.jsonl
```

To use the data in Fabric notebooks or Spark, reference the file path using the OneLake ABFS URI:

```
abfss://<workspace_guid>@onelake.dfs.fabric.microsoft.com/<lakehouse>.Lakehouse/Files/<path>
```

---

## Troubleshooting

### Authentication Errors

- **403 Forbidden:** Verify the Service Principal or Managed Identity has the **Contributor** role in the Fabric workspace settings (not just Azure RBAC).
- **Invalid client secret:** Client secrets expire. Rotate the secret in Entra ID and update the connector configuration.
- **Managed Identity not found:** Ensure the VM or AKS node has the identity attached, and that the identity has been granted access in Fabric.

### Data Not Appearing in Lakehouse Tables

Data written by this connector goes to the **Files** section of the Lakehouse, not the managed **Tables** section. To query the data as a table, create a shortcut or use a Fabric notebook to load the files into a Delta table.

### File Size Issues

If syncs are producing very large files, reduce the **Target Object Size (MB)** setting to trigger file spilling at a smaller threshold.

---

## Changelog

| Version | Date | Pull Request | Subject |
|---|---|---|---|
| 0.1.0 | 2025-01-01 | | Initial release of destination-azure-onelake |