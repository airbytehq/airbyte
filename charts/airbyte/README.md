# airbyte

![Version: 0.39.36](https://img.shields.io/badge/Version-0.39.36-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.40.3](https://img.shields.io/badge/AppVersion-0.39.41--alpha-informational?style=flat-square)

Helm chart to deploy airbyte

## Requirements

| Repository                               | Name               | Version     |
| ---------------------------------------- | ------------------ | ----------- |
| https://airbytehq.github.io/helm-charts/ | airbyte-bootloader | placeholder |
| https://airbytehq.github.io/helm-charts/ | pod-sweeper        | placeholder |
| https://airbytehq.github.io/helm-charts/ | server             | placeholder |
| https://airbytehq.github.io/helm-charts/ | temporal           | placeholder |
| https://airbytehq.github.io/helm-charts/ | webapp             | placeholder |
| https://airbytehq.github.io/helm-charts/ | worker             | placeholder |
| https://charts.bitnami.com/bitnami       | common             | 1.x.x       |
| https://charts.bitnami.com/bitnami       | minio              | 11.x.x      |
| https://charts.bitnami.com/bitnami       | postgresql         | 10.x.x      |

## Values

| Key                                                | Type   | Default                     | Description |
| -------------------------------------------------- | ------ | --------------------------- | ----------- |
| airbyte-bootloader.affinity                        | object | `{}`                        |             |
| airbyte-bootloader.enabled                         | bool   | `true`                      |             |
| airbyte-bootloader.image.pullPolicy                | string | `"IfNotPresent"`            |             |
| airbyte-bootloader.image.repository                | string | `"airbyte/bootloader"`      |             |
| airbyte-bootloader.image.tag                       | string | `"0.40.3"`                  |             |
| airbyte-bootloader.nodeSelector                    | object | `{}`                        |             |
| airbyte-bootloader.podAnnotations                  | object | `{}`                        |             |
| airbyte-bootloader.resources.limits                | object | `{}`                        |             |
| airbyte-bootloader.resources.requests              | object | `{}`                        |             |
| airbyte-bootloader.tolerations                     | list   | `[]`                        |             |
| externalDatabase.database                          | string | `"db-airbyte"`              |             |
| externalDatabase.existingSecret                    | string | `""`                        |             |
| externalDatabase.existingSecretPasswordKey         | string | `""`                        |             |
| externalDatabase.host                              | string | `"localhost"`               |             |
| externalDatabase.password                          | string | `""`                        |             |
| externalDatabase.port                              | int    | `5432`                      |             |
| externalDatabase.user                              | string | `"airbyte"`                 |             |
| fullnameOverride                                   | string | `""`                        |             |
| global.database.host                               | string | `"test"`                    |             |
| global.database.port                               | string | `"5432"`                    |             |
| global.database.secretValue                        | string | `""`                        |             |
| global.deploymentMode                              | string | `"oss"`                     |             |
| global.imageRegistry                               | string | `""`                        |             |
| global.jobs.kube.annotations                       | object | `{}`                        |             |
| global.jobs.kube.main_container_image_pull_secret  | string | `""`                        |             |
| global.jobs.kube.nodeSelector                      | object | `{}`                        |             |
| global.jobs.kube.tolerations                       | list   | `[]`                        |             |
| global.jobs.resources.limits                       | object | `{}`                        |             |
| global.jobs.resources.requests                     | object | `{}`                        |             |
| global.logs.accessKey.existingSecret               | string | `""`                        |             |
| global.logs.accessKey.existingSecretKey            | string | `""`                        |             |
| global.logs.accessKey.password                     | string | `""`                        |             |
| global.logs.externalMinio.enabled                  | bool   | `false`                     |             |
| global.logs.externalMinio.host                     | string | `"localhost"`               |             |
| global.logs.externalMinio.port                     | int    | `9000`                      |             |
| global.logs.gcs.bucket                             | string | `""`                        |             |
| global.logs.gcs.credentials                        | string | `""`                        |             |
| global.logs.gcs.credentialsJson                    | string | `""`                        |             |
| global.logs.minio.enabled                          | bool   | `true`                      |             |
| global.logs.s3.bucket                              | string | `"airbyte-dev-logs"`        |             |
| global.logs.s3.bucketRegion                        | string | `""`                        |             |
| global.logs.s3.enabled                             | bool   | `false`                     |             |
| global.logs.secretKey.existingSecret               | string | `""`                        |             |
| global.logs.secretKey.existingSecretKey            | string | `""`                        |             |
| global.logs.secretKey.password                     | string | `""`                        |             |
| global.secretName                                  | string | `"airbyte-secrets"`         |             |
| global.serviceAccountName                          | string | `"airbyte-admin"`           |             |
| minio.auth.rootPassword                            | string | `"minio123"`                |             |
| minio.auth.rootUser                                | string | `"minio"`                   |             |
| nameOverride                                       | string | `""`                        |             |
| pod-sweeper.affinity                               | object | `{}`                        |             |
| pod-sweeper.containerSecurityContext               | object | `{}`                        |             |
| pod-sweeper.enabled                                | bool   | `true`                      |             |
| pod-sweeper.extraVolumeMounts                      | list   | `[]`                        |             |
| pod-sweeper.extraVolumes                           | list   | `[]`                        |             |
| pod-sweeper.image.pullPolicy                       | string | `"IfNotPresent"`            |             |
| pod-sweeper.image.repository                       | string | `"bitnami/kubectl"`         |             |
| pod-sweeper.image.tag                              | string | `"latest"`                  |             |
| pod-sweeper.livenessProbe.enabled                  | bool   | `true`                      |             |
| pod-sweeper.livenessProbe.failureThreshold         | int    | `3`                         |             |
| pod-sweeper.livenessProbe.initialDelaySeconds      | int    | `5`                         |             |
| pod-sweeper.livenessProbe.periodSeconds            | int    | `30`                        |             |
| pod-sweeper.livenessProbe.successThreshold         | int    | `1`                         |             |
| pod-sweeper.livenessProbe.timeoutSeconds           | int    | `1`                         |             |
| pod-sweeper.nodeSelector                           | object | `{}`                        |             |
| pod-sweeper.podAnnotations                         | object | `{}`                        |             |
| pod-sweeper.readinessProbe.enabled                 | bool   | `true`                      |             |
| pod-sweeper.readinessProbe.failureThreshold        | int    | `3`                         |             |
| pod-sweeper.readinessProbe.initialDelaySeconds     | int    | `5`                         |             |
| pod-sweeper.readinessProbe.periodSeconds           | int    | `30`                        |             |
| pod-sweeper.readinessProbe.successThreshold        | int    | `1`                         |             |
| pod-sweeper.readinessProbe.timeoutSeconds          | int    | `1`                         |             |
| pod-sweeper.resources.limits                       | object | `{}`                        |             |
| pod-sweeper.resources.requests                     | object | `{}`                        |             |
| pod-sweeper.tolerations                            | list   | `[]`                        |             |
| postgresql.commonAnnotations."helm.sh/hook"        | string | `"pre-install,pre-upgrade"` |             |
| postgresql.commonAnnotations."helm.sh/hook-weight" | string | `"-1"`                      |             |
| postgresql.containerSecurityContext.runAsNonRoot   | bool   | `true`                      |             |
| postgresql.enabled                                 | bool   | `true`                      |             |
| postgresql.existingSecret                          | string | `""`                        |             |
| postgresql.postgresqlDatabase                      | string | `"db-airbyte"`              |             |
| postgresql.postgresqlPassword                      | string | `"airbyte"`                 |             |
| postgresql.postgresqlUsername                      | string | `"airbyte"`                 |             |
| server.affinity                                    | object | `{}`                        |             |
| server.containerSecurityContext                    | object | `{}`                        |             |
| server.enabled                                     | bool   | `true`                      |             |
| server.extraEnv                                    | list   | `[]`                        |             |
| server.extraVolumeMounts                           | list   | `[]`                        |             |
| server.extraVolumes                                | list   | `[]`                        |             |
| server.image.pullPolicy                            | string | `"IfNotPresent"`            |             |
| server.image.repository                            | string | `"airbyte/server"`          |             |
| server.image.tag                                   | string | `"0.40.3"`                  |             |
| server.livenessProbe.enabled                       | bool   | `true`                      |             |
| server.livenessProbe.failureThreshold              | int    | `3`                         |             |
| server.livenessProbe.initialDelaySeconds           | int    | `30`                        |             |
| server.livenessProbe.periodSeconds                 | int    | `10`                        |             |
| server.livenessProbe.successThreshold              | int    | `1`                         |             |
| server.livenessProbe.timeoutSeconds                | int    | `1`                         |             |
| server.log.level                                   | string | `"INFO"`                    |             |
| server.nodeSelector                                | object | `{}`                        |             |
| server.podAnnotations                              | object | `{}`                        |             |
| server.readinessProbe.enabled                      | bool   | `true`                      |             |
| server.readinessProbe.failureThreshold             | int    | `3`                         |             |
| server.readinessProbe.initialDelaySeconds          | int    | `10`                        |             |
| server.readinessProbe.periodSeconds                | int    | `10`                        |             |
| server.readinessProbe.successThreshold             | int    | `1`                         |             |
| server.readinessProbe.timeoutSeconds               | int    | `1`                         |             |
| server.replicaCount                                | int    | `1`                         |             |
| server.resources.limits                            | object | `{}`                        |             |
| server.resources.requests                          | object | `{}`                        |             |
| server.service.port                                | int    | `8001`                      |             |
| server.service.type                                | string | `"ClusterIP"`               |             |
| server.tolerations                                 | list   | `[]`                        |             |
| serviceAccount.annotations                         | object | `{}`                        |             |
| serviceAccount.create                              | bool   | `true`                      |             |
| serviceAccount.name                                | string | `"airbyte-admin"`           |             |
| temporal.affinity                                  | object | `{}`                        |             |
| temporal.containerSecurityContext                  | object | `{}`                        |             |
| temporal.enabled                                   | bool   | `true`                      |             |
| temporal.extraEnv                                  | list   | `[]`                        |             |
| temporal.extraInitContainers                       | list   | `[]`                        |             |
| temporal.extraVolumeMounts                         | list   | `[]`                        |             |
| temporal.extraVolumes                              | list   | `[]`                        |             |
| temporal.image.pullPolicy                          | string | `"IfNotPresent"`            |             |
| temporal.image.repository                          | string | `"temporalio/auto-setup"`   |             |
| temporal.image.tag                                 | string | `"1.13.0"`                  |             |
| temporal.livenessProbe.enabled                     | bool   | `true`                      |             |
| temporal.livenessProbe.failureThreshold            | int    | `3`                         |             |
| temporal.livenessProbe.initialDelaySeconds         | int    | `5`                         |             |
| temporal.livenessProbe.periodSeconds               | int    | `30`                        |             |
| temporal.livenessProbe.successThreshold            | int    | `1`                         |             |
| temporal.livenessProbe.timeoutSeconds              | int    | `1`                         |             |
| temporal.nodeSelector                              | object | `{}`                        |             |
| temporal.podAnnotations                            | object | `{}`                        |             |
| temporal.readinessProbe.enabled                    | bool   | `true`                      |             |
| temporal.readinessProbe.failureThreshold           | int    | `3`                         |             |
| temporal.readinessProbe.initialDelaySeconds        | int    | `5`                         |             |
| temporal.readinessProbe.periodSeconds              | int    | `30`                        |             |
| temporal.readinessProbe.successThreshold           | int    | `1`                         |             |
| temporal.readinessProbe.timeoutSeconds             | int    | `1`                         |             |
| temporal.replicaCount                              | int    | `1`                         |             |
| temporal.resources.limits                          | object | `{}`                        |             |
| temporal.resources.requests                        | object | `{}`                        |             |
| temporal.service.port                              | int    | `7233`                      |             |
| temporal.service.type                              | string | `"ClusterIP"`               |             |
| temporal.tolerations                               | list   | `[]`                        |             |
| version                                            | string | `""`                        |             |
| webapp.affinity                                    | object | `{}`                        |             |
| webapp.api.url                                     | string | `"/api/v1/"`                |             |
| webapp.containerSecurityContext                    | object | `{}`                        |             |
| webapp.enabled                                     | bool   | `true`                      |             |
| webapp.extraEnv                                    | list   | `[]`                        |             |
| webapp.extraVolumeMounts                           | list   | `[]`                        |             |
| webapp.extraVolumes                                | list   | `[]`                        |             |
| webapp.fullstory.enabled                           | bool   | `false`                     |             |
| webapp.image.pullPolicy                            | string | `"IfNotPresent"`            |             |
| webapp.image.repository                            | string | `"airbyte/webapp"`          |             |
| webapp.image.tag                                   | string | `"0.40.3"`                  |             |
| webapp.ingress.annotations                         | object | `{}`                        |             |
| webapp.ingress.className                           | string | `""`                        |             |
| webapp.ingress.enabled                             | bool   | `false`                     |             |
| webapp.ingress.hosts                               | list   | `[]`                        |             |
| webapp.ingress.tls                                 | list   | `[]`                        |             |
| webapp.livenessProbe.enabled                       | bool   | `true`                      |             |
| webapp.livenessProbe.failureThreshold              | int    | `3`                         |             |
| webapp.livenessProbe.initialDelaySeconds           | int    | `30`                        |             |
| webapp.livenessProbe.periodSeconds                 | int    | `10`                        |             |
| webapp.livenessProbe.successThreshold              | int    | `1`                         |             |
| webapp.livenessProbe.timeoutSeconds                | int    | `1`                         |             |
| webapp.nodeSelector                                | object | `{}`                        |             |
| webapp.podAnnotations                              | object | `{}`                        |             |
| webapp.readinessProbe.enabled                      | bool   | `true`                      |             |
| webapp.readinessProbe.failureThreshold             | int    | `3`                         |             |
| webapp.readinessProbe.initialDelaySeconds          | int    | `10`                        |             |
| webapp.readinessProbe.periodSeconds                | int    | `10`                        |             |
| webapp.readinessProbe.successThreshold             | int    | `1`                         |             |
| webapp.readinessProbe.timeoutSeconds               | int    | `1`                         |             |
| webapp.replicaCount                                | int    | `1`                         |             |
| webapp.resources.limits                            | object | `{}`                        |             |
| webapp.resources.requests                          | object | `{}`                        |             |
| webapp.service.annotations                         | object | `{}`                        |             |
| webapp.service.port                                | int    | `80`                        |             |
| webapp.service.type                                | string | `"ClusterIP"`               |             |
| webapp.tolerations                                 | list   | `[]`                        |             |
| worker.affinity                                    | object | `{}`                        |             |
| worker.containerSecurityContext                    | object | `{}`                        |             |
| worker.enabled                                     | bool   | `true`                      |             |
| worker.extraEnv                                    | list   | `[]`                        |             |
| worker.extraVolumeMounts                           | list   | `[]`                        |             |
| worker.extraVolumes                                | list   | `[]`                        |             |
| worker.image.pullPolicy                            | string | `"IfNotPresent"`            |             |
| worker.image.repository                            | string | `"airbyte/worker"`          |             |
| worker.image.tag                                   | string | `"0.40.3"`                  |             |
| worker.livenessProbe.enabled                       | bool   | `true`                      |             |
| worker.livenessProbe.failureThreshold              | int    | `3`                         |             |
| worker.livenessProbe.initialDelaySeconds           | int    | `30`                        |             |
| worker.livenessProbe.periodSeconds                 | int    | `10`                        |             |
| worker.livenessProbe.successThreshold              | int    | `1`                         |             |
| worker.livenessProbe.timeoutSeconds                | int    | `1`                         |             |
| worker.log.level                                   | string | `"INFO"`                    |             |
| worker.nodeSelector                                | object | `{}`                        |             |
| worker.podAnnotations                              | object | `{}`                        |             |
| worker.readinessProbe.enabled                      | bool   | `true`                      |             |
| worker.readinessProbe.failureThreshold             | int    | `3`                         |             |
| worker.readinessProbe.initialDelaySeconds          | int    | `10`                        |             |
| worker.readinessProbe.periodSeconds                | int    | `10`                        |             |
| worker.readinessProbe.successThreshold             | int    | `1`                         |             |
| worker.readinessProbe.timeoutSeconds               | int    | `1`                         |             |
| worker.replicaCount                                | int    | `1`                         |             |
| worker.resources.limits                            | object | `{}`                        |             |
| worker.resources.requests                          | object | `{}`                        |             |
| worker.tolerations                                 | list   | `[]`                        |             |

---

Autogenerated from chart metadata using [helm-docs v1.11.0](https://github.com/norwoodj/helm-docs/releases/v1.11.0)
