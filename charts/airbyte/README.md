# airbyte

Helm charts for Airbyte.

## Parameters

### Global Parameters

| Name                   | Description                  | Value |
| ---------------------- | ---------------------------- | ----- |
| `global.imageRegistry` | Global Docker image registry | `""`  |


### Common Parameters

| Name                         | Description                                                                                                         | Value           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------- | --------------- |
| `nameOverride`               | String to partially override airbyte.fullname template with a string (will prepend the release name)                | `""`            |
| `fullnameOverride`           | String to fully override airbyte.fullname template with a string                                                    | `""`            |
| `serviceAccount.annotations` | Annotations for service account. Evaluated as a template. Only used if `create` is `true`.                          | `{}`            |
| `serviceAccount.create`      | Specifies whether a ServiceAccount should be created                                                                | `true`          |
| `serviceAccount.name`        | Name of the service account to use. If not set and create is true, a name is generated using the fullname template. | `airbyte-admin` |
| `version`                    | Sets the AIRBYTE_VERSION environment variable. Defaults to Chart.AppVersion.                                        | `""`            |


### Webapp Parameters

| Name                                        | Description                                                      | Value            |
| ------------------------------------------- | ---------------------------------------------------------------- | ---------------- |
| `webapp.replicaCount`                       | Number of webapp replicas                                        | `1`              |
| `webapp.image.repository`                   | The repository to use for the airbyte webapp image.              | `airbyte/webapp` |
| `webapp.image.pullPolicy`                   | the pull policy to use for the airbyte webapp image              | `IfNotPresent`   |
| `webapp.image.tag`                          | The airbyte webapp image tag. Defaults to the chart's AppVersion | `0.39.29-alpha`  |
| `webapp.podAnnotations`                     | Add extra annotations to the webapp pod(s)                       | `{}`             |
| `webapp.containerSecurityContext`           | Security context for the container                               | `{}`             |
| `webapp.livenessProbe.enabled`              | Enable livenessProbe on the webapp                               | `true`           |
| `webapp.livenessProbe.initialDelaySeconds`  | Initial delay seconds for livenessProbe                          | `30`             |
| `webapp.livenessProbe.periodSeconds`        | Period seconds for livenessProbe                                 | `10`             |
| `webapp.livenessProbe.timeoutSeconds`       | Timeout seconds for livenessProbe                                | `1`              |
| `webapp.livenessProbe.failureThreshold`     | Failure threshold for livenessProbe                              | `3`              |
| `webapp.livenessProbe.successThreshold`     | Success threshold for livenessProbe                              | `1`              |
| `webapp.readinessProbe.enabled`             | Enable readinessProbe on the webapp                              | `true`           |
| `webapp.readinessProbe.initialDelaySeconds` | Initial delay seconds for readinessProbe                         | `10`             |
| `webapp.readinessProbe.periodSeconds`       | Period seconds for readinessProbe                                | `10`             |
| `webapp.readinessProbe.timeoutSeconds`      | Timeout seconds for readinessProbe                               | `1`              |
| `webapp.readinessProbe.failureThreshold`    | Failure threshold for readinessProbe                             | `3`              |
| `webapp.readinessProbe.successThreshold`    | Success threshold for readinessProbe                             | `1`              |
| `webapp.service.type`                       | The service type to use for the webapp service                   | `ClusterIP`      |
| `webapp.service.port`                       | The service port to expose the webapp on                         | `80`             |
| `webapp.service.annotations`                | Annotations for the webapp service resource                      | `{}`             |
| `webapp.resources.limits`                   | The resources limits for the Web container                       | `{}`             |
| `webapp.resources.requests`                 | The requested resources for the Web container                    | `{}`             |
| `webapp.nodeSelector`                       | Node labels for pod assignment                                   | `{}`             |
| `webapp.tolerations`                        | Tolerations for webapp pod assignment.                           | `[]`             |
| `webapp.affinity`                           | Affinity and anti-affinity for webapp pod assignment.            | `{}`             |
| `webapp.ingress.enabled`                    | Set to true to enable ingress record generation                  | `false`          |
| `webapp.ingress.className`                  | Specifies ingressClassName for clusters >= 1.18+                 | `""`             |
| `webapp.ingress.annotations`                | Ingress annotations done as key:value pairs                      | `{}`             |
| `webapp.ingress.hosts`                      | The list of hostnames to be covered with this ingress record.    | `[]`             |
| `webapp.ingress.tls`                        | Custom ingress TLS configuration                                 | `[]`             |
| `webapp.api.url`                            | The webapp API url.                                              | `/api/v1/`       |
| `webapp.isDemo`                             | Set to true if this is a demo                                    | `false`          |
| `webapp.fullstory.enabled`                  | Whether or not to enable fullstory                               | `false`          |
| `webapp.extraEnv`                           | Additional env vars for webapp pod(s).                           | `[]`             |
| `webapp.extraVolumeMounts`                  | Additional volumeMounts for webapp container(s).                 | `[]`             |
| `webapp.extraVolumes`                       | Additional volumes for webapp pod(s).                            | `[]`             |


### Pod Sweeper parameters

| Name                                            | Description                                               | Value             |
| ----------------------------------------------- | --------------------------------------------------------- | ----------------- |
| `podSweeper.image.repository`                   | The image repository to use for the pod sweeper           | `bitnami/kubectl` |
| `podSweeper.image.pullPolicy`                   | The pull policy for the pod sweeper image                 | `IfNotPresent`    |
| `podSweeper.image.tag`                          | The pod sweeper image tag to use                          | `latest`          |
| `podSweeper.podAnnotations`                     | Add extra annotations to the podSweeper pod               | `{}`              |
| `podSweeper.containerSecurityContext`           | Security context for the container                        | `{}`              |
| `podSweeper.livenessProbe.enabled`              | Enable livenessProbe on the podSweeper                    | `true`            |
| `podSweeper.livenessProbe.initialDelaySeconds`  | Initial delay seconds for livenessProbe                   | `5`               |
| `podSweeper.livenessProbe.periodSeconds`        | Period seconds for livenessProbe                          | `30`              |
| `podSweeper.livenessProbe.timeoutSeconds`       | Timeout seconds for livenessProbe                         | `1`               |
| `podSweeper.livenessProbe.failureThreshold`     | Failure threshold for livenessProbe                       | `3`               |
| `podSweeper.livenessProbe.successThreshold`     | Success threshold for livenessProbe                       | `1`               |
| `podSweeper.readinessProbe.enabled`             | Enable readinessProbe on the podSweeper                   | `true`            |
| `podSweeper.readinessProbe.initialDelaySeconds` | Initial delay seconds for readinessProbe                  | `5`               |
| `podSweeper.readinessProbe.periodSeconds`       | Period seconds for readinessProbe                         | `30`              |
| `podSweeper.readinessProbe.timeoutSeconds`      | Timeout seconds for readinessProbe                        | `1`               |
| `podSweeper.readinessProbe.failureThreshold`    | Failure threshold for readinessProbe                      | `3`               |
| `podSweeper.readinessProbe.successThreshold`    | Success threshold for readinessProbe                      | `1`               |
| `podSweeper.resources.limits`                   | The resources limits for the podSweeper container         | `{}`              |
| `podSweeper.resources.requests`                 | The requested resources for the podSweeper container      | `{}`              |
| `podSweeper.nodeSelector`                       | Node labels for pod assignment                            | `{}`              |
| `podSweeper.tolerations`                        | Tolerations for podSweeper pod assignment.                | `[]`              |
| `podSweeper.affinity`                           | Affinity and anti-affinity for podSweeper pod assignment. | `{}`              |
| `podSweeper.extraVolumeMounts`                  | Additional volumeMounts for podSweeper container(s).      | `[]`              |
| `podSweeper.extraVolumes`                       | Additional volumes for podSweeper pod(s).                 | `[]`              |


### Server parameters

| Name                                        | Description                                                      | Value            |
| ------------------------------------------- | ---------------------------------------------------------------- | ---------------- |
| `server.replicaCount`                       | Number of server replicas                                        | `1`              |
| `server.image.repository`                   | The repository to use for the airbyte server image.              | `airbyte/server` |
| `server.image.pullPolicy`                   | the pull policy to use for the airbyte server image              | `IfNotPresent`   |
| `server.image.tag`                          | The airbyte server image tag. Defaults to the chart's AppVersion | `0.39.29-alpha`  |
| `server.podAnnotations`                     | Add extra annotations to the server pod                          | `{}`             |
| `server.containerSecurityContext`           | Security context for the container                               | `{}`             |
| `server.livenessProbe.enabled`              | Enable livenessProbe on the server                               | `true`           |
| `server.livenessProbe.initialDelaySeconds`  | Initial delay seconds for livenessProbe                          | `30`             |
| `server.livenessProbe.periodSeconds`        | Period seconds for livenessProbe                                 | `10`             |
| `server.livenessProbe.timeoutSeconds`       | Timeout seconds for livenessProbe                                | `1`              |
| `server.livenessProbe.failureThreshold`     | Failure threshold for livenessProbe                              | `3`              |
| `server.livenessProbe.successThreshold`     | Success threshold for livenessProbe                              | `1`              |
| `server.readinessProbe.enabled`             | Enable readinessProbe on the server                              | `true`           |
| `server.readinessProbe.initialDelaySeconds` | Initial delay seconds for readinessProbe                         | `10`             |
| `server.readinessProbe.periodSeconds`       | Period seconds for readinessProbe                                | `10`             |
| `server.readinessProbe.timeoutSeconds`      | Timeout seconds for readinessProbe                               | `1`              |
| `server.readinessProbe.failureThreshold`    | Failure threshold for readinessProbe                             | `3`              |
| `server.readinessProbe.successThreshold`    | Success threshold for readinessProbe                             | `1`              |
| `server.resources.limits`                   | The resources limits for the server container                    | `{}`             |
| `server.resources.requests`                 | The requested resources for the server container                 | `{}`             |
| `server.service.type`                       | The service type to use for the API server                       | `ClusterIP`      |
| `server.service.port`                       | The service port to expose the API server on                     | `8001`           |
| `server.nodeSelector`                       | Node labels for pod assignment                                   | `{}`             |
| `server.tolerations`                        | Tolerations for server pod assignment.                           | `[]`             |
| `server.affinity`                           | Affinity and anti-affinity for server pod assignment.            | `{}`             |
| `server.log.level`                          | The log level to log at                                          | `INFO`           |
| `server.extraEnv`                           | Additional env vars for server pod(s).                           | `[]`             |
| `server.extraVolumeMounts`                  | Additional volumeMounts for server container(s).                 | `[]`             |
| `server.extraVolumes`                       | Additional volumes for server pod(s).                            | `[]`             |


### Worker Parameters

| Name                                        | Description                                                      | Value            |
| ------------------------------------------- | ---------------------------------------------------------------- | ---------------- |
| `worker.replicaCount`                       | Number of worker replicas                                        | `1`              |
| `worker.image.repository`                   | The repository to use for the airbyte worker image.              | `airbyte/worker` |
| `worker.image.pullPolicy`                   | the pull policy to use for the airbyte worker image              | `IfNotPresent`   |
| `worker.image.tag`                          | The airbyte worker image tag. Defaults to the chart's AppVersion | `0.39.29-alpha`  |
| `worker.podAnnotations`                     | Add extra annotations to the worker pod(s)                       | `{}`             |
| `worker.containerSecurityContext`           | Security context for the container                               | `{}`             |
| `worker.livenessProbe.enabled`              | Enable livenessProbe on the worker                               | `true`           |
| `worker.livenessProbe.initialDelaySeconds`  | Initial delay seconds for livenessProbe                          | `30`             |
| `worker.livenessProbe.periodSeconds`        | Period seconds for livenessProbe                                 | `10`             |
| `worker.livenessProbe.timeoutSeconds`       | Timeout seconds for livenessProbe                                | `1`              |
| `worker.livenessProbe.failureThreshold`     | Failure threshold for livenessProbe                              | `3`              |
| `worker.livenessProbe.successThreshold`     | Success threshold for livenessProbe                              | `1`              |
| `worker.readinessProbe.enabled`             | Enable readinessProbe on the worker                              | `true`           |
| `worker.readinessProbe.initialDelaySeconds` | Initial delay seconds for readinessProbe                         | `10`             |
| `worker.readinessProbe.periodSeconds`       | Period seconds for readinessProbe                                | `10`             |
| `worker.readinessProbe.timeoutSeconds`      | Timeout seconds for readinessProbe                               | `1`              |
| `worker.readinessProbe.failureThreshold`    | Failure threshold for readinessProbe                             | `3`              |
| `worker.readinessProbe.successThreshold`    | Success threshold for readinessProbe                             | `1`              |
| `worker.resources.limits`                   | The resources limits for the worker container                    | `{}`             |
| `worker.resources.requests`                 | The requested resources for the worker container                 | `{}`             |
| `worker.nodeSelector`                       | Node labels for pod assignment                                   | `{}`             |
| `worker.tolerations`                        | Tolerations for worker pod assignment.                           | `[]`             |
| `worker.affinity`                           | Affinity and anti-affinity for worker pod assignment.            | `{}`             |
| `worker.log.level`                          | The log level to log at.                                         | `INFO`           |
| `worker.extraEnv`                           | Additional env vars for worker pod(s).                           | `[]`             |
| `worker.extraVolumeMounts`                  | Additional volumeMounts for worker container(s).                 | `[]`             |
| `worker.extraVolumes`                       | Additional volumes for worker pod(s).                            | `[]`             |


### Bootloader Parameters

| Name                            | Description                                                          | Value                |
| ------------------------------- | -------------------------------------------------------------------- | -------------------- |
| `bootloader.image.repository`   | The repository to use for the airbyte bootloader image.              | `airbyte/bootloader` |
| `bootloader.image.pullPolicy`   | the pull policy to use for the airbyte bootloader image              | `IfNotPresent`       |
| `bootloader.image.tag`          | The airbyte bootloader image tag. Defaults to the chart's AppVersion | `0.39.29-alpha`      |
| `bootloader.podAnnotations`     | Add extra annotations to the bootloader pod                          | `{}`                 |
| `bootloader.nodeSelector`       | Node labels for pod assignment                                       | `{}`                 |
| `bootloader.tolerations`        | Tolerations for worker pod assignment.                               | `[]`                 |
| `bootloader.resources.limits`   | The resources limits for the airbyte bootloader image                | `{}`                 |
| `bootloader.resources.requests` | The requested resources for the airbyte bootloader image             | `{}`                 |
| `bootloader.affinity`           | Affinity and anti-affinity for bootloader pod assignment.            | `{}`                 |


### Temporal parameters

| Name                                          | Description                                             | Value                   |
| --------------------------------------------- | ------------------------------------------------------- | ----------------------- |
| `temporal.replicaCount`                       | The number of temporal replicas to deploy               | `1`                     |
| `temporal.image.repository`                   | The temporal image repository to use                    | `temporalio/auto-setup` |
| `temporal.image.pullPolicy`                   | The pull policy for the temporal image                  | `IfNotPresent`          |
| `temporal.image.tag`                          | The temporal image tag to use                           | `1.7.0`                 |
| `temporal.service.type`                       | The Kubernetes Service Type                             | `ClusterIP`             |
| `temporal.service.port`                       | The temporal port and exposed kubernetes port           | `7233`                  |
| `temporal.podAnnotations`                     | Add extra annotations to the temporal pod               | `{}`                    |
| `temporal.containerSecurityContext`           | Security context for the container                      | `{}`                    |
| `temporal.extraInitContainers`                | Additional InitContainers to initialize the pod         | `[]`                    |
| `temporal.livenessProbe.enabled`              | Enable livenessProbe on the temporal                    | `true`                  |
| `temporal.livenessProbe.initialDelaySeconds`  | Initial delay seconds for livenessProbe                 | `5`                     |
| `temporal.livenessProbe.periodSeconds`        | Period seconds for livenessProbe                        | `30`                    |
| `temporal.livenessProbe.timeoutSeconds`       | Timeout seconds for livenessProbe                       | `1`                     |
| `temporal.livenessProbe.failureThreshold`     | Failure threshold for livenessProbe                     | `3`                     |
| `temporal.livenessProbe.successThreshold`     | Success threshold for livenessProbe                     | `1`                     |
| `temporal.readinessProbe.enabled`             | Enable readinessProbe on the temporal                   | `true`                  |
| `temporal.readinessProbe.initialDelaySeconds` | Initial delay seconds for readinessProbe                | `5`                     |
| `temporal.readinessProbe.periodSeconds`       | Period seconds for readinessProbe                       | `30`                    |
| `temporal.readinessProbe.timeoutSeconds`      | Timeout seconds for readinessProbe                      | `1`                     |
| `temporal.readinessProbe.failureThreshold`    | Failure threshold for readinessProbe                    | `3`                     |
| `temporal.readinessProbe.successThreshold`    | Success threshold for readinessProbe                    | `1`                     |
| `temporal.nodeSelector`                       | Node labels for temporal pod assignment                 | `{}`                    |
| `temporal.tolerations`                        | Tolerations for temporal pod assignment.                | `[]`                    |
| `temporal.affinity`                           | Affinity and anti-affinity for temporal pod assignment. | `{}`                    |
| `temporal.extraEnv`                           | Additional env vars for temporal pod(s).                | `[]`                    |
| `temporal.extraVolumeMounts`                  | Additional volumeMounts for temporal container(s).      | `[]`                    |
| `temporal.extraVolumes`                       | Additional volumes for temporal pod(s).                 | `[]`                    |
| `temporal.resources.limits`                   | The resources limits for temporal pod(s)                | `{}`                    |
| `temporal.resources.requests`                 | The requested resources for temporal pod(s)             | `{}`                    |


### Airbyte Database parameters

| Name                                               | Description                                                                               | Value                     |
| -------------------------------------------------- | ----------------------------------------------------------------------------------------- | ------------------------- |
| `postgresql.enabled`                               | Switch to enable or disable the PostgreSQL helm chart                                     | `true`                    |
| `postgresql.postgresqlUsername`                    | Airbyte Postgresql username                                                               | `airbyte`                 |
| `postgresql.postgresqlPassword`                    | Airbyte Postgresql password                                                               | `airbyte`                 |
| `postgresql.postgresqlDatabase`                    | Airbyte Postgresql database                                                               | `db-airbyte`              |
| `postgresql.existingSecret`                        | Name of an existing secret containing the PostgreSQL password ('postgresql-password' key) | `""`                      |
| `postgresql.containerSecurityContext.runAsNonRoot` | Ensures the container will run with a non-root user                                       | `true`                    |
| `postgresql.commonAnnotations.helm.sh/hook`        | It will determine when the hook should be rendered                                        | `pre-install,pre-upgrade` |
| `postgresql.commonAnnotations.helm.sh/hook-weight` | The order in which the hooks are executed. If weight is lower, it has higher priority     | `-1`                      |
| `externalDatabase.host`                            | Database host                                                                             | `localhost`               |
| `externalDatabase.user`                            | non-root Username for Airbyte Database                                                    | `airbyte`                 |
| `externalDatabase.password`                        | Database password                                                                         | `""`                      |
| `externalDatabase.existingSecret`                  | Name of an existing secret resource containing the DB password                            | `""`                      |
| `externalDatabase.existingSecretPasswordKey`       | Name of an existing secret key containing the DB password                                 | `""`                      |
| `externalDatabase.database`                        | Database name                                                                             | `db-airbyte`              |
| `externalDatabase.port`                            | Database port number                                                                      | `5432`                    |


### Logs parameters

| Name                               | Description                                            | Value              |
| ---------------------------------- | ------------------------------------------------------ | ------------------ |
| `logs.accessKey.password`          | Logs Access Key                                        | `minio`            |
| `logs.accessKey.existingSecret`    |                                                        | `""`               |
| `logs.accessKey.existingSecretKey` |                                                        | `""`               |
| `logs.secretKey.password`          | Logs Secret Key                                        | `minio123`         |
| `logs.secretKey.existingSecret`    |                                                        | `""`               |
| `logs.secretKey.existingSecretKey` |                                                        | `""`               |
| `logs.minio.enabled`               | Switch to enable or disable the Minio helm chart       | `true`             |
| `logs.externalMinio.enabled`       | Switch to enable or disable an external Minio instance | `false`            |
| `logs.externalMinio.host`          | External Minio Host                                    | `localhost`        |
| `logs.externalMinio.port`          | External Minio Port                                    | `9000`             |
| `logs.s3.enabled`                  | Switch to enable or disable custom S3 Log location     | `false`            |
| `logs.s3.bucket`                   | Bucket name where logs should be stored                | `airbyte-dev-logs` |
| `logs.s3.bucketRegion`             | Region of the bucket (must be empty if using minio)    | `""`               |
| `logs.gcs.bucket`                  | GCS bucket name                                        | `""`               |
| `logs.gcs.credentials`             | The path the GCS creds are written to                  | `""`               |
| `logs.gcs.credentialsJson`         | Base64 encoded json GCP credentials file contents      | `""`               |


### Minio chart overwrites

| Name                                         | Description                                  | Value      |
| -------------------------------------------- | -------------------------------------------- | ---------- |
| `minio.accessKey.password`                   | Minio Access Key                             | `minio`    |
| `minio.secretKey.password`                   | Minio Secret Key                             | `minio123` |
| `jobs.resources.limits`                      | The resources limits for jobs                | `{}`       |
| `jobs.resources.requests`                    | The requested resources for jobs             | `{}`       |
| `jobs.kube.annotations`                      | key/value annotations applied to kube jobs   | `{}`       |
| `jobs.kube.nodeSelector`                     | key/value node selector applied to kube jobs | `{}`       |
| `jobs.kube.tolerations`                      | Tolerations for jobs.kube pod assignment.    | `[]`       |
| `jobs.kube.main_container_image_pull_secret` | image pull secret to use for job pod         | `""`       |
