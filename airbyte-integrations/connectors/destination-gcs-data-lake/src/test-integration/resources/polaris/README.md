# Polaris Integration Test Setup (GCS)

This directory contains the configuration for running Polaris integration tests with GCS storage.

## What is Polaris?

For a detailed explanation of Apache Polaris concepts, architecture, and how the test environment works, see:
**[S3 Data Lake Polaris README](../../../destination-s3-data-lake/src/test-integration/resources/polaris/README.md)**

The GCS variant uses the same Polaris setup but with Google Cloud Storage instead of S3/MinIO.

## Prerequisites

1. A GCS bucket with appropriate permissions
2. A service account JSON key file with access to the bucket
3. Docker and Docker Compose installed locally

## Setup Instructions

### Step 1: Update Service Account Credentials File

Replace the contents of the file:
```
airbyte-integrations/connectors/destination-gcs-data-lake/src/test-integration/resources/polaris/secrets-2/gcs-sa.json
```

With your actual GCS service account JSON credentials. The file should contain the complete service account JSON:

### Step 2: Update PolarisEnvironment Configuration

Edit the file `src/test-integration/kotlin/io/airbyte/integrations/destination/gcs_data_lake/PolarisEnvironment.kt`:

Update the following constants with your GCS details:

```kotlin
// Update with your GCS bucket name
private const val BUCKET = "your-bucket-name"

// Update with your service account email
// IMPORTANT: Must include the "serviceAccount:" prefix
private const val GCS_SERVICE_ACCOUNT =
    "serviceAccount:your-service-account@your-project.iam.gserviceaccount.com"

// Update with your GCP location (e.g., "us", "eu", "asia-northeast1")
private const val GCP_LOCATION = "us"
```

**Note:** The service account credentials will be automatically loaded from the `secrets-2/gcs-sa.json` file.

### Step 3: Run the Tests

The Polaris integration tests are marked as `@Disabled` by default since they require manual setup.

To run them, execute:

```bash
./gradlew :airbyte-integrations:connectors:destination-gcs-data-lake:integrationTestNonDocker \
  --tests "*PolarisWriteTest"
```

## Test Lifecycle

When you run the test:

1. `PolarisEnvironment.startServices()` starts Docker Compose with Polaris and PostgreSQL
2. The environment waits for Polaris to be healthy
3. A catalog is created with your GCS bucket configuration
4. Principals, roles, and permissions are configured automatically
5. The test executes against the configured Polaris catalog
6. Data is written to your GCS bucket via Polaris