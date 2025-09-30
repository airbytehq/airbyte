Here is a complete list of environment variables with their Helm chart V2 equivalent. Some environment variables don't have direct V2 equivalents, so you can set these using the `extraEnv` configuration in the appropriate service section.

| Environment variable                                      | Helm chart V2 equivalent                                               
| --------------------------------------------------------- | ---------------------------------------------------------------------- 
| **Core**                                                  |                                                                        
| AIRBYTE_VERSION                                           | global.version                                                         
| AIRBYTE_EDITION                                           | global.edition                                                         
| AIRBYTE_CLUSTER_TYPE                                      | global.cluster.type                                                    
| AIRBYTE_CLUSTER_NAME                                      | global.cluster.name                                                    
| AIRBYTE_URL                                               | global.airbyteUrl                                                      
| AIRBYTE_API_HOST                                          | global.api.host                                                        
| AIRBYTE_API_AUTH_HEADER_NAME                              | global.api.authHeaderName                                              
| AIRBYTE_API_AUTH_HEADER_VALUE                             | global.api.authHeaderValue                                             
| AIRBYTE_SERVER_HOST                                       | global.server.host                                                     
| API_AUTHORIZATION_ENABLED                                 | global.auth.enabled                                                    
| CONNECTOR_BUILDER_SERVER_API_HOST                         | global.connectorBuilderServer.apiHost                                  
| DEPLOYMENT_ENV                                            | global.deploymentEnv                                                   
| INTERNAL_API_HOST                                         | global.api.internalHost                                                
| LOCAL                                                     | global.local                                                           
| WEBAPP_URL                                                | global.webapp.url                                                      
| SPEC_CACHE_BUCKET                                         | Use extraEnvs                                                          
| **Secrets**                                               |                                                                        
| SECRET_PERSISTENCE                                        | global.secretsManager.type                                             
| SECRET_STORE_GCP_PROJECT_ID                               | global.secretsManager.googleSecretManager.projectId                    
| SECRET_STORE_GCP_CREDENTIALS                              | global.secretsManager.googleSecretManager.credentials                  
| VAULT_ADDRESS                                             | global.secretsManager.vault.address                                    
| VAULT_PREFIX                                              | global.secretsManager.vault.prefix                                     
| VAULT_AUTH_TOKEN                                          | global.secretsManager.vault.token                                      
| VAULT_AUTH_METHOD                                         | global.secretsManager.vault.authMethod                                 
| AWS_ACCESS_KEY                                            | global.aws.accessKeyId                                                 
| AWS_SECRET_ACCESS_KEY                                     | global.aws.secretAccessKey                                             
| AWS_KMS_KEY_ARN                                           | global.secretsManager.awsSecretManager.kmsKeyArn                       
| AWS_SECRET_MANAGER_SECRET_TAGS                            | global.secretsManager.awsSecretManager.tags                            
| AWS_ASSUME_ROLE_ACCESS_KEY_ID                             | global.aws.assumeRole.accessKeyId                                      
| **Database**                                              |                                                                        
| DATABASE_USER                                             | global.database.user                                                   
| DATABASE_PASSWORD                                         | global.database.password                                               
| DATABASE_URL                                              | global.database.url                                                    
| DATABASE_HOST                                             | global.database.host                                                   
| DATABASE_PORT                                             | global.database.port                                                   
| DATABASE_DB                                               | global.database.database                                               
| JOBS_DATABASE_INITIALIZATION_TIMEOUT_MS                   | global.database.initializationTimeoutMs                                
| CONFIG_DATABASE_USER                                      | global.database.user                                                   
| CONFIG_DATABASE_PASSWORD                                  | global.database.password                                               
| CONFIG_DATABASE_URL                                       | global.database.url                                                    
| CONFIG_DATABASE_INITIALIZATION_TIMEOUT_MS                 | global.database.initializationTimeoutMs                                
| RUN_DATABASE_MIGRATION_ON_STARTUP                         | global.migrations.runAtStartup                                         
| USE_CLOUD_SQL_PROXY                                       | global.cloudSqlProxy.enabled                                           
| **Airbyte Services**                                      |                                                                        
| TEMPORAL_HOST                                             | temporal.host                                                          
| **Jobs**                                                  |                                                                        
| SYNC_JOB_MAX_ATTEMPTS                                     | Use extraEnvs                                                          
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_MAX_SUCCESSIVE         | Use extraEnvs                                                          
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_MAX_TOTAL              | Use extraEnvs                                                          
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_MIN_INTERVAL_S | Use extraEnvs                                                          
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_MAX_INTERVAL_S | Use extraEnvs                                                          
| SYNC_JOB_RETRIES_COMPLETE_FAILURES_BACKOFF_BASE           | Use extraEnvs                                                          
| SYNC_JOB_RETRIES_PARTIAL_FAILURES_MAX_SUCCESSIVE          | Use extraEnvs                                                          
| SYNC_JOB_RETRIES_PARTIAL_FAILURES_MAX_TOTAL               | Use extraEnvs                                                          
| SYNC_JOB_MAX_TIMEOUT_DAYS                                 | Use extraEnvs                                                          
| JOB_MAIN_CONTAINER_CPU_REQUEST                            | global.workloads.resources.mainContainer.cpu.request                   
| JOB_MAIN_CONTAINER_CPU_LIMIT                              | global.workloads.resources.mainContainer.cpu.limit                     
| JOB_MAIN_CONTAINER_MEMORY_REQUEST                         | global.workloads.resources.mainContainer.memory.request                
| JOB_MAIN_CONTAINER_MEMORY_LIMIT                           | global.workloads.resources.mainContainer.memory.limit                  
| JOB_KUBE_TOLERATIONS                                      | global.jobs.kube.tolerations                                           
| JOB_KUBE_NODE_SELECTORS                                   | global.jobs.kube.nodeSelector                                          
| JOB_KUBE_ANNOTATIONS                                      | global.jobs.kube.annotations                                           
| JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY                 | global.jobs.kube.mainContainerImagePullPolicy                          
| JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET                 | global.jobs.kube.mainContainerImagePullSecret                          
| JOB_KUBE_SIDECAR_CONTAINER_IMAGE_PULL_POLICY              | global.jobs.kube.sidecarContainerImagePullPolicy                       
| JOB_KUBE_SOCAT_IMAGE                                      | global.jobs.kube.images.socat                                          
| JOB_KUBE_BUSYBOX_IMAGE                                    | global.jobs.kube.images.busybox                                        
| JOB_KUBE_CURL_IMAGE                                       | global.jobs.kube.images.curl                                           
| JOB_KUBE_NAMESPACE                                        | global.jobs.kube.namespace                                             
| JOB_KUBE_SERVICEACCOUNT                                   | global.jobs.kube.serviceAccount                                        
| **Jobs-specific**                                         |                                                                        
| SPEC_JOB_KUBE_NODE_SELECTORS                              | global.jobs.kube.scheduling.spec.nodeSelectors                         
| CHECK_JOB_KUBE_NODE_SELECTORS                             | global.jobs.kube.scheduling.check.nodeSelectors                        
| DISCOVER_JOB_KUBE_NODE_SELECTORS                          | global.jobs.kube.scheduling.discover.nodeSelectors                     
| SPEC_JOB_KUBE_ANNOTATIONS                                 | global.jobs.kube.scheduling.spec.annotations                           
| CHECK_JOB_KUBE_ANNOTATIONS                                | global.jobs.kube.scheduling.check.annotations                          
| DISCOVER_JOB_KUBE_ANNOTATIONS                             | global.jobs.kube.scheduling.discover.annotations                       
| **Connections**                                           |                                                                        
| MAX_FIELDS_PER_CONNECTION                                 | Use extraEnvs                                                          
| MAX_DAYS_OF_ONLY_FAILED_JOBS_BEFORE_CONNECTION_DISABLE    | Use extraEnvs                                                          
| MAX_FAILED_JOBS_IN_A_ROW_BEFORE_CONNECTION_DISABLE        | Use extraEnvs                                                          
| **Logging**                                               |                                                                        
| LOG_LEVEL                                                 | global.logging.level                                                   
| GCS_LOG_BUCKET                                            | global.storage.gcs.bucket                                              
| S3_BUCKET                                                 | global.storage.s3.bucket                                               
| S3_REGION                                                 | global.storage.s3.region                                               
| S3_AWS_KEY                                                | global.storage.s3.accessKeyId                                          
| S3_AWS_SECRET                                             | global.storage.s3.secretAccessKey                                      
| S3_MINIO_ENDPOINT                                         | global.storage.minio.endpoint                                          
| S3_PATH_STYLE_ACCESS                                      | global.storage.s3.pathStyleAccess                                      
| **Monitoring**                                            |                                                                        
| PUBLISH_METRICS                                           | global.metrics.enabled                                                 
| METRIC_CLIENT                                             | global.metrics.client                                                  
| DD_AGENT_HOST                                             | global.datadog.agentHost                                               
| DD_AGENT_PORT                                             | global.datadog.agentPort                                               
| OTEL_COLLECTOR_ENDPOINT                                   | global.metrics.otel.exporter.endpoint                                  
| MICROMETER_METRICS_ENABLED                                | global.metrics.enabled                                                 
| **Worker**                                                |                                                                        
| MAX_CHECK_WORKERS                                         | worker.maxCheckWorkers                                                 
| MAX_SYNC_WORKERS                                          | worker.maxSyncWorkers                                                  
| TEMPORAL_WORKER_PORTS                                     | worker.temporalWorkerPorts                                             
| DISCOVER_REFRESH_WINDOW_MINUTES                           | Use extraEnvs                                                          
| **Launcher**                                              |                                                                        
| WORKLOAD_LAUNCHER_PARALLELISM                             | workloadLauncher.parallelism                                           
| **Data Retention**                                        |                                                                        
| TEMPORAL_HISTORY_RETENTION_IN_DAYS                        | Use extraEnvs                                                          
| **Server**                                                |                                                                        
| AUDIT_LOGGING_ENABLED                                     | server.auditLoggingEnabled                                             
| STORAGE_BUCKET_AUDIT_LOGGING                              | server.auditLoggingBucket                                              
| HTTP_IDLE_TIMEOUT                                         | server.httpIdleTimeout                                                 
| READ_TIMEOUT                                              | Use extraEnvs                                                          
| **Authentication**                                        |                                                                        
| AB_INSTANCE_ADMIN_PASSWORD                                | global.auth.instanceAdmin.password                                     
| AB_AUTH_SECRET_CREATION_ENABLED                           | global.auth.secretCreationEnabled                                      
| AB_KUBERNETES_SECRET_NAME                                 | global.auth.managedSecretName                                          
| AB_INSTANCE_ADMIN_CLIENT_ID                               | global.auth.instanceAdmin.clientId                                     
| AB_INSTANCE_ADMIN_CLIENT_SECRET                           | global.auth.instanceAdmin.clientSecret                                 
| AB_JWT_SIGNATURE_SECRET                                   | global.auth.security.jwtSignatureSecret                                
| AB_COOKIE_SECURE                                          | global.auth.security.cookieSecureSetting                               
| INITIAL_USER_FIRST_NAME                                   | global.auth.instanceAdmin.firstName                                    
| INITIAL_USER_LAST_NAME                                    | global.auth.instanceAdmin.lastName                                     
| INITIAL_USER_EMAIL                                        | global.auth.instanceAdmin.email                                        
| INITIAL_USER_PASSWORD                                     | global.auth.instanceAdmin.password                                     
| **Tracking**                                              |                                                                        
| TRACKING_ENABLED                                          | global.tracking.enabled                                                
| TRACKING_STRATEGY                                         | global.tracking.strategy                                               
| **Enterprise**                                            |                                                                        
| AIRBYTE_LICENSE_KEY                                       | global.enterprise.licenseKey                                           
| **Feature Flags**                                         |                                                                        
| FEATURE_FLAG_CLIENT                                       | global.featureFlags.client                                             
| LAUNCHDARKLY_KEY                                          | global.featureFlags.launchDarkly.sdkKey                                
| **Java**                                                  |                                                                        
| JAVA_TOOL_OPTIONS                                         | global.java.opts                                                       
| **Temporal**                                              |                                                                        
| AUTO_SETUP                                                | temporal.autoSetup                                                     
| TEMPORAL_CLI_ADDRESS                                      | global.temporal.cli.address                                            
| TEMPORAL_CLOUD_ENABLED                                    | global.temporal.cloud.enabled                                          
| TEMPORAL_CLOUD_HOST                                       | global.temporal.cloud.host                                             
| TEMPORAL_CLOUD_NAMESPACE                                  | global.temporal.cloud.namespace                                        
| TEMPORAL_CLOUD_CLIENT_CERT                                | global.temporal.cloud.clientCert                                       
| TEMPORAL_CLOUD_CLIENT_KEY                                 | global.temporal.cloud.clientKey                                        
| **Container Orchestrator**                                |                                                                        
| CONTAINER_ORCHESTRATOR_SECRET_NAME                        | global.workloads.containerOrchestrator.secretName                      
| CONTAINER_ORCHESTRATOR_SECRET_MOUNT_PATH                  | global.workloads.containerOrchestrator.secretMountPath                 
| CONTAINER_ORCHESTRATOR_DATA_PLANE_CREDS_SECRET_NAME       | global.workloads.containerOrchestrator.dataPlane.credentialsSecretName 
| CONTAINER_ORCHESTRATOR_IMAGE                              | global.workloads.containerOrchestrator.image                           
| **Workload Launcher**                                     |                                                                        
| WORKLOAD_LAUNCHER_PARALLELISM                             | workloadLauncher.parallelism                                           
| CONNECTOR_PROFILER_IMAGE                                  | workloadLauncher.connectorProfiler.image                               
| WORKLOAD_INIT_IMAGE                                       | workloadLauncher.workloadInit.image                                    
| **Connector Registry**                                    |                                                                        
| CONNECTOR_REGISTRY_SEED_PROVIDER                          | global.connectorRegistry.seedProvider                                  
| CONNECTOR_REGISTRY_BASE_URL                               | global.connectorRegistry.baseUrl                                       
| **AI Assist**                                             |                                                                        
| AI_ASSIST_URL_BASE                                        | connectorBuilderServer.aiAssistUrlBase                                 
| AI_ASSIST_API_KEY                                         | connectorBuilderServer.aiAssistApiKey                                  
| **Connector Rollout**                                     |                                                                        
| CONNECTOR_ROLLOUT_EXPIRATION_SECONDS                      | global.connectorRollout.expirationSeconds                              
| CONNECTOR_ROLLOUT_PARALLELISM                             | global.connectorRollout.parallelism                                    
| CONNECTOR_ROLLOUT_GITHUB_AIRBYTE_PAT                      | connectorRolloutWorker.githubToken                                     
| **Customer.io**                                           |                                                                        
| CUSTOMERIO_API_KEY                                        | global.customerio.apiKey                                               
| **Shopify**                                               |                                                                        
| SHOPIFY_CLIENT_ID                                         | global.shopify.clientId                                                
| SHOPIFY_CLIENT_SECRET                                     | global.shopify.clientSecret                                            
| **Keycloak**                                              |                                                                        
| KEYCLOAK_ADMIN_USER                                       | keycloak.auth.adminUsername                                            
| KEYCLOAK_ADMIN_PASSWORD                                   | keycloak.auth.adminPassword                                            
| KEYCLOAK_ADMIN_REALM                                      | keycloak.auth.adminRealm                                               
| KEYCLOAK_INTERNAL_REALM_ISSUER                            | keycloak.realmIssuer                                                   
| **MinIO**                                                 |                                                                        
| MINIO_ROOT_USER                                           | minio.rootUser                                                         
| MINIO_ROOT_PASSWORD                                       | minio.rootPassword                                                     
| **Micronaut**                                             |                                                                        
| MICRONAUT_ENVIRONMENTS                                    | global.micronaut.environments                                          
| **Topology**                                              |                                                                        
| NODE_SELECTOR_LABEL                                       | global.topology.nodeSelectorLabel                                      
| QUICK_JOBS_NODE_SELECTOR_LABEL                            | global.topology.quickJobsNodeSelectorLabel                             
| **Workloads**                                             |                                                                        
| CONNECTOR_SPECIFIC_RESOURCE_DEFAULTS_ENABLED              | global.workloads.resources.useConnectorResourceDefaults                
| DATA_CHECK_TASK_QUEUES                                    | global.workloads.queues.check                                          
