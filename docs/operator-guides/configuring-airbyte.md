---
products: oss-*
---

# Configuring Airbyte

This section covers the various configuration options Airbyte accepts. [Airbyte runs on Kubernetes](../deploying-airbyte/deploying-airbyte.md). To configure the Airbyte Kubernetes deployment, modify the `values.yaml` file. If you want to manage your own Kube manifests, refer to the `Helm Chart`.

The following configuration options are possible, organized by service. Internal-only variables are omitted for clarity. See `Configs.java` for a full list of variables.

:::warning
Be careful using variables marked as `alpha`. They aren't meant for public consumption.
:::

## Core

1. `AIRBYTE_VERSION` - Defines the Airbyte deployment version.
2. `SPEC_CACHE_BUCKET` - Defines the bucket for caching specs. This immensely speeds up spec operations. This is updated when new versions are published.

## Secrets

1. `SECRET_PERSISTENCE` - Defines the Secret Persistence type. Defaults to NONE. Set to GOOGLE_SECRET_MANAGER to use Google Secret Manager. Set to AWS_SECRET_MANAGER to use AWS Secret Manager. Set to TESTING_CONFIG_DB_TABLE to use the database as a test. Set to VAULT to use Hashicorp Vault, currently only the token based authentication is supported. Alpha support. Undefined behavior will result if this is turned on and then off.
2. `SECRET_STORE_GCP_PROJECT_ID` - Defines the GCP Project to store secrets in. Alpha support.
3. `SECRET_STORE_GCP_CREDENTIALS` - Defines the JSON credentials used to read/write Airbyte Configuration to Google Secret Manager. These credentials must have Secret Manager Read/Write access. Alpha support.
4. `VAULT_ADDRESS` - Defines the vault address to read/write Airbyte Configuration to Hashicorp Vault. Alpha Support.
5. `VAULT_PREFIX` - Defines the vault path prefix. Should follow the format `<engine>/<directory>/`, for example `kv/airbyte/` or `secret/airbyte/`. Empty by default. Alpha Support.
6. `VAULT_AUTH_TOKEN` - The token used for vault authentication. Alpha Support.
7. `VAULT_AUTH_METHOD` - How vault will preform authentication. Currently, only supports Token auth. Defaults to token. Alpha Support.
8. `AWS_ACCESS_KEY` - Defines the aws_access_key_id from the AWS credentials to use for AWS Secret Manager.
9. `AWS_SECRET_ACCESS_KEY`- Defines aws_secret_access_key to use for the AWS Secret Manager.
10. `AWS_KMS_KEY_ARN` - Optional param that defines the KMS Encryption key used for the AWS Secret Manager.
11. `AWS_SECRET_MANAGER_SECRET_TAGS` - Defines the tags that will be included to all writes to the AWS Secret Manager. The format should be "key1=value1,key2=value2".

## Database

1. `DATABASE_USER` - Defines the Jobs Database user.
2. `DATABASE_PASSWORD` - Defines the Jobs Database password.
3. `DATABASE_URL` - Defines the Jobs Database url in the form of `jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_DB}`. Do not include username or password.
4. `JOBS_DATABASE_INITIALIZATION_TIMEOUT_MS` - Defines the total time to wait for the Jobs Database to be initialized. This includes migrations.
5. `CONFIG_DATABASE_USER` - Defines the Configs Database user. Defaults to the Jobs Database user if empty.
6. `CONFIG_DATABASE_PASSWORD` - Defines the Configs Database password. Defaults to the Jobs Database password if empty.
7. `CONFIG_DATABASE_URL` - Defines the Configs Database url in the form of `jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_DB}`. Defaults to the Jobs Database url if empty.
8. `CONFIG_DATABASE_INITIALIZATION_TIMEOUT_MS` - Defines the total time to wait for the Configs Database to be initialized. This includes migrations.
9. `RUN_DATABASE_MIGRATION_ON_STARTUP` - Defines if the Bootloader should run migrations on start up.

## Airbyte Services

1. `TEMPORAL_HOST` - Defines the url where Temporal is hosted at. Please include the port. Airbyte services use this information.
2. `INTERNAL_API_HOST` - Defines the url where the Airbyte Server is hosted at. Please include the port. Airbyte services use this information.
3. `WEBAPP_URL` - Defines the url the Airbyte Webapp is hosted at. Please include the port. Airbyte services use this information. You can set this variable to your custom domain name to change the Airbyte instance URL provided in notifications.

## Jobs

1. `SYNC_JOB_MAX_ATTEMPTS` - Defines the number of attempts a sync will attempt before failing. _Legacy - this is superseded by the values below_
2. `SYNC_JOB_RETRIES_COMPLETE_FAILURES_MAX_SUCCESSIVE` - Defines the max number of successive attempts in which no data was synchronized before failing the job.
3. `SYNC_JOB_RETRIES_COMPLETE_FAILURES_MAX_TOTAL` - Defines the max number of attempts in which no data was synchronized before failing the job.
4. `SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_MIN_INTERVAL_S` - Defines the minimum backoff interval in seconds between failed attempts in which no data was synchronized.
5. `SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_MAX_INTERVAL_S` - Defines the maximum backoff interval in seconds between failed attempts in which no data was synchronized.
6. `SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_BASE` - Defines the exponential base of the backoff interval between failed attempts in which no data was synchronized.
7. `SYNC_JOB_RETRIES_PARTIAL_FAILURES_MAX_SUCCESSIVE` - Defines the max number of attempts in which some data was synchronized before failing the job.
8. `SYNC_JOB_RETRIES_PARTIAL_FAILURES_MAX_TOTAL` - Defines the max number of attempts in which some data was synchronized before failing the job.
9. `SYNC_JOB_MAX_TIMEOUT_DAYS` - Defines the number of days a sync job will execute for before timing out.
10. `JOB_MAIN_CONTAINER_CPU_REQUEST` - Defines the job container's minimum CPU usage. Defaults to none.
11. `JOB_MAIN_CONTAINER_CPU_LIMIT` - Defines the job container's maximum CPU usage. Defaults to none.
12. `JOB_MAIN_CONTAINER_MEMORY_REQUEST` - Defines the job container's minimum RAM usage. Defaults to none.
13. `JOB_MAIN_CONTAINER_MEMORY_LIMIT` - Defines the job container's maximum RAM usage. Defaults to none.
14. `JOB_KUBE_TOLERATIONS` - Defines one or more Job pod tolerations. Tolerations are separated by ';'. Each toleration contains k=v pairs mentioning some/all of key, effect, operator and value and separated by `,`.
15. `JOB_KUBE_NODE_SELECTORS` - Defines one or more Job pod node selectors. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`. It is the pod node selectors of the sync job and the default pod node selectors fallback for others jobs.
16. `JOB_KUBE_ANNOTATIONS` - Defines one or more Job pod annotations. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`. It is the pod annotations of the sync job and the default pod annotations fallback for others jobs.
17. `JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY` - Defines the Job pod connector image pull policy.
18. `JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET` - Defines the Job pod connector image pull secret. Useful when hosting private images.
19. `JOB_KUBE_SIDECAR_CONTAINER_IMAGE_PULL_POLICY` - Defines the image pull policy on the sidecar containers in the Job pod. Useful when there are cluster policies enforcing to always pull.
20. `JOB_KUBE_SOCAT_IMAGE` - Defines the Job pod socat image.
21. `JOB_KUBE_BUSYBOX_IMAGE` - Defines the Job pod busybox image.
22. `JOB_KUBE_CURL_IMAGE` - Defines the Job pod curl image pull.
23. `JOB_KUBE_NAMESPACE` - Defines the Kubernetes namespace Job pods are created in.

## Jobs-specific

A job specific variable overwrites the default sync job variable defined above.

1. `SPEC_JOB_KUBE_NODE_SELECTORS` - Defines one or more pod node selectors for the spec job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
2. `CHECK_JOB_KUBE_NODE_SELECTORS` - Defines one or more pod node selectors for the check job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
3. `DISCOVER_JOB_KUBE_NODE_SELECTORS` - Defines one or more pod node selectors for the discover job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
4. `SPEC_JOB_KUBE_ANNOTATIONS` - Defines one or more pod annotations for the spec job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
5. `CHECK_JOB_KUBE_ANNOTATIONS` - Defines one or more pod annotations for the check job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
6. `DISCOVER_JOB_KUBE_ANNOTATIONS` - Defines one or more pod annotations for the discover job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`

## Connections

1. `MAX_FIELDS_PER_CONNECTION` - Defines the maximum number of fields able to be selected for a single connection.
2. `MAX_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_CONNECTION_DISABLE` - Defines the number of consecutive days of only failed jobs before the connection is disabled.
3. `MAX_FAILED_JOBS_IN_A_ROW_BEFORE_CONNECTION_DISABLE` - Defines the number of consecutive failed jobs before the connection is disabled.

## Logging

See [State and Logging Storage](../deploying-airbyte/integrations/storage.md) for more information on configuring logging.

1. `LOG_LEVEL` - Defines log levels. Defaults to INFO. This value is expected to be one of the various Log4J log levels.
2. `GCS_LOG_BUCKET` - Defines the GCS bucket to store logs.
3. `S3_BUCKET` - Defines the S3 bucket to store logs.
4. `S3_REGION` - Defines the S3 region the S3 log bucket is in.
5. `S3_AWS_KEY` - Defines the key used to access the S3 log bucket.
6. `S3_AWS_SECRET` - Defines the secret used to access the S3 log bucket.
7. `S3_MINIO_ENDPOINT` - Defines the url Minio is hosted at so Airbyte can use Minio to store logs.
8. `S3_PATH_STYLE_ACCESS` - Set to `true` if using Minio to store logs. Empty otherwise.

## Monitoring

1. `PUBLISH_METRICS` - Defines whether to publish metrics collected by the Metrics Reporter. Defaults to false.
2. `METRIC_CLIENT` - Defines which metrics client to use. Only relevant if `PUBLISH_METRICS` is set to true. Accepts either `datadog` or `otel`. Default to none.
3. `DD_AGENT_HOST` - Defines the ip the Datadog metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `datadog`. Defaults to none.
4. `DD_AGENT_PORT` - Defines the port the Datadog metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `datadog`. Defaults to none.
5. `OTEL_COLLECTOR_ENDPOINT` - Defines the ip:port the OTEL metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `otel`. Defaults to none.

## Worker

1. `MAX_CHECK_WORKERS` - Defines the maximum number of Non-Sync workers each Airbyte Worker container can support. Defaults to 5.
2. `MAX_SYNC_WORKERS` - Defines the maximum number of Sync workers each Airbyte Worker container can support. Defaults to 10.
3. `TEMPORAL_WORKER_PORTS` - Defines the local ports the Airbyte Worker pod uses to connect to the various Job pods. Port 9001 - 9040 are exposed by default in the Helm Chart.
4. `DISCOVER_REFRESH_WINDOW_MINUTES` - The minimum number of minutes Airbyte will wait to refresh a schema. By setting a larger number, you delay automatic schema refreshes and improve sync performance. The default in self-managed instances is 1440 (once per day), and in Cloud it's 15 (every 15 minutes). The lowest interval you can set is 1 (once per minute). Set this to 0 to disable automatic schema refreshes.

## Launcher

1. `WORKLOAD_LAUNCHER_PARALLELISM` - Defines the number of jobs that can be started at once. Defaults to 10.

## Data Retention

1. `TEMPORAL_HISTORY_RETENTION_IN_DAYS` - Defines the retention period of the job history in Temporal. Defaults to 30 days.

## Server

1.  `AUDIT_LOGGING_ENABLED` - For Self-Managed Enterprise only, defines whether audit logging is enabled. Set to `true` or `false`. If `true`, specify `STORAGE_BUCKET_AUDIT_LOGGING`.
2. `STORAGE_BUCKET_AUDIT_LOGGING` - For Self-Managed Enterprise only, if `AUDIT_LOGGING_ENABLED` is `true`, define your audit logging bucket here. You 
must configure a blob storage solution (S3, GCS, Azure Blob Storage).
