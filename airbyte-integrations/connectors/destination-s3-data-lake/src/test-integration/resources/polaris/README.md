# Polaris Test Environment

This directory contains the Docker Compose configuration and supporting code for running integration tests against [Apache Polaris](https://polaris.apache.org/), an open-source catalog service for Apache Iceberg.

## Overview

Apache Polaris is a catalog management service that implements the Iceberg REST Catalog API. It provides multi-tenancy, role-based access control, and credential vending for Iceberg tables, making it suitable for production data lake deployments.

## Docker Compose Architecture

The `docker-compose.yml` file orchestrates a complete Polaris environment with the following services:

### 1. MinIO (S3-Compatible Storage)
```yaml
- Image: minio/minio:RELEASE.2025-09-07T16-13-09Z
- Ports: 9000 (S3 API), 9001 (Web Console)
- Credentials: minio_root / m1n1opwd
```

MinIO provides S3-compatible object storage for Iceberg table data and metadata files. The service includes a health check that polls `/minio/health/ready` to ensure readiness before dependent services start.

### 2. mc-bootstrap (Bucket Initialization)
```yaml
- Image: minio/mc:latest
- Purpose: One-shot initialization job
- Creates: bucket123
```

This service uses the MinIO Client (`mc`) to automatically create the required S3 bucket. It:
- Waits for MinIO to be healthy
- Configures an alias for the MinIO instance
- Creates `bucket123` with automatic retries
- Exits successfully only when the bucket is confirmed visible
- Acts as a dependency gate: Polaris won't start until bucket creation succeeds

### 3. PostgreSQL (Metadata Store)
```yaml
- Image: postgres:16-alpine
- Port: 5432
- Database: POLARIS
- Credentials: postgres / postgres
```

PostgreSQL stores Polaris metadata including catalog definitions, principal information, role assignments, and privilege grants. All Polaris configuration persists here, making it the source of truth for the catalog's state.

### 4. Polaris (Catalog Service)
```yaml
- Image: apache/polaris:1.1.0-incubating
- Ports: 8181 (Catalog API), 8182 (Health/Metrics)
- Bootstrap Credentials: POLARIS realm, root principal, s3cr3t secret
```

The Polaris service provides:
- **Catalog API** (port 8181): REST endpoints for Iceberg catalog operations and management
- **Health/Metrics** (port 8182): Quarkus management endpoints for readiness probes
- **OAuth Token Endpoint**: `/api/catalog/v1/oauth/tokens` for credential exchange
- **Management API**: `/api/management/v1/*` for catalog/principal/role administration

Polaris is configured with:
- Connection to PostgreSQL for metadata persistence
- Bootstrap credentials for initial admin access
- AWS credentials (MinIO root) for server-side credential vending
- Path-style S3 access for MinIO compatibility

## Apache Polaris Concepts

Understanding Polaris requires familiarity with its security and organizational model:

### Realms
A **realm** is a top-level tenant in Polaris, providing complete isolation between different organizations or environments. Each realm has:
- Its own set of principals, catalogs, and roles
- Independent authentication and authorization
- Separate credential namespaces

In this setup, we use the `POLARIS` realm (configured via `Polaris-Realm` HTTP header).

### Principals
A **principal** is an authenticated identity (user or service account) in Polaris. Each principal has:
- A unique name
- OAuth credentials (`clientId` and `clientSecret`)
- Zero or more principal roles assigned to it

Principals authenticate using OAuth 2.0 client credentials flow and receive bearer tokens for API access.

### Principal Roles
A **principal role** is a collection of catalog role assignments that can be granted to principals. Think of it as a group membership:
- A principal can have multiple principal roles
- A principal role can contain multiple catalog role assignments
- Principal roles provide a level of indirection for managing permissions

Example: `quickstart_user_role` is a principal role that contains the assignment of the `quickstart_catalog_role` for the `quickstart_catalog`.

### Catalog Roles
A **catalog role** is a named set of privileges within a specific catalog. It defines what operations can be performed on catalog resources:
- Scoped to a single catalog
- Contains grants for specific privileges
- Can be assigned to principal roles

Example: `quickstart_catalog_role` might have `TABLE_CREATE`, `TABLE_READ_PROPERTIES`, and `NAMESPACE_LIST` privileges.

### Privileges
**Privileges** are atomic permissions that control access to catalog operations. Polaris supports privileges such as:

| Privilege | Description |
|-----------|-------------|
| `CATALOG_MANAGE_CONTENT` | Manage tables and namespaces in the catalog |
| `TABLE_CREATE` | Create new tables |
| `TABLE_DROP` | Delete tables |
| `TABLE_LIST` | List tables in a namespace |
| `TABLE_READ_PROPERTIES` | Read table metadata |
| `TABLE_WRITE_PROPERTIES` | Update table metadata |
| `TABLE_WRITE_DATA` | Write data to tables |
| `NAMESPACE_CREATE` | Create new namespaces |
| `NAMESPACE_LIST` | List namespaces |
| `NAMESPACE_READ_PROPERTIES` | Read namespace metadata |

### Permission Hierarchy

The permission flow in Polaris follows this hierarchy:

```
Principal (user/service account)
    ↓ assigned to
Principal Role (group)
    ↓ contains
Catalog Role Assignment (catalog-specific permissions)
    ↓ grants
Catalog Role (role within catalog)
    ↓ has
Privileges (specific operations)
```

## How PolarisEnvironment Works

The `PolarisEnvironment.kt` object (`src/test-integration/kotlin/.../PolarisEnvironment.kt`) orchestrates the test environment setup. Here's the detailed workflow:

### 1. Service Startup
```kotlin
startServices()
```
- Executes `docker compose up -d` using the docker-compose.yml file
- Waits for MinIO health check: `GET http://localhost:9000/minio/health/ready`
- Waits for Polaris health check: `GET http://localhost:8182/q/health/ready`
- Uses exponential backoff with configurable timeouts (120s for MinIO, 150s for Polaris)

### 2. Authentication Setup
```kotlin
fetchToken(scope = "PRINCIPAL_ROLE:ALL")
```
The bootstrap credentials are used for initial authentication:
- Sends OAuth token request to `http://localhost:8181/api/catalog/v1/oauth/tokens`
- Uses HTTP Basic Auth with `root:s3cr3t` (bootstrap principal)
- Includes `Polaris-Realm: POLARIS` header to specify the realm
- Receives bearer token for Management API access
- Implements automatic token refresh on 401 responses

### 3. Catalog Creation
```kotlin
createCatalogIfNeeded()
```
Creates the `quickstart_catalog` via `POST /api/management/v1/catalogs`:

```json
{
  "catalog": {
    "type": "INTERNAL",
    "name": "quickstart_catalog",
    "properties": {
      "default-base-location": "s3://bucket123/"
    },
    "storageConfigInfo": {
      "storageType": "S3",
      "region": "us-east-1",
      "endpoint": "http://localhost:9000",
      "endpointInternal": "http://minio:9000",
      "pathStyleAccess": true,
      "stsUnavailable": true
    }
  }
}
```

Key configuration points:
- **INTERNAL catalog**: Polaris manages the storage configuration
- **Two endpoints**: External (`localhost:9000`) for host access, internal (`minio:9000`) for container-to-container communication
- **Path-style access**: Required for MinIO compatibility (virtual-hosted style not supported)
- **STS unavailable**: MinIO doesn't support AWS STS, so Polaris uses direct credentials

### 4. Principal and Role Creation
```kotlin
createPrincipalAndGrants()
```

This is the most complex step, creating a complete authorization chain:

#### Step 4a: Create Principal
```kotlin
POST /api/management/v1/principals
{
  "name": "quickstart_user-{timestamp}"
}
```
- Generates unique principal name with timestamp
- Response includes `clientId` and `clientSecret` for OAuth
- Stores credentials in `appClientId` and `appClientSecret` for test use

#### Step 4b: Create Roles
```kotlin
POST /api/management/v1/principal-roles
{
  "name": "quickstart_user_role"
}

POST /api/management/v1/catalogs/quickstart_catalog/catalog-roles
{
  "name": "quickstart_catalog_role"
}
```
- Creates principal role (scope: realm-wide)
- Creates catalog role (scope: within quickstart_catalog)

#### Step 4c: Link Catalog Role to Principal Role
```kotlin
PUT /api/management/v1/principal-roles/quickstart_user_role/catalog-roles/quickstart_catalog
{
  "catalogRole": {
    "name": "quickstart_catalog_role"
  }
}
```
This grants the catalog role to the principal role for the specific catalog.

#### Step 4d: Grant Privileges to Catalog Role
```kotlin
grantAirbytePrivileges(catalogName, catalogRole)
```
Iterates through required privileges and grants each one:

```kotlin
PUT /api/management/v1/catalogs/quickstart_catalog/catalog-roles/quickstart_catalog_role/grants
{
  "grant": {
    "type": "catalog",
    "privilege": "TABLE_CREATE"  // repeated for each privilege
  }
}
```

Grants include:
- `CATALOG_MANAGE_CONTENT`: Overall catalog management
- `TABLE_*`: Table operations (list, create, drop, read/write properties, write data)
- `NAMESPACE_*`: Namespace operations (list, create, read properties)

#### Step 4e: Attach Principal Role to Principal
```kotlin
PUT /api/management/v1/principals/quickstart_user-{timestamp}/principal-roles
{
  "principalRole": {
    "name": "quickstart_user_role"
  }
}
```
Final step: assigns the principal role to the newly created principal.

### 5. Configuration Generation
```kotlin
getConfig()
```
Returns JSON configuration for the S3 Data Lake connector:

```json
{
  "catalog_type": {
    "catalog_type": "POLARIS",
    "server_uri": "http://localhost:8181/api/catalog",
    "catalog_name": "quickstart_catalog",
    "client_id": "{dynamically-generated-clientId}",
    "client_secret": "{dynamically-generated-clientSecret}",
    "namespace": "<DEFAULT_NAMESPACE_PLACEHOLDER>"
  },
  "s3_bucket_name": "bucket123",
  "s3_bucket_region": "us-east-1",
  "access_key_id": "minio_root",
  "secret_access_key": "m1n1opwd",
  "s3_endpoint": "http://localhost:9000",
  "warehouse_location": "s3://bucket123/",
  "main_branch_name": "main"
}
```

Configuration highlights:
- **POLARIS catalog type**: Uses Polaris-specific catalog implementation
- **Catalog name**: Explicitly references the `quickstart_catalog` created during setup
- **OAuth credentials**: Separate `client_id` and `client_secret` fields with dynamically created principal credentials
- **Direct S3 access**: Includes MinIO root credentials for S3 operations

### 6. Service Cleanup
```kotlin
stopServices()
```
- Executes `docker compose down -v` to stop and remove containers and volumes
- Clears cached tokens and credentials
- Ensures clean state for subsequent test runs

## Credential Vending

Polaris supports two credential modes:

### Option A: Client-Side Credentials (Current Setup)
The current configuration uses **client-side credentials**, where the client provides S3 credentials (`access_key_id` and `secret_access_key`) directly in the configuration. The connector uses these MinIO root credentials to access the underlying storage directly.

### Option B: Server-Side Vending (Available but Not Configured)
Polaris also supports server-side credential vending. When `header.X-Iceberg-Access-Delegation: vended-credentials` is added to the catalog configuration, Polaris generates temporary S3 credentials for each operation:
1. Client requests table metadata with OAuth token
2. Polaris validates the token and checks privileges
3. Polaris generates scoped temporary credentials using its AWS credentials (configured in docker-compose as `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`)
4. Response includes time-limited credentials for specific S3 paths
5. Client uses these credentials for data access

The docker-compose.yml is already configured with `AWS_ACCESS_KEY_ID: minio_root` and `AWS_SECRET_ACCESS_KEY: m1n1opwd` to support this mode, but it's not currently enabled in the test configuration.

## Running Integration Tests

The Polaris environment is automatically managed by integration tests:

```bash
# Run all Polaris integration tests
./gradlew :airbyte-integrations:connectors:destination-s3-data-lake:integrationTestNonDocker \
  --tests "*PolarisWriteTest"
```

### Test Lifecycle
1. Test calls `PolarisEnvironment.getConfig()` for catalog configuration
2. `startServices()` is called (idempotent, runs once per JVM)
3. Services start, catalog and permissions are configured
4. Test executes against the configured catalog
5. On JVM shutdown, `stopServices()` can be called to clean up (optional)