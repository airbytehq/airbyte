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

public interface Configs {

  // CORE
  // General
  String getAirbyteRole();

  AirbyteVersion getAirbyteVersion();

  String getAirbyteVersionOrWarning();

  String getSpecCacheBucket();

  DeploymentMode getDeploymentMode();

  WorkerEnvironment getWorkerEnvironment();

  Path getConfigRoot();

  Path getWorkspaceRoot();

  // Docker Only
  String getWorkspaceDockerMount();

  String getLocalDockerMount();

  String getDockerNetwork();

  Path getLocalRoot();

  // Secrets
  String getSecretStoreGcpProjectId();

  String getSecretStoreGcpCredentials();

  SecretPersistenceType getSecretPersistenceType();

  // Database
  String getDatabaseUser();

  String getDatabasePassword();

  String getDatabaseUrl();

  String getConfigDatabaseUser();

  String getConfigDatabasePassword();

  String getConfigDatabaseUrl();

  boolean runDatabaseMigrationOnStartup();

  // Airbyte Services
  String getTemporalHost();

  String getAirbyteApiHost();

  int getAirbyteApiPort();

  String getWebappUrl();

  // Jobs
  int getSyncJobMaxAttempts();

  int getSyncJobMaxTimeoutDays();

  List<TolerationPOJO> getJobPodTolerations();

  Map<String, String> getJobPodNodeSelectors();

  String getJobPodMainContainerImagePullPolicy();

  String getJobPodMainContainerImagePullSecret();

  String getJobPodSocatImage();

  String getJobPodBusyboxImage();

  String getJobPodCurlImage();

  String getJobPodKubeNamespace();

  String getJobPodMainContainerCpuRequest();

  String getJobPodMainContainerCpuLimit();

  String getJobPodMainContainerMemoryRequest();

  String getJobPodMainContainerMemoryLimit();

  // Logging/Monitoring/Tracking
  LogConfigs getLogConfigs();

  CloudStorageConfigs getStateStorageCloudConfigs();

  boolean getPublishMetrics();

  TrackingStrategy getTrackingStrategy();

  // APPLICATIONS
  // Worker
  MaxWorkersConfig getMaxWorkers();

  Set<Integer> getTemporalWorkerPorts();

  // Scheduler
  WorkspaceRetentionConfig getWorkspaceRetentionConfig();

  String getSubmitterNumThreads();

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
