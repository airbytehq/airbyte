# OneLake Airbyte Destination Connector — Build, Deploy & Operations

This guide covers building the Docker image, deploying to Kubernetes (including Kind), configuring in Airbyte, and troubleshooting.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Building the Connector](#building-the-connector)
3. [Running Locally (Gradle)](#running-locally-gradle)
4. [Building the Docker Image](#building-the-docker-image)
5. [Deploying to Kind (Local Kubernetes)](#deploying-to-kind-local-kubernetes)
6. [Deploying to Airbyte (Kubernetes)](#deploying-to-airbyte-kubernetes)
7. [Configuration Reference](#configuration-reference)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- **Java 21** (OpenJDK or equivalent)
- **Gradle** (use the project wrapper: `./gradlew`)
- **Docker** (for building the connector image)
- **Kind** (optional, for local K8s): [install Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- **Airbyte** instance (self-hosted Kubernetes or Airbyte Cloud)
- **Microsoft Fabric** workspace with a Lakehouse, and either:
  - **Service Principal**: Azure Tenant ID, Client ID, Client Secret with **Storage Blob Data Contributor** on the workspace, or
  - **Managed Identity**: Identity attached to the host running the connector (e.g. AKS workload identity) with the same role

---

## Building the Connector

From the **Airbyte monorepo root** (parent of `airbyte-integrations/`):

```bash
# Compile and run unit tests
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:check

# Build the application (JAR) and Docker image
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:assemble
```

- **Output**: Application tarball and Docker image `airbyte/destination-azure-onelake:dev` (version comes from `gradle.properties` / build).

---

## Running Locally (Gradle)

Useful for testing spec, check, or sync without Docker.

### Spec (output connector JSON schema)

```bash
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:run --no-daemon -q --args="--spec"
```

### Check connection

Use an **absolute path** to your config file:

```bash
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:run --no-daemon -q --args="--check --config /absolute/path/to/config.json"
```

### Managed Identity config (local with env vars)

To test the Managed Identity config path locally, use environment variables so DefaultAzureCredential succeeds:

```bash
# Option A: export then run
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:run --no-daemon -q --args="--check --config /absolute/path/to/config_managed_identity.json"

# Option B: use the helper script (sources sample_secrets/.env.managed_identity if present)
./scripts/run_check_managed_identity_local.sh
```

---

## Building the Docker Image

From the **Airbyte monorepo root**:

```bash
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:assemble
```

This produces the image **`airbyte/destination-azure-onelake:dev`** (tag `dev` is the default from the build).

### Tagging for a release (e.g. 1.1)

```bash
docker tag airbyte/destination-azure-onelake:dev airbyte/destination-azure-onelake:1.1
```

(Use any tag you need: `1.0`, `1.1`, `latest`, etc.)

---

## Deploying to Kind (Local Kubernetes)

If you run Airbyte on a Kind cluster:

1. **Build and tag** (e.g. 1.1):
   ```bash
   ./gradlew :airbyte-integrations:connectors:destination-azure-onelake:assemble --no-daemon -q
   docker tag airbyte/destination-azure-onelake:dev airbyte/destination-azure-onelake:1.1
   ```

2. **Load the image into Kind** (replace `airbyte-abctl` with your cluster name if different):
   ```bash
   kind load docker-image airbyte/destination-azure-onelake:1.1 --name airbyte-abctl
   ```

3. **In Airbyte UI**: Add or edit the destination connector so its Docker image is `airbyte/destination-azure-onelake:1.1` (or the tag you used).

---

## Deploying to Airbyte (Kubernetes)

### Self-hosted Airbyte (Kubernetes)

1. **Build and push** the image to a registry your cluster can pull from:
   ```bash
   docker tag airbyte/destination-azure-onelake:dev your-registry/airbyte-destination-azure-onelake:1.1
   docker push your-registry/airbyte-destination-azure-onelake:1.1
   ```

2. **Register the connector** in Airbyte (UI or API) with:
   - **Docker image**: `your-registry/airbyte-destination-azure-onelake:1.1`
   - **Connector name**: e.g. "Microsoft OneLake"

3. **Create a destination** of that type and configure workspace, lakehouse, auth (Service Principal or Managed Identity), and path (see [Configuration Reference](#configuration-reference)).

### Airbyte Cloud

- Use a **custom connector** (if your plan supports it) and point it to your published image in a public or connected registry.
- Or use the same image in a self-hosted Airbyte instance that syncs to your Fabric workspace.

---

## Configuration Reference

| Field | Description | Example |
|-------|-------------|--------|
| **Fabric Workspace Name or GUID** | Workspace that contains the Lakehouse | `EG_Dataplatform_Dev` |
| **Lakehouse Item Path** | Lakehouse name (suffix `.Lakehouse` is added if missing) | `lakehouse_raw` |
| **Output Path Format** | Path under `Files/<subpath>/`; use trailing slash. Variables: `${NAMESPACE}`, `${STREAM_NAME}` | `Direct_Onelake_Connector_Data/` |
| **Use Managed Identity** | If `true`, use DefaultAzureCredential (no SP fields) | `false` for Service Principal |
| **Azure Tenant ID / Client ID / Client Secret** | Required when **Use Managed Identity** is `false` | — |
| **Managed Identity Client ID** | Optional; for user-assigned MI only | Leave empty for system-assigned |
| **one_lake_files_sub_path** | (Hidden in UI) Subfolder under `Files/`. Default: `data`. Set via JSON/config API for `Files/data/...` | `data` |

### Target path in Fabric

- Blob path prefix: `lakehouse_raw.Lakehouse/Files/<one_lake_files_sub_path>/<destination_path_format>...`
- In Fabric UI: **Lakehouse → Files → &lt;one_lake_files_sub_path&gt;/&lt;destination_path_format&gt;/...**
- Example: **Output Path Format** = `Direct_Onelake_Connector_Data/` and default subpath `data` → **Files/data/Direct_Onelake_Connector_Data/**

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| **Check fails: "blob was uploaded but could not be verified via metadata"** | Normal on OneLake. Connector 1.1+ treats upload success as a passing check; metadata/listing are best-effort. |
| **Check fails: "ManagedIdentityCredential authentication unavailable"** | Connector is not running in Azure. Use Service Principal or, locally, env vars (Option B) with Managed Identity config. |
| **Check fails: "Please run 'az login'"** | For local run with Managed Identity config, either run `az login` and ensure `az` is on PATH for the JVM, or set `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` and use the same config. |
| **Sync fails: NonUniqueBeanException** | Ensure you use the **onelake** connector image, not a mix of Azure Blob + OneLake in the same classpath. Use the built image as documented. |
| **Files not under Files/data/...** | Set **Output Path Format** (e.g. `Direct_Onelake_Connector_Data/`). For `Files/data/...`, set `one_lake_files_sub_path` to `data` via JSON/config (default in 1.1 is `data`). |
| **Permission denied on workspace** | Grant the Service Principal or Managed Identity **Storage Blob Data Contributor** (or equivalent) on the Fabric workspace. |

---

## Quick reference: full build + tag + Kind load

```bash
# From Airbyte repo root
./gradlew :airbyte-integrations:connectors:destination-azure-onelake:assemble --no-daemon -q
docker tag airbyte/destination-azure-onelake:dev airbyte/destination-azure-onelake:1.1
kind load docker-image airbyte/destination-azure-onelake:1.1 --name airbyte-abctl
```

Then in Airbyte, set the destination connector image to `airbyte/destination-azure-onelake:1.1`.
