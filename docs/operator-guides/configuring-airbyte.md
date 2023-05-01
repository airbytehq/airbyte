# Configuring Airbyte

This section covers how to configure Airbyte, and the various configuration Airbyte accepts.

Configuration is currently via environment variables. See the below section on how to modify these variables.

## Docker Deployments

The recommended way to run an Airbyte Docker deployment is via the Airbyte repo's `docker-compose.yaml` and `.env` file.

To configure the default Airbyte Docker deployment, modify the bundled `.env` file. The `docker-compose.yaml` file injects appropriate variables into
the containers.

If you want to manage your own docker files, please refer to Airbyte's docker file to ensure applications get the correct variables.

## Kubernetes Deployments

The recommended way to run an Airbyte Kubernetes deployment is via the `Kustomize` overlays.

We recommend using the overlays in the `stable` directory as these have preset resource limits.

To configure the default Airbyte Kubernetes deployment, modify the `.env` in the respective directory. Each application will consume the appropriate
env var from a generated configmap.

If you want to manage your own Kube manifests, please refer to the various `Kustomize` overlays for examples.

## Reference

The following are the possible configuration options organised by deployment type and services.

Internal-only variables have been omitted for clarity. See `Configs.java` for a full list.

Be careful using variables marked as `alpha` as they aren't meant for public consumption.

### Shared

The following variables are relevant to both Docker and Kubernetes.

#### Core

1. `AIRBYTE_VERSION` - Defines the Airbyte deployment version.
2. `SPEC_CACHE_BUCKET` - Defines the bucket for caching specs. This immensely speeds up spec operations. This is updated when new versions are published.
3. `WORKER_ENVIRONMENT` - Defines if the deployment is Docker or Kubernetes. Airbyte behaves accordingly.
4. `CONFIG_ROOT` - Defines the configs directory. Applies only to Docker, and is present in Kubernetes for backward compatibility.
5. `WORKSPACE_ROOT` - Defines the Airbyte workspace directory. Applies only to Docker, and is present in Kubernetes for backward compatibility.

#### Access

Set to empty values, e.g. "" to disable basic auth. **Be sure to change these values**.

1. BASIC_AUTH_USERNAME=airbyte
2. BASIC_AUTH_PASSWORD=password
3. BASIC_AUTH_PROXY_TIMEOUT=600 - Defines the proxy timeout time for requests to Airbyte Server. Main use should be for dynamic discover when creating a connection (S3, JDBC, etc) that takes a long time.

#### Secrets

1. `SECRET_PERSISTENCE` - Defines the Secret Persistence type. Defaults to NONE. Set to GOOGLE_SECRET_MANAGER to use Google Secret Manager. Set to AWS_SECRET_MANAGER to use AWS Secret Manager. Set to TESTING_CONFIG_DB_TABLE to use the database as a test. Set to VAULT to use Hashicorp Vault, currently only the token based authentication is supported. Alpha support. Undefined behavior will result if this is turned on and then off.
2. `SECRET_STORE_GCP_PROJECT_ID` - Defines the GCP Project to store secrets in. Alpha support.
3. `SECRET_STORE_GCP_CREDENTIALS` - Define the JSON credentials used to read/write Airbyte Configuration to Google Secret Manager. These credentials must have Secret Manager Read/Write access. Alpha support.
4. `VAULT_ADDRESS` - Define the vault address to read/write Airbyte Configuration to Hashicorp Vault. Alpha Support.
5. `VAULT_PREFIX` - Define the vault path prefix. Empty by default. Alpha Support.
6. `VAULT_AUTH_TOKEN` - The token used for vault authentication. Alpha Support.
7. `VAULT_AUTH_METHOD` - How vault will preform authentication. Currently, only supports Token auth. Defaults to token. Alpha Support.
8. `AWS_ACCESS_KEY` - Defines the aws_access_key_id from the AWS credentials to use for AWS Secret Manager.
9. `AWS_SECRET_ACCESS_KEY`- Defines aws_secret_access_key to use for the AWS Secret Manager.

#### Database

1. `DATABASE_USER` - Define the Jobs Database user.
2. `DATABASE_PASSWORD` - Define the Jobs Database password.
3. `DATABASE_URL` - Define the Jobs Database url in the form of `jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT/${DATABASE_DB}`. Do not include username or password.
4. `JOBS_DATABASE_INITIALIZATION_TIMEOUT_MS` - Define the total time to wait for the Jobs Database to be initialized. This includes migrations.
5. `CONFIG_DATABASE_USER` - Define the Configs Database user. Defaults to the Jobs Database user if empty.
6. `CONFIG_DATABASE_PASSWORD` - Define the Configs Database password. Defaults to the Jobs Database password if empty.
7. `CONFIG_DATABASE_URL` - Define the Configs Database url in the form of `jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT/${DATABASE_DB}`. Defaults to the Jobs Database url if empty.
8. `CONFIG_DATABASE_INITIALIZATION_TIMEOUT_MS` - Define the total time to wait for the Configs Database to be initialized. This includes migrations.
9. `RUN_DATABASE_MIGRATION_ON_STARTUP` - Define if the Bootloader should run migrations on start up.

#### Airbyte Services

1. `TEMPORAL_HOST` - Define the url where Temporal is hosted at. Please include the port. Airbyte services use this information.
2. `INTERNAL_API_HOST` - Define the url where the Airbyte Server is hosted at. Please include the port. Airbyte services use this information.
3. `WEBAPP_URL` - Define the url the Airbyte Webapp is hosted at. Please include the port. Airbyte services use this information.

#### Jobs

1. `SYNC_JOB_MAX_ATTEMPTS` - Define the number of attempts a sync will attempt before failing.
2. `SYNC_JOB_MAX_TIMEOUT_DAYS` - Define the number of days a sync job will execute for before timing out.
3. `JOB_MAIN_CONTAINER_CPU_REQUEST` - Define the job container's minimum CPU usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.
4. `JOB_MAIN_CONTAINER_CPU_LIMIT` - Define the job container's maximum CPU usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.
5. `JOB_MAIN_CONTAINER_MEMORY_REQUEST` - Define the job container's minimum RAM usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.
6. `JOB_MAIN_CONTAINER_MEMORY_LIMIT` - Define the job container's maximum RAM usage. Units follow either Docker or Kubernetes, depending on the deployment. Defaults to none.

#### Logging

1. `LOG_LEVEL` - Define log levels. Defaults to INFO. This value is expected to be one of the various Log4J log levels.

#### Monitoring

1. `PUBLISH_METRICS` - Define whether to publish metrics collected by the Metrics Reporter. Defaults to false.
2. `METRIC_CLIENT` - Defines which metrics client to use. Only relevant if `PUBLISH_METRICS` is set to true. Accepts either `datadog` or `otel`. Default to none.
3. `DD_AGENT_HOST` - Defines the ip the Datadog metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `datadog`. Defaults to none.
4. `DD_AGENT_PORT` - Defines the port the Datadog metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `datadog`. Defaults to none.
5. `OTEL_COLLECTOR_ENDPOIN` - Define the ip:port the OTEL metric client sends metrics to. Only relevant if `METRIC_CLIENT` is set to `otel`. Defaults to none.

#### Worker

1. `MAX_SPEC_WORKERS` - Define the maximum number of Spec workers each Airbyte Worker container can support. Defaults to 5.
2. `MAX_CHECK_WORKERS` - Define the maximum number of Check workers each Airbyte Worker container can support. Defaults to 5.
3. `MAX_SYNC_WORKERS` - Define the maximum number of Sync workers each Airbyte Worker container can support. Defaults to 5.
4. `MAX_DISCOVER_WORKERS` - Define the maximum number of Discover workers each Airbyte Worker container can support. Defaults to 5.
5. `SENTRY_DSN` - Define the [DSN](https://docs.sentry.io/product/sentry-basics/dsn-explainer/) of necessary Sentry instance. Defaults to empty. Integration with Sentry is explained [here](./sentry-integration.md)

#### Data Retention

1. `TEMPORAL_HISTORY_RETENTION_IN_DAYS` - Define the retention period of the job history in Temporal, defaults to 30 days. When running in docker, 
   this same value is applied to the log retention.

### Docker-Only

1. `WORKSPACE_DOCKER_MOUNT` - Defines the name of the Airbyte docker volume.
2. `DOCKER_NETWORK` - Defines the docker network the new Scheduler launches jobs on.
3. `LOCAL_DOCKER_MOUNT` - Defines the name of the docker mount that is used for local file handling. On Docker, this allows connector pods to interact with a volume for "local file" operations.

### Kubernetes-Only

#### Jobs

1. `JOB_KUBE_TOLERATIONS` - Define one or more Job pod tolerations. Tolerations are separated by ';'. Each toleration contains k=v pairs mentioning some/all of key, effect, operator and value and separated by `,`.
2. `JOB_KUBE_NODE_SELECTORS` - Define one or more Job pod node selectors. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`. It is the pod node selectors of the sync job and the default pod node selectors fallback for others jobs.
3. `JOB_KUBE_ANNOTATIONS` - Define one or more Job pod annotations. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`. It is the pod annotations of the sync job and the default pod annotations fallback for others jobs.
4. `JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY` - Define the Job pod connector image pull policy.
5. `JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET` - Define the Job pod connector image pull secret. Useful when hosting private images.
6. `JOB_KUBE_SIDECAR_CONTAINER_IMAGE_PULL_POLICY` - Define the image pull policy on the sidecar containers in the Job pod. Useful when there are cluster policies enforcing to always pull.
7. `JOB_KUBE_SOCAT_IMAGE` - Define the Job pod socat image.
8. `JOB_KUBE_BUSYBOX_IMAGE` - Define the Job pod busybox image.
9. `JOB_KUBE_CURL_IMAGE` - Define the Job pod curl image pull.
10. `JOB_KUBE_NAMESPACE` - Define the Kubernetes namespace Job pods are created in.

#### Jobs specific

A job specific variable overwrites the default sync job variable defined above.

1. `SPEC_JOB_KUBE_NODE_SELECTORS` - Define one or more pod node selectors for the spec job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
2. `CHECK_JOB_KUBE_NODE_SELECTORS` - Define one or more pod node selectors for the check job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
3. `DISCOVER_JOB_KUBE_NODE_SELECTORS` - Define one or more pod node selectors for the discover job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
4. `SPEC_JOB_KUBE_ANNOTATIONS` - Define one or more pod annotations for the spec job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
5. `CHECK_JOB_KUBE_ANNOTATIONS` - Define one or more pod annotations for the check job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`
6. `DISCOVER_JOB_KUBE_ANNOTATIONS` - Define one or more pod annotations for the discover job. Each k=v pair is separated by a `,`. For example: `key1=value1,key2=value2`

#### Worker

1. `TEMPORAL_WORKER_PORTS` - Define the local ports the Airbyte Worker pod uses to connect to the various Job pods. Port 9001 - 9040 are exposed by default in the Kustomize deployments.

#### Logging

Note that Airbyte does not support logging to separate Cloud Storage providers.

Please see [here](https://docs.airbyte.com/deploying-airbyte/on-kubernetes#configure-logs) for more information on configuring Kubernetes logging.

1. `GCS_LOG_BUCKET` - Define the GCS bucket to store logs.
2. `S3_BUCKET` - Define the S3 bucket to store logs.
3. `S3_RREGION` - Define the S3 region the S3 log bucket is in.
4. `S3_AWS_KEY` - Define the key used to access the S3 log bucket.
5. `S3_AWS_SECRET` - Define the secret used to access the S3 log bucket.
6. `S3_MINIO_ENDPOINT` - Define the url Minio is hosted at so Airbyte can use Minio to store logs.
7. `S3_PATH_STYLE_ACCESS` - Set to `true` if using Minio to store logs. Empty otherwise.
