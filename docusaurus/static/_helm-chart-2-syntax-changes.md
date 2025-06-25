| Helm chart V1                                                        | Helm chart V2                                          |
| -------------------------------------------------------------------- | ------------------------------------------------------ |
| `global.database.database`                                           | `global.database.name`                                 |
| `workload-launcher`                                                  | `workloadLauncher`                                     |
| `airbyte-bootloader`                                                 | `airbyteBootloader`                                    |
| `orchestrator`                                                       | `containerOrchestrator`                                |
| `workload-launcher.extraEnvs[JOB_KUBE_NODE_SELECTORS]`               | `global.jobs.kube.nodeSelector`                        |
| `workload-launcher.extraEnvs[CHECK_JOB_KUBE_NODE_SELECTORS]`         | `global.jobs.kube.scheduling.check.nodeSelectors`      |
| `workload-launcher.extraEnvs[DISCOVER_JOB_KUBE_NODE_SELECTORS]`      | `global.jobs.kube.scheduling.discover.nodeSelectors`   |
| `worker.extraEnvs[MAX_SYNC_WORKERS]`                                 | `worker.maxSyncWorkers`                                |
| `worker.extraEnvs[MAX_CHECK_WORKERS]`                                | `worker.maxCheckWorkers`                               |
| `server.extraEnvs[HTTP_IDLE_TIMEOUT]`                                | `server.httpIdleTimeout`                               |
| `global.env_vars[TRACKING_STRATEGY]`                                 | `global.tracking.strategy`                             |
| `server.env_vars[AUDIT_LOGGING_ENABLED]`                             | `server.auditLoggingEnabled`                           |
| `global.env_vars[STORAGE_BUCKET_AUDIT_LOGGING]`                      | `global.storage.bucket.auditLogging`                   |
| `global.env_vars[JOB_MAIN_CONTAINER_CPU_REQUEST]`                    | `global.workloads.resources.mainContainer.cpu.request` |
| `orchestrator.nodeSelector`                                          | `global.jobs.kube.nodeSelector`                        |
| Individual bucket env vars (`S3_LOG_BUCKET`, `GCS_LOG_BUCKET`, etc.) | `global.storage.bucket.log`                            |
| `STORAGE_BUCKET_STATE`                                               | `global.storage.bucket.state`                          |
| `STORAGE_BUCKET_WORKLOAD_OUTPUT`                                     | `global.storage.bucket.workloadOutput`                 |
| `STORAGE_BUCKET_ACTIVITY_PAYLOAD`                                    | `global.storage.bucket.activityPayload`                |
