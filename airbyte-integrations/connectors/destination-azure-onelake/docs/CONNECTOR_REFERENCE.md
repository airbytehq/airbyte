# Microsoft OneLake Destination — Connector reference

This document describes configuration, authentication, and how data is laid out in Fabric OneLake. Use it alongside [BUILD_AND_DEPLOY.md](./BUILD_AND_DEPLOY.md) for build and deployment steps.

---

## Table of contents

1. [What this connector does](#what-this-connector-does)
2. [Authentication: Service Principal vs Managed Identity](#authentication-service-principal-vs-managed-identity)
3. [Mandatory and optional fields](#mandatory-and-optional-fields)
4. [Folder and path structure in OneLake](#folder-and-path-structure-in-onelake)
5. [Airbyte UI behavior](#airbyte-ui-behavior)
6. [Permissions (Fabric / Azure)](#permissions-fabric--azure)

---

## What this connector does

- Writes Airbyte sync output to **Microsoft Fabric OneLake** (Lakehouse **Files**) using the **Azure Blob Storage API** against the fixed endpoint `https://onelake.blob.fabric.microsoft.com`.
- **Workspace** is the blob “container” name (use workspace name or GUID).
- **Lakehouse** is expressed as a path segment such as `MyLakehouse.Lakehouse` (or shorthand `MyLakehouse`, which the connector normalizes to `MyLakehouse.Lakehouse`).
- **Not supported for OneLake**: storage account key and SAS token. They remain in the JSON schema for compatibility but are **`airbyte_hidden`** in the UI (do not use them for OneLake).

---

## Authentication: Service Principal vs Managed Identity

| Mode | When to use | How it works |
|------|----------------|--------------|
| **Service Principal (SP)** | Any environment where you can store app credentials securely (Airbyte Cloud, self‑hosted, local with config file). | Connector uses **tenant ID + client ID + client secret** to obtain tokens for `https://storage.azure.com/.default`. |
| **Managed Identity (MI)** | Airbyte runs on **Azure** (e.g. AKS, Azure VM) and you want no client secret in config. | Connector uses **DefaultAzureCredential** (VM/AKS/pod identity). The **runtime identity** must be granted access in Fabric — this is **not** the same user as your Airbyte UI login. |

**Important:** Service Principal and Managed Identity are **different principals**. If SP works but MI returns `403` / “not authorized for workspace … artifact …”, grant the **MI** (object ID / app ID from the runtime) the same Fabric workspace access you gave the SP.

---

## Mandatory and optional fields

### Always required

| JSON field | UI label (typical) | Notes |
|------------|-------------------|--------|
| `azure_blob_storage_account_name` | Fabric Workspace Name or GUID | Fabric workspace identifier. |
| `azure_blob_storage_container_name` | Lakehouse Item Path | Lakehouse item, e.g. `lakehouse_raw` or `lakehouse_raw.Lakehouse`. |
| `format` | Output Format | JSONL or CSV (object storage format). |
| `use_managed_identity` | Use Managed Identity | `true` or `false` (boolean; always sent by the form). |

### Service Principal (`use_managed_identity` = **false**)

**Required (non-empty):**

- `azure_tenant_id` — Entra tenant ID  
- `azure_client_id` — App (client) ID  
- `azure_client_secret` — App secret  

**Do not** rely on Shared Access Signature or Account Key for OneLake; leave them empty.

### Managed Identity (`use_managed_identity` = **true**)

**Required:**

- None of tenant / client ID / client secret (leave blank or omit).

**Optional:**

- `managed_identity_client_id` — Set this for **user-assigned** managed identity (the identity’s client ID). Leave empty for **system-assigned** MI on the host.

### Common optional fields

| JSON field | UI label | Purpose |
|------------|----------|---------|
| `azure_blob_storage_endpoint_domain_name` | Azure Storage Endpoint Domain Name | Default `onelake.dfs.fabric.microsoft.com`; connector still uses the OneLake **blob** endpoint internally. |
| `destination_path_format` | Output Path Format | Directory layout under `Files/` (see below). |
| `file_name_pattern` | File Name Pattern | Output file naming pattern. |
| `azure_blob_storage_spill_size` | Target Object Size (MB) | When to roll to a new blob. |
| `one_lake_files_sub_path` | *(hidden)* | Advanced: subfolder under `Files/`. Normally leave unset; see path rules below. |

---

## Folder and path structure in OneLake

The connector builds a blob prefix:

`<LakehouseItem.Lakehouse>/Files/<optional subpath>/<destination_path_format>…`

Where:

- **`LakehouseItem.Lakehouse`** comes from **Lakehouse Item Path** (`.Lakehouse` appended if you omit it).
- **`destination_path_format`** is **Output Path Format** in the UI (`destination_path_format` in JSON).

### When **Output Path Format** is empty (null / blank)

- The connector uses a default internal subfolder under `Files/` of **`data`** (unless you override the hidden `one_lake_files_sub_path`).
- Resulting base path pattern:

  `…/Files/data/${NAMESPACE}/${STREAM_NAME}/…`  
  (plus default file name pattern unless you set **File Name Pattern**).

So in Fabric Explorer you typically see: **Files → data → …**

### When **Output Path Format** has a value

- The connector **does not** inject the extra default `data` segment for that case; your custom path is applied directly under `Files/`.
- Example: if Output Path Format is `Direct_Onelake_Connector_Data/`, data appears under:

  `…/Files/Direct_Onelake_Connector_Data/…`

Use this when you want full control of the folder layout and avoid an automatic `Files/data/...` layer.

### Hidden field `one_lake_files_sub_path`

- Normally hidden and empty in the UI.
- If set via API/raw config, it adds an extra segment: `Files/<one_lake_files_sub_path>/…`.
- Prefer using **Output Path Format** for visible, documented layout unless you have a specific reason to set the hidden field.

---

## Airbyte UI behavior

### Single UI group and “Optional fields”

Airbyte’s UI follows the [connector specification reference](https://docs.airbyte.com/platform/connector-development/connector-specification-reference/):

- **`connectionSpecification.groups`** plus **`group`** on each property puts related fields on **one card** (“Microsoft OneLake”). Without this, **ungrouped** properties can each get their own card, and **secrets** may appear outside the **Optional fields** section.
- **`always_show: true`** on a field **removes it from the “Optional fields”** collapsible and shows it in the main form (interleaved by `order`).
- For optional fields, **`order`** controls position inside **Optional fields** (then un-ordered fields are alphabetical).

This connector assigns **every visible property** to group **`onelake`** and uses **`order`** so that under **Optional fields** you typically get: **Managed Identity Client ID** (5) → **Azure Tenant ID** (6) → **Azure Client ID** (7) → **Azure Client Secret** (8), after the required block (workspace, lakehouse, output format, use managed identity).

Exact rendering can vary slightly by Airbyte version. **Rebuild the Docker image** after spec changes so the UI picks up the new schema.

### Duplicate error messages on save / test

When **Test connection** or **Save** fails, Airbyte often shows:

- An inline error in the form **and**
- A **toast / popup** with the same text

That duplication is produced by the **Airbyte web application**, not by duplicate messages from this connector. The connector cannot disable the extra toast; it only returns a single failure reason through the Airbyte protocol. If your team wants a single notification, that would be a change in the Airbyte UI or deployment configuration (if your fork supports it).

---

## Permissions (Fabric / Azure)

- **Service Principal app registration**: grant access to the Fabric **workspace** (and effectively the lakehouse artifact) so it can write to OneLake via Blob API. Typical guidance: **Storage Blob Data Contributor** (or equivalent) on the workspace scope your organization uses.
- **Managed Identity**: add the **same style of access** for the **MI principal** that the Airbyte workload uses (verify with IMDS / Azure portal — not the Airbyte UI user).

---

## Related docs

- [BUILD_AND_DEPLOY.md](./BUILD_AND_DEPLOY.md) — build, Docker, Kind, Kubernetes, troubleshooting  
- [GITHUB_SETUP.md](./GITHUB_SETUP.md) — publishing the connector repository  
