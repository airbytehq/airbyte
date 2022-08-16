/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.storage.CloudStorageConfigs;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * This interface defines the general variables for configuring Airbyte.
 * <p>
 * Please update the configuring-airbyte.md document when modifying this file.
 * <p>
 * Please also add one of the following tags to the env var accordingly:
 * <p>
 * 1. 'Internal-use only' if a var is mainly for Airbyte-only configuration. e.g. tracking, test or
 * Cloud related etc.
 * <p>
 * 2. 'Alpha support' if a var does not have proper support and should be used with care.
 */

@SuppressWarnings("PMD.BooleanGetMethodName")
public interface Configs {

  // CORE
  // General
  /**
   * Distinguishes internal Airbyte deployments. Internal-use only.
   */
  String getAirbyteRole();

  /**
   * Defines the Airbyte deployment version.
   */
  AirbyteVersion getAirbyteVersion();

  String getAirbyteVersionOrWarning();

  /**
   * Defines the bucket for caching specs. This immensely speeds up spec operations. This is updated
   * when new versions are published.
   */
  String getSpecCacheBucket();

  /**
   * Distinguishes internal Airbyte deployments. Internal-use only.
   */
  DeploymentMode getDeploymentMode();

  /**
   * Defines if the deployment is Docker or Kubernetes. Airbyte behaves accordingly.
   */
  WorkerEnvironment getWorkerEnvironment();

  /**
   * Defines the configs directory. Applies only to Docker, and is present in Kubernetes for backward
   * compatibility.
   */
  Path getConfigRoot();

  /**
   * Defines the Airbyte workspace directory. Applies only to Docker, and is present in Kubernetes for
   * backward compatibility.
   */
  Path getWorkspaceRoot();

  // Docker Only
  /**
   * Defines the name of the Airbyte docker volume.
   */
  String getWorkspaceDockerMount();

  /**
   * Defines the name of the docker mount that is used for local file handling. On Docker, this allows
   * connector pods to interact with a volume for "local file" operations.
   */
  String getLocalDockerMount();

  /**
   * Defines the docker network jobs are launched on with the new scheduler.
   */
  String getDockerNetwork();

  Path getLocalRoot();

  // Secrets
  /**
   * Defines the GCP Project to store secrets in. Alpha support.
   */
  String getSecretStoreGcpProjectId();

  /**
   * Define the JSON credentials used to read/write Airbyte Configuration to Google Secret Manager.
   * These credentials must have Secret Manager Read/Write access. Alpha support.
   */
  String getSecretStoreGcpCredentials();

  /**
   * Defines the Secret Persistence type. None by default. Set to GOOGLE_SECRET_MANAGER to use Google
   * Secret Manager. Set to TESTING_CONFIG_DB_TABLE to use the database as a test. Set to VAULT to use
   * Hashicorp Vault. Alpha support. Undefined behavior will result if this is turned on and then off.
   */
  SecretPersistenceType getSecretPersistenceType();

  /**
   * Define the vault address to read/write Airbyte Configuration to Hashicorp Vault. Alpha Support.
   */
  String getVaultAddress();

  /**
   * Define the vault path prefix to read/write Airbyte Configuration to Hashicorp Vault. Empty by
   * default. Alpha Support.
   */
  String getVaultPrefix();

  /**
   * Define the vault token to read/write Airbyte Configuration to Hashicorp Vault. Empty by default.
   * Alpha Support.
   */
  String getVaultToken();

  // Database
  /**
   * Define the Jobs Database user.
   */
  String getDatabaseUser();

  /**
   * Define the Jobs Database password.
   */
  String getDatabasePassword();

  /**
   * Define the Jobs Database url in the form of
   * jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT/${DATABASE_DB}. Do not include username or
   * password.
   */
  String getDatabaseUrl();

  /**
   * Define the minimum flyway migration version the Jobs Database must be at. If this is not
   * satisfied, applications will not successfully connect. Internal-use only.
   */
  String getJobsDatabaseMinimumFlywayMigrationVersion();

  /**
   * Define the total time to wait for the Jobs Database to be initialized. This includes migrations.
   */
  long getJobsDatabaseInitializationTimeoutMs();

  /**
   * Define the Configs Database user. Defaults to the Jobs Database user if empty.
   */
  String getConfigDatabaseUser();

  /**
   * Define the Configs Database password. Defaults to the Jobs Database password if empty.
   */
  String getConfigDatabasePassword();

  /**
   * Define the Configs Database url in the form of
   * jdbc:postgresql://${DATABASE_HOST}:${DATABASE_PORT/${DATABASE_DB}. Defaults to the Jobs Database
   * url if empty.
   */
  String getConfigDatabaseUrl();

  /**
   * Define the minimum flyway migration version the Configs Database must be at. If this is not
   * satisfied, applications will not successfully connect. Internal-use only.
   */
  String getConfigsDatabaseMinimumFlywayMigrationVersion();

  /**
   * Define the total time to wait for the Configs Database to be initialized. This includes
   * migrations.
   */
  long getConfigsDatabaseInitializationTimeoutMs();

  /**
   * Define if the Bootloader should run migrations on start up.
   */
  boolean runDatabaseMigrationOnStartup();

  // Temporal Cloud - Internal-Use Only

  /**
   * Define if Temporal Cloud should be used. Internal-use only.
   */
  boolean temporalCloudEnabled();

  /**
   * Temporal Cloud target endpoint, usually with form ${namespace}.tmprl.cloud:7233. Internal-use
   * only.
   */
  String getTemporalCloudHost();

  /**
   * Temporal Cloud namespace. Internal-use only.
   */
  String getTemporalCloudNamespace();

  /**
   * Temporal Cloud client cert for SSL. Internal-use only.
   */
  String getTemporalCloudClientCert();

  /**
   * Temporal Cloud client key for SSL. Internal-use only.
   */
  String getTemporalCloudClientKey();

  // Airbyte Services

  /**
   * Define the url where Temporal is hosted at. Please include the port. Airbyte services use this
   * information.
   */
  String getTemporalHost();

  /**
   * Define the number of retention days for the temporal history
   */
  int getTemporalRetentionInDays();

  /**
   * Define the url where the Airbyte Server is hosted at. Airbyte services use this information.
   * Manipulates the `INTERNAL_API_HOST` variable.
   */
  String getAirbyteApiHost();

  /**
   * Define the port where the Airbyte Server is hosted at. Airbyte services use this information.
   * Manipulates the `INTERNAL_API_HOST` variable.
   */
  int getAirbyteApiPort();

  /**
   * Define the url the Airbyte Webapp is hosted at. Airbyte services use this information.
   */
  String getWebappUrl();

  // Jobs
  /**
   * Define the number of attempts a sync will attempt before failing.
   */
  int getSyncJobMaxAttempts();

  /**
   * Define the number of days a sync job will execute for before timing out.
   */
  int getSyncJobMaxTimeoutDays();

  /**
   * Defines whether job creation uses connector-specific resource requirements when spawning jobs.
   * Works on both Docker and Kubernetes. Defaults to false for ease of use in OSS trials of Airbyte
   * but recommended for production deployments.
   */
  boolean connectorSpecificResourceDefaultsEnabled();

  /**
   * Define the job container's minimum CPU usage. Units follow either Docker or Kubernetes, depending
   * on the deployment. Defaults to none.
   */
  String getJobMainContainerCpuRequest();

  /**
   * Define the job container's maximum CPU usage. Units follow either Docker or Kubernetes, depending
   * on the deployment. Defaults to none.
   */
  String getJobMainContainerCpuLimit();

  /**
   * Define the job container's minimum RAM usage. Units follow either Docker or Kubernetes, depending
   * on the deployment. Defaults to none.
   */
  String getJobMainContainerMemoryRequest();

  /**
   * Define the job container's maximum RAM usage. Units follow either Docker or Kubernetes, depending
   * on the deployment. Defaults to none.
   */
  String getJobMainContainerMemoryLimit();

  /**
   * Get datadog or OTEL metric client for Airbyte to emit metrics. Allows empty value
   */
  String getMetricClient();

  /**
   * If choosing OTEL as the metric client, Airbyte will emit metrics and traces to this provided
   * endpoint.
   */
  String getOtelCollectorEndpoint();

  /**
   * Defines a default map of environment variables to use for any launched job containers. The
   * expected format is a JSON encoded String -> String map. Make sure to escape properly. Defaults to
   * an empty map.
   */
  Map<String, String> getJobDefaultEnvMap();

  /**
   * Defines the number of consecutive job failures required before a connection is auto-disabled if
   * the AUTO_DISABLE_FAILING_CONNECTIONS flag is set to true.
   */
  int getMaxFailedJobsInARowBeforeConnectionDisable();

  /**
   * Defines the required number of days with only failed jobs before a connection is auto-disabled if
   * the AUTO_DISABLE_FAILING_CONNECTIONS flag is set to true.
   */
  int getMaxDaysOfOnlyFailedJobsBeforeConnectionDisable();

  // Jobs - Kube only
  /**
   * Define the check job container's minimum CPU request. Defaults to
   * {@link #getJobMainContainerCpuRequest()} if not set. Internal-use only.
   */
  String getCheckJobMainContainerCpuRequest();

  /**
   * Define the check job container's maximum CPU usage. Defaults to
   * {@link #getJobMainContainerCpuLimit()} if not set. Internal-use only.
   */
  String getCheckJobMainContainerCpuLimit();

  /**
   * Define the check job container's minimum RAM usage. Defaults to
   * {@link #getJobMainContainerMemoryRequest()} if not set. Internal-use only.
   */
  String getCheckJobMainContainerMemoryRequest();

  /**
   * Define the check job container's maximum RAM usage. Defaults to
   * {@link #getJobMainContainerMemoryLimit()} if not set. Internal-use only.
   */
  String getCheckJobMainContainerMemoryLimit();

  /**
   * Define the normalization job container's minimum CPU request. Defaults to
   * {@link #getJobMainContainerCpuRequest()} if not set. Internal-use only.
   */
  String getNormalizationJobMainContainerCpuRequest();

  /**
   * Define the normalization job container's maximum CPU usage. Defaults to
   * {@link #getJobMainContainerCpuLimit()} if not set. Internal-use only.
   */
  String getNormalizationJobMainContainerCpuLimit();

  /**
   * Define the normalization job container's minimum RAM usage. Defaults to
   * {@link #getJobMainContainerMemoryRequest()} if not set. Internal-use only.
   */
  String getNormalizationJobMainContainerMemoryRequest();

  /**
   * Define the normalization job container's maximum RAM usage. Defaults to
   * {@link #getJobMainContainerMemoryLimit()} if not set. Internal-use only.
   */
  String getNormalizationJobMainContainerMemoryLimit();

  /**
   * Define one or more Job pod tolerations. Tolerations are separated by ';'. Each toleration
   * contains k=v pairs mentioning some/all of key, effect, operator and value and separated by `,`.
   */
  List<TolerationPOJO> getJobKubeTolerations();

  /**
   * Define one or more Job pod node selectors. Each kv-pair is separated by a `,`. Used for the sync
   * job and as fallback in case job specific (spec, check, discover) node selectors are not defined.
   */
  Map<String, String> getJobKubeNodeSelectors();

  /**
   * Define node selectors for Spec job pods specifically. Each kv-pair is separated by a `,`.
   */
  Map<String, String> getSpecJobKubeNodeSelectors();

  /**
   * Define node selectors for Check job pods specifically. Each kv-pair is separated by a `,`.
   */
  Map<String, String> getCheckJobKubeNodeSelectors();

  /**
   * Define node selectors for Discover job pods specifically. Each kv-pair is separated by a `,`.
   */
  Map<String, String> getDiscoverJobKubeNodeSelectors();

  /**
   * Define one or more Job pod annotations. Each kv-pair is separated by a `,`. Used for the sync job
   * and as fallback in case job specific (spec, check, discover) annotations are not defined.
   */
  Map<String, String> getJobKubeAnnotations();

  /**
   * Define annotations for Spec job pods specifically. Each kv-pair is separated by a `,`.
   */
  Map<String, String> getSpecJobKubeAnnotations();

  /**
   * Define annotations for Check job pods specifically. Each kv-pair is separated by a `,`.
   */
  Map<String, String> getCheckJobKubeAnnotations();

  /**
   * Define annotations for Discover job pods specifically. Each kv-pair is separated by a `,`.
   */
  Map<String, String> getDiscoverJobKubeAnnotations();

  /**
   * Define the Job pod connector image pull policy.
   */
  String getJobKubeMainContainerImagePullPolicy();

  /**
   * Define the Job pod connector sidecar image pull policy.
   */
  String getJobKubeSidecarContainerImagePullPolicy();

  /**
   * Define the Job pod connector image pull secret. Useful when hosting private images.
   */
  String getJobKubeMainContainerImagePullSecret();

  /**
   * Define the Job pod socat image.
   */
  String getJobKubeSocatImage();

  /**
   * Define the Job pod busybox image.
   */
  String getJobKubeBusyboxImage();

  /**
   * Define the Job pod curl image pull.
   */
  String getJobKubeCurlImage();

  /**
   * Define the Kubernetes namespace Job pods are created in.
   */
  String getJobKubeNamespace();

  // Logging/Monitoring/Tracking
  /**
   * Define either S3, Minio or GCS as a logging backend. Kubernetes only. Multiple variables are
   * involved here. Please see {@link CloudStorageConfigs} for more info.
   */
  LogConfigs getLogConfigs();

  /**
   * Defines the optional Google application credentials used for logging.
   */
  String getGoogleApplicationCredentials();

  /**
   * Define either S3, Minio or GCS as a state storage backend. Multiple variables are involved here.
   * Please see {@link CloudStorageConfigs} for more info.
   */
  CloudStorageConfigs getStateStorageCloudConfigs();

  /**
   * Determine if Datadog tracking events should be published. Mainly for Airbyte internal use.
   */
  boolean getPublishMetrics();

  /**
   * Set the Agent to publish Datadog metrics to. Only relevant if metrics should be published. Mainly
   * for Airbyte internal use.
   */
  String getDDAgentHost();

  /**
   * Set the port to publish Datadog metrics to. Only relevant if metrics should be published. Mainly
   * for Airbyte internal use.
   */
  String getDDDogStatsDPort();

  /**
   * Set constant tags to be attached to all metrics. Useful for distinguishing between environments.
   * Example: airbyte_instance:dev,k8s-cluster:aws-dev
   */
  List<String> getDDConstantTags();

  /**
   * Define whether to publish tracking events to Segment or log-only. Airbyte internal use.
   */
  TrackingStrategy getTrackingStrategy();

  /**
   * Define whether to send job failure events to Sentry or log-only. Airbyte internal use.
   */
  JobErrorReportingStrategy getJobErrorReportingStrategy();

  /**
   * Determines the Sentry DSN that should be used when reporting connector job failures to Sentry.
   * Used with SENTRY error reporting strategy. Airbyte internal use.
   */
  String getJobErrorReportingSentryDSN();

  // APPLICATIONS
  // Worker
  /**
   * Define the maximum number of workers each Airbyte Worker container supports. Multiple variables
   * are involved here. Please see {@link MaxWorkersConfig} for more info.
   */
  MaxWorkersConfig getMaxWorkers();

  /**
   * Define if the worker should run get spec workflows. Defaults to true. Internal-use only.
   */
  boolean shouldRunGetSpecWorkflows();

  /**
   * Define if the worker should run check connection workflows. Defaults to true. Internal-use only.
   */
  boolean shouldRunCheckConnectionWorkflows();

  /**
   * Define if the worker should run discover workflows. Defaults to true. Internal-use only.
   */
  boolean shouldRunDiscoverWorkflows();

  /**
   * Define if the worker should run sync workflows. Defaults to true. Internal-use only.
   */
  boolean shouldRunSyncWorkflows();

  /**
   * Define if the worker should run connection manager workflows. Defaults to true. Internal-use
   * only.
   */
  boolean shouldRunConnectionManagerWorkflows();

  // Worker - Kube only
  /**
   * Define the local ports the Airbyte Worker pod uses to connect to the various Job pods.
   */
  Set<Integer> getTemporalWorkerPorts();

  // Container Orchestrator
  /**
   * Define if Airbyte should use the container orchestrator. Internal-use only.
   */
  boolean getContainerOrchestratorEnabled();

  /**
   * Get the name of the container orchestrator secret. Internal-use only.
   */
  String getContainerOrchestratorSecretName();

  /**
   * Get the mount path for a secret that should be loaded onto container orchestrator pods.
   * Internal-use only.
   */
  String getContainerOrchestratorSecretMountPath();

  /**
   * Define the image to use for the container orchestrator. Defaults to the Airbyte version.
   */
  String getContainerOrchestratorImage();

  /**
   * Define the replication orchestrator's minimum CPU usage. Defaults to none.
   */
  String getReplicationOrchestratorCpuRequest();

  /**
   * Define the replication orchestrator's maximum CPU usage. Defaults to none.
   */
  String getReplicationOrchestratorCpuLimit();

  /**
   * Define the replication orchestrator's minimum RAM usage. Defaults to none.
   */
  String getReplicationOrchestratorMemoryRequest();

  /**
   * Define the replication orchestrator's maximum RAM usage. Defaults to none.
   */
  String getReplicationOrchestratorMemoryLimit();

  /**
   * Get the longest duration of non long running activity
   */
  int getMaxActivityTimeoutSecond();

  /**
   * Get initial delay in seconds between two activity attempts
   */
  int getInitialDelayBetweenActivityAttemptsSeconds();

  /**
   * Get maximum delay in seconds between two activity attempts
   */
  int getMaxDelayBetweenActivityAttemptsSeconds();

  /**
   * Get the delay in seconds between an activity failing and the workflow being restarted
   */
  int getWorkflowFailureRestartDelaySeconds();

  /**
   * Get number of attempts of the non long running activities
   */
  int getActivityNumberOfAttempt();

  enum TrackingStrategy {
    SEGMENT,
    LOGGING
  }

  enum JobErrorReportingStrategy {
    SENTRY,
    LOGGING
  }

  enum WorkerEnvironment {
    DOCKER,
    KUBERNETES
  }

  enum DeploymentMode {
    OSS,
    CLOUD
  }

  enum SecretPersistenceType {
    NONE,
    TESTING_CONFIG_DB_TABLE,
    GOOGLE_SECRET_MANAGER,
    VAULT
  }

}
