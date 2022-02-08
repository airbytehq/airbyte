/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
   * Secret Manager. Set to TESTING_CONFIG_DB_TABLE to use the database as a test. Alpha support.
   * Undefined behavior will result if this is turned on and then off.
   */
  SecretPersistenceType getSecretPersistenceType();

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

  // Airbyte Services
  /**
   * Define the url where Temporal is hosted at. Please include the port. Airbyte services use this
   * information.
   */
  String getTemporalHost();

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
   * Defines a default map of environment variables to use for any launched job containers. The
   * expected format is a JSON encoded String -> String map. Make sure to escape properly. Defaults to
   * an empty map.
   */
  Map<String, String> getJobDefaultEnvMap();

  // Jobs - Kube only
  /**
   * Define one or more Job pod tolerations. Tolerations are separated by ';'. Each toleration
   * contains k=v pairs mentioning some/all of key, effect, operator and value and separated by `,`.
   */
  List<TolerationPOJO> getJobKubeTolerations();

  /**
   * Define one or more Job pod node selectors. Each kv-pair is separated by a `,`.
   */
  Map<String, String> getJobKubeNodeSelectors();

  /**
   * Define the Job pod connector image pull policy.
   */
  String getJobKubeMainContainerImagePullPolicy();

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
   * Define either S3, Minio or GCS as a state storage backend. Multiple variables are involved here.
   * Please see {@link CloudStorageConfigs} for more info.
   */
  CloudStorageConfigs getStateStorageCloudConfigs();

  /**
   * Determine if Datadog tracking events should be published. Mainly for Airbyte internal use.
   */
  boolean getPublishMetrics();

  /**
   * Define whether to publish tracking events to Segment or log-only. Airbyte internal use.
   */
  TrackingStrategy getTrackingStrategy();

  // APPLICATIONS
  // Worker
  /**
   * Define the maximum number of workers each Airbyte Worker container supports. Multiple variables
   * are involved here. Please see {@link MaxWorkersConfig} for more info.
   */
  MaxWorkersConfig getMaxWorkers();

  // Worker - Kube only
  /**
   * Define the local ports the Airbyte Worker pod uses to connect to the various Job pods.
   */
  Set<Integer> getTemporalWorkerPorts();

  // Scheduler
  /**
   * Define how and how often the Scheduler sweeps its local disk for old configs. Multiple variables
   * are involved here. Please see {@link WorkspaceRetentionConfig} for more info.
   */
  WorkspaceRetentionConfig getWorkspaceRetentionConfig();

  /**
   * Define the maximum number of concurrent jobs the Scheduler schedules. Defaults to 5.
   */
  String getSubmitterNumThreads();

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
   * Get the longest duration of non long running activity
   */
  int getMaxActivityTimeoutSecond();

  /**
   * Get the duration in second between 2 activity attempts
   */
  int getDelayBetweenActivityAttempts();

  /**
   * Get number of attempts of the non long running activities
   */
  int getActivityNumberOfAttempt();

  enum TrackingStrategy {
    SEGMENT,
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
    GOOGLE_SECRET_MANAGER
  }

}
