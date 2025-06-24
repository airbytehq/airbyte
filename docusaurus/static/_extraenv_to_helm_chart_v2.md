Here is a complete list of environment variables with their Helm chart V2 equivalent. Some environment variables don't have direct V2 equivalents, so you can set these using the `extraEnv` configuration in the appropriate service section.

| Environment variable | Helm chart V2 equivalent | Description |
|---------------------|---------------------------|-------------|
| **Core** | | |
| AIRBYTE_VERSION | global.version | Defines the Airbyte deployment version. |
| AIRBYTE_EDITION | global.edition | Defines the Airbyte edition (community, pro, enterprise). |
| AIRBYTE_CLUSTER_TYPE | global.cluster.type | Defines the cluster type (control-plane, data-plane, hybrid). |
| AIRBYTE_CLUSTER_NAME | global.cluster.name | Defines the cluster name. |
| AIRBYTE_URL | global.airbyteUrl | Defines the URL where Airbyte is hosted. |
| AIRBYTE_API_HOST | global.api.host | Defines the API host URL. |
| AIRBYTE_API_AUTH_HEADER_NAME | global.api.authHeaderName | Defines the API authentication header name. |
| AIRBYTE_API_AUTH_HEADER_VALUE | global.api.authHeaderValue | Defines the API authentication header value. |
| AIRBYTE_SERVER_HOST | global.server.host | Defines the server host (without scheme). |
| API_AUTHORIZATION_ENABLED | global.auth.enabled | Defines whether API authorization is enabled. |
| CONNECTOR_BUILDER_SERVER_API_HOST | global.connectorBuilderServer.apiHost | Defines the connector builder server API host. |
| DEPLOYMENT_ENV | global.deploymentEnv | Defines the deployment environment. |
| INTERNAL_API_HOST | global.api.internalHost | Defines the internal API host URL. |
| LOCAL | global.local | Defines if running in local mode. |
| WEBAPP_URL | global.webapp.url | Defines the webapp URL. |
| SPEC_CACHE_BUCKET | Use extraEnvs | Defines the bucket for caching specs. This immensely speeds up spec operations. This is updated when new versions are published. |
| **Secrets** | | |
| SECRET_PERSISTENCE | global.secretsManager.type | Defines the Secret Persistence type. Defaults to NONE. Set to GOOGLE_SECRET_MANAGER to use Google Secret Manager. Set to AWS_SECRET_MANAGER to use AWS Secret Manager. Set to TESTING_CONFIG_DB_TABLE to use the database as a test. Set to VAULT to use Hashicorp Vault, currently only the token based authentication is supported. Alpha support. Undefined behavior will result if this is turned on and then off. |
| SECRET_STORE_GCP_PROJECT_ID | global.secretsManager.googleSecretManager.projectId | Defines the GCP Project to store secrets in. Alpha support. |
| SECRET_STORE_GCP_CREDENTIALS | global.secretsManager.googleSecretManager.credentials | Defines the JSON credentials used to read/write Airbyte Configuration to Google Secret Manager. These credentials must have Secret Manager Read/Write access. Alpha support. |
| VAULT_ADDRESS | global.secretsManager.vault.address | Defines the vault address to read/write Airbyte Configuration to Hashicorp Vault. Alpha Support. |
| VAULT_PREFIX | global.secretsManager.vault.prefix | Defines the vault path prefix. Should follow the format `<engine>/<directory>/`, for example `kv/airbyte/` or `secret/airbyte/`. Empty by default. Alpha Support. |
| VAULT_AUTH_TOKEN | global.secretsManager.vault.token | The token used for vault authentication. Alpha Support. |
| VAULT_AUTH_METHOD | global.secretsManager.vault.authMethod | How vault will preform authentication. Currently, only supports Token auth. Defaults to token. Alpha Support. |
| AWS_ACCESS_KEY | global.aws.accessKeyId | Defines the aws_access_key_id from the AWS credentials to use for AWS Secret Manager. |
| AWS_SECRET_ACCESS_KEY | global.aws.secretAccessKey | Defines aws_secret_access_key to use for the AWS Secret Manager. |
| AWS_KMS_KEY_ARN | global.secretsManager.awsSecretManager.kmsKeyArn | Optional param that defines the KMS Encryption key used for the AWS Secret Manager. |
| AWS_SECRET_MANAGER_SECRET_TAGS | global.secretsManager.awsSecretManager.tags | Defines the tags that will be included to all writes to the AWS Secret Manager. The format should be "key1=value1,key2=value2". |
| AWS_ASSUME_ROLE_ACCESS_KEY_ID | global.aws.assumeRole.accessKeyId | Defines the access key ID for AWS assume role. |
| **Database** | | |
| DATABASE_USER | global.database.user | Defines the Jobs Database user. |
| DATABASE_PASSWORD | global.database.password | Defines the Jobs Database password. |
| DATABASE_URL | global.database.url | Defines the Jobs Database url in the form of `jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_DB}`. Do not include username or password. |
| DATABASE_HOST | global.database.host | Defines the database host. |
| DATABASE_PORT | global.database.port | Defines the database port. |
| DATABASE_DB | global.database.database | Defines the database name. |
| JOBS_DATABASE_INITIALIZATION_TIMEOUT_MS | global.database.initializationTimeoutMs | Defines the total time to wait for the Jobs Database to be initialized. This includes migrations. |
| CONFIG_DATABASE_USER | global.database.user | Defines the Configs Database user. Defaults to the Jobs Database user if empty. |
| CONFIG_DATABASE_PASSWORD | global.database.password | Defines the Configs Database password. Defaults to the Jobs Database password if empty. |
| CONFIG_DATABASE_URL | global.database.url | Defines the Configs Database url in the form of `jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_DB}`. Defaults to the Jobs Database url if empty. |
| CONFIG_DATABASE_INITIALIZATION_TIMEOUT_MS | global.database.initializationTimeoutMs | Defines the total time to wait for the Configs Database to be initialized. This includes migrations. |
| RUN_DATABASE_MIGRATION_ON_STARTUP | global.migrations.runAtStartup | Defines if the Bootloader should run migrations on start up. |
| USE_CLOUD_SQL_PROXY | global.cloudSqlProxy.enabled | Defines whether to use Cloud SQL Proxy. |
| **Airbyte Services** | | |
| TEMPORAL_HOST | temporal.host | Defines the url where Temporal is hosted at. Please include the port. Airbyte services use this information. |
| **Jobs** | | |
| SYNC_JOB_MAX_ATTEMPTS | Use extraEnvs | Defines the number of attempts a sync will attempt before failing. *Legacy - this is superseded by the values below* |
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_MAX_SUCCESSIVE | Use extraEnvs | Defines the max number of successive attempts in which no data was synchronized before failing the job. |
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_MAX_TOTAL | Use extraEnvs | Defines the max number of attempts in which no data was synchronized before failing the job. |
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_MIN_INTERVAL_S | Use extraEnvs | Defines the minimum backoff interval in seconds between failed attempts in which no data was synchronized. |
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_MAX_INTERVAL_S | Use extraEnvs | Defines the maximum backoff interval in seconds between failed attempts in which no data was synchronized. |
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_BASE | Use extraEnvs | Defines the exponential base of the backoff interval between failed attempts in which no data was synchronized. |
| SYNC_JOB_RETRIES_PARTIAL_FAILURES_MAX_SUCCESSIVE | Use extraEnvs | Defines the max number of attempts in which some data was synchronized before failing the job. |
| SYNC_JOB_RETRIES_PARTIAL_FAILURES_MAX_TOTAL | Use extraEnvs | Defines the max number of attempts in which some data was synchronized before failing the job. |
| SYNC_JOB_MAX_TIMEOUT_DAYS | Use extraEnvs | Defines the number of days a sync job will execute for before timing out. |
| JOB_MAIN_CONTAINER_CPU_REQUEST | global.workloads.resources.mainContainer.cpu.request | Defines the job container's minimum CPU usage. Defaults to none. |
| JOB_MAIN_CONTAINER_CPU_LIMIT | global.workloads.resources.mainContainer.cpu.limit | Defines the job container's maximum CPU usage. Defaults to none. |
| JOB_MAIN_CONTAINER_MEMORY_REQUEST | global.workloads.resources.mainContainer.memory.request | Defines the job container's minimum RAM usage. Defaults to none. |
| JOB_MAIN_CONTAINER_MEMORY_LIMIT | global.workloads.resources.mainContainer.memory.limit | Defines the job container's maximum RAM usage. Defaults to none. |
| JOB_KUBE_TOLERATIONS | global.jobs.kube.tolerations | Defines one or more Job pod tolerations. Tolerations are separated by ';'. Each toleration contains k=v pairs mentioning some/all of key, effect, operator and value and separated by `,`. |
| JOB_KUBE_NODE_SELECTORS | global.jobs.kube.nodeSelector | Defines one or more Job pod node selectors. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`. It is the pod node selectors of the sync job and the default pod node selectors fallback for others jobs. |
| JOB_KUBE_ANNOTATIONS | global.jobs.kube.annotations | Defines one or more Job pod annotations. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`. It is the pod annotations of the sync job and the default pod annotations fallback for others jobs. |
| JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY | global.jobs.kube.mainContainerImagePullPolicy | Defines the Job pod connector image pull policy. |
| JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET | global.jobs.kube.mainContainerImagePullSecret | Defines the Job pod connector image pull secret. Useful when hosting private images. |
| JOB_KUBE_SIDECAR_CONTAINER_IMAGE_PULL_POLICY | global.jobs.kube.sidecarContainerImagePullPolicy | Defines the image pull policy on the sidecar containers in the Job pod. Useful when there are cluster policies enforcing to always pull. |
| JOB_KUBE_SOCAT_IMAGE | global.jobs.kube.images.socat | Defines the Job pod socat image. |
| JOB_KUBE_BUSYBOX_IMAGE | global.jobs.kube.images.busybox | Defines the Job pod busybox image. |
| JOB_KUBE_CURL_IMAGE | global.jobs.kube.images.curl | Defines the Job pod curl image pull. |
| JOB_KUBE_NAMESPACE | global.jobs.kube.namespace | Defines the Kubernetes namespace Job pods are created in. |
| JOB_KUBE_SERVICEACCOUNT | global.jobs.kube.serviceAccount | Defines the Kubernetes service account for Job pods. |
| **Jobs-specific** | | |
| SPEC_JOB_KUBE_NODE_SELECTORS | global.jobs.kube.scheduling.spec.nodeSelectors | Defines one or more pod node selectors for the spec job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2` |
| CHECK_JOB_KUBE_NODE_SELECTORS | global.jobs.kube.scheduling.check.nodeSelectors | Defines one or more pod node selectors for the check job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2` |
| DISCOVER_JOB_KUBE_NODE_SELECTORS | global.jobs.kube.scheduling.discover.nodeSelectors | Defines one or more pod node selectors for the discover job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2` |
| SPEC_JOB_KUBE_ANNOTATIONS | global.jobs.kube.scheduling.spec.annotations | Defines one or more pod annotations for the spec job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2` |
| CHECK_JOB_KUBE_ANNOTATIONS | global.jobs.kube.scheduling.check.annotations | Defines one or more pod annotations for the check job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2` |
| DISCOVER_JOB_KUBE_ANNOTATIONS | global.jobs.kube.scheduling.discover.annotations | Defines one or more pod annotations for the discover job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2` |
| **Connections** | | |
| MAX_FIELDS_PER_CONNECTION | Use extraEnvs | Defines the maximum number of fields able to be selected for a single connection. |
| MAX_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_CONNECTION_DISABLE | Use extraEnvs | Defines the number of consecutive days of only failed jobs before the connection is disabled. |
| MAX_FAILED_JOBS_IN_A_ROW_BEFORE_CONNECTION_DISABLE | Use extraEnvs | Defines the number of consecutive failed jobs before the connection is disabled. |
| **Logging** | | |
| LOG_LEVEL | global.logging.level | Defines log levels. Defaults to INFO. This value is expected to be one of the various Log4J log levels. |
| GCS_LOG_BUCKET | global.storage.gcs.bucket | Defines the GCS bucket to store logs. |
| S3_BUCKET | global.storage.s3.bucket | Defines the S3 bucket to store logs. |
| S3_REGION | global.storage.s3.region | Defines the S3 region the S3 log bucket is in. |
| S3_AWS_KEY | global.storage.s3.accessKeyId | Defines the key used to access the S3 log bucket. |
| S3_AWS_SECRET | global.storage.s3.secretAccessKey | Defines the secret used to access the S3 log bucket. |
| S3_MINIO_ENDPOINT | global.storage.minio.endpoint | Defines the url Minio is hosted at so Airbyte can use Minio to store logs. |
| S3_PATH_STYLE_ACCESS | global.storage.s3.pathStyleAccess | Set to `true` if using Minio to store logs. Empty otherwise. |
| **Monitoring** | | |
| PUBLISH_METRICS | global.metrics.enabled | Defines whether to publish metrics collected by the Metrics Reporter. Defaults to false. |
| METRIC_CLIENT | global.metrics.client | Defines which metrics client to use. Only relevant if `PUBLISH_METRICS` is set to true. Accepts either `datadog` or `otel`. Default to none. |
| DD_AGENT_HOST | global.datadog.agentHost | Defines the ip the Datadog metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `datadog`. Defaults to none. |
| DD_AGENT_PORT | global.datadog.agentPort | Defines the port the Datadog metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `datadog`. Defaults to none. |
| OTEL_COLLECTOR_ENDPOINT | global.metrics.otel.exporter.endpoint | Defines the ip:port the OTEL metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `otel`. Defaults to none. |
| MICROMETER_METRICS_ENABLED | global.metrics.enabled | Defines whether micrometer metrics are enabled. |
| **Worker** | | |
| MAX_CHECK_WORKERS | worker.maxCheckWorkers | Defines the maximum number of Non-Sync workers each Airbyte Worker container can support. Defaults to 5. |
| MAX_SYNC_WORKERS | worker.maxSyncWorkers | Defines the maximum number of Sync workers each Airbyte Worker container can support. Defaults to 10. |
| TEMPORAL_WORKER_PORTS | worker.temporalWorkerPorts | Defines the local ports the Airbyte Worker pod uses to connect to the various Job pods. Port 9001 - 9040 are exposed by default in the Helm Chart. |
| DISCOVER_REFRESH_WINDOW_MINUTES | Use extraEnvs | The minimum number of minutes Airbyte will wait to refresh a schema. By setting a larger number, you delay automatic schema refreshes and improve sync performance. The default in self-managed instances is 1440 (once per day), and in Cloud it's 15 (every 15 minutes). The lowest interval you can set is 1 (once per minute). Set this to 0 to disable automatic schema refreshes. |
| **Launcher** | | |
| WORKLOAD_LAUNCHER_PARALLELISM | workloadLauncher.parallelism | Defines the number of jobs that can be started at once. Defaults to 10. |
| **Data Retention** | | |
| TEMPORAL_HISTORY_RETENTION_IN_DAYS | Use extraEnvs | Defines the retention period of the job history in Temporal. Defaults to 30 days. |
| **Server** | | |
| AUDIT_LOGGING_ENABLED | server.auditLoggingEnabled | For Self-Managed Enterprise only, defines whether Airbyte enables audit logging. Set to `true` or `false`. If `true`, specify `STORAGE_BUCKET_AUDIT_LOGGING`. |
| STORAGE_BUCKET_AUDIT_LOGGING | server.auditLoggingBucket | For Self-Managed Enterprise only, if `AUDIT_LOGGING_ENABLED` is true, define your audit logging bucket here. You must configure a blob storage solution, like AWS S3, Google Cloud Storage, or Azure Blob Storage. |
| HTTP_IDLE_TIMEOUT | server.httpIdleTimeout | Defines the HTTP idle timeout for the server. |
| READ_TIMEOUT | Use extraEnvs | Defines the read timeout for the server. |
| **Authentication** | | |
| AB_INSTANCE_ADMIN_PASSWORD | global.auth.instanceAdmin.password | Defines the instance admin password. |
| AB_AUTH_SECRET_CREATION_ENABLED | global.auth.secretCreationEnabled | Defines whether auth secret creation is enabled. |
| AB_KUBERNETES_SECRET_NAME | global.auth.managedSecretName | Defines the Kubernetes secret name for auth. |
| AB_INSTANCE_ADMIN_CLIENT_ID | global.auth.instanceAdmin.clientId | Defines the instance admin client ID. |
| AB_INSTANCE_ADMIN_CLIENT_SECRET | global.auth.instanceAdmin.clientSecret | Defines the instance admin client secret. |
| AB_JWT_SIGNATURE_SECRET | global.auth.security.jwtSignatureSecret | Defines the JWT signature secret. |
| AB_COOKIE_SECURE | global.auth.security.cookieSecureSetting | Defines the cookie secure setting. |
| INITIAL_USER_FIRST_NAME | global.auth.instanceAdmin.firstName | Defines the initial user's first name. |
| INITIAL_USER_LAST_NAME | global.auth.instanceAdmin.lastName | Defines the initial user's last name. |
| INITIAL_USER_EMAIL | global.auth.instanceAdmin.email | Defines the initial user's email. |
| INITIAL_USER_PASSWORD | global.auth.instanceAdmin.password | Defines the initial user's password. |
| **Tracking** | | |
| TRACKING_ENABLED | global.tracking.enabled | Defines whether tracking is enabled. |
| TRACKING_STRATEGY | global.tracking.strategy | Defines the tracking strategy (logging or segment). |
| **Enterprise** | | |
| AIRBYTE_LICENSE_KEY | global.enterprise.licenseKey | Defines the Airbyte license key for enterprise features. |
| **Feature Flags** | | |
| FEATURE_FLAG_CLIENT | global.featureFlags.client | Defines the feature flag client type. |
| LAUNCHDARKLY_KEY | global.featureFlags.launchDarkly.sdkKey | Defines the LaunchDarkly SDK key. |
| **Java** | | |
| JAVA_TOOL_OPTIONS | global.java.opts | Defines Java tool options. |
| **Temporal** | | |
| AUTO_SETUP | temporal.autoSetup | Defines whether Temporal auto-setup is enabled. |
| TEMPORAL_CLI_ADDRESS | global.temporal.cli.address | Defines the Temporal CLI address. |
| TEMPORAL_CLOUD_ENABLED | global.temporal.cloud.enabled | Defines whether Temporal Cloud is enabled. |
| TEMPORAL_CLOUD_HOST | global.temporal.cloud.host | Defines the Temporal Cloud host. |
| TEMPORAL_CLOUD_NAMESPACE | global.temporal.cloud.namespace | Defines the Temporal Cloud namespace. |
| TEMPORAL_CLOUD_CLIENT_CERT | global.temporal.cloud.clientCert | Defines the Temporal Cloud client certificate. |
| TEMPORAL_CLOUD_CLIENT_KEY | global.temporal.cloud.clientKey | Defines the Temporal Cloud client key. |
| **Container Orchestrator** | | |
| CONTAINER_ORCHESTRATOR_SECRET_NAME | global.workloads.containerOrchestrator.secretName | Defines the secret name for the container orchestrator. |
| CONTAINER_ORCHESTRATOR_SECRET_MOUNT_PATH | global.workloads.containerOrchestrator.secretMountPath | Defines the secret mount path for the container orchestrator. |
| CONTAINER_ORCHESTRATOR_DATA_PLANE_CREDS_SECRET_NAME | global.workloads.containerOrchestrator.dataPlane.credentialsSecretName | Defines the data plane credentials secret name. |
| CONTAINER_ORCHESTRATOR_IMAGE | global.workloads.containerOrchestrator.image | Defines the container orchestrator image. |
| **Workload Launcher** | | |
| WORKLOAD_LAUNCHER_PARALLELISM | workloadLauncher.parallelism | Defines the workload launcher parallelism. |
| CONNECTOR_PROFILER_IMAGE | workloadLauncher.connectorProfiler.image | Defines the connector profiler image. |
| WORKLOAD_INIT_IMAGE | workloadLauncher.workloadInit.image | Defines the workload init image. |
| **Connector Registry** | | |
| CONNECTOR_REGISTRY_SEED_PROVIDER | global.connectorRegistry.seedProvider | Defines the connector registry seed provider. |
| CONNECTOR_REGISTRY_BASE_URL | global.connectorRegistry.baseUrl | Defines the connector registry base URL. |
| **AI Assist** | | |
| AI_ASSIST_URL_BASE | connectorBuilderServer.aiAssistUrlBase | Defines the AI assist URL base. |
| AI_ASSIST_API_KEY | connectorBuilderServer.aiAssistApiKey | Defines the AI assist API key. |
| **Connector Rollout** | | |
| CONNECTOR_ROLLOUT_EXPIRATION_SECONDS | global.connectorRollout.expirationSeconds | Defines the connector rollout expiration in seconds. |
| CONNECTOR_ROLLOUT_PARALLELISM | global.connectorRollout.parallelism | Defines the connector rollout parallelism. |
| CONNECTOR_ROLLOUT_GITHUB_AIRBYTE_PAT | connectorRolloutWorker.githubToken | Defines the GitHub personal access token for connector rollout. |
| **Customer.io** | | |
| CUSTOMERIO_API_KEY | global.customerio.apiKey | Defines the Customer.io API key. |
| **Shopify** | | |
| SHOPIFY_CLIENT_ID | global.shopify.clientId | Defines the Shopify client ID. |
| SHOPIFY_CLIENT_SECRET | global.shopify.clientSecret | Defines the Shopify client secret. |
| **Keycloak** | | |
| KEYCLOAK_ADMIN_USER | keycloak.auth.adminUsername | Defines the Keycloak admin username. |
| KEYCLOAK_ADMIN_PASSWORD | keycloak.auth.adminPassword | Defines the Keycloak admin password. |
| KEYCLOAK_ADMIN_REALM | keycloak.auth.adminRealm | Defines the Keycloak admin realm. |
| KEYCLOAK_INTERNAL_REALM_ISSUER | keycloak.realmIssuer | Defines the Keycloak internal realm issuer. |
| **MinIO** | | |
| MINIO_ROOT_USER | minio.rootUser | Defines the MinIO root user. |
| MINIO_ROOT_PASSWORD | minio.rootPassword | Defines the MinIO root password. |
| **Micronaut** | | |
| MICRONAUT_ENVIRONMENTS | global.micronaut.environments | Defines the Micronaut environments. |
| **Topology** | | |
| NODE_SELECTOR_LABEL | global.topology.nodeSelectorLabel | Defines the node selector label for topology. |
| QUICK_JOBS_NODE_SELECTOR_LABEL | global.topology.quickJobsNodeSelectorLabel | Defines the quick jobs node selector label. |
| **Workloads** | | |
| CONNECTOR_SPECIFIC_RESOURCE_DEFAULTS_ENABLED | global.workloads.resources.useConnectorResourceDefaults | Defines whether connector-specific resource defaults are enabled. |
| DATA_CHECK_TASK_QUEUES | global.workloads.queues.check | Defines the data check task queues. |
