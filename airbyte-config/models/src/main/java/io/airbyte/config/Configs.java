/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.helpers.LogConfigs;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Set;

public interface Configs {

  String getAirbyteRole();

  AirbyteVersion getAirbyteVersion();

  String getAirbyteApiHost();

  int getAirbyteApiPort();

  String getAirbyteVersionOrWarning();

  Path getConfigRoot();

  Path getWorkspaceRoot();

  Path getLocalRoot();

  String getDatabaseUser();

  String getDatabasePassword();

  String getDatabaseUrl();

  String getConfigDatabaseUser();

  String getConfigDatabasePassword();

  String getConfigDatabaseUrl();

  String getSecretStoreGcpProjectId();

  String getSecretStoreGcpCredentials();

  boolean runDatabaseMigrationOnStartup();

  int getMaxSyncJobAttempts();

  int getMaxSyncTimeoutDays();

  String getWebappUrl();

  String getWorkspaceDockerMount();

  String getLocalDockerMount();

  String getDockerNetwork();

  TrackingStrategy getTrackingStrategy();

  DeploymentMode getDeploymentMode();

  WorkerEnvironment getWorkerEnvironment();

  String getSpecCacheBucket();

  WorkspaceRetentionConfig getWorkspaceRetentionConfig();

  String getJobImagePullPolicy();

  List<WorkerPodToleration> getWorkerPodTolerations();

  Map<String, String> getWorkerNodeSelectors();

  String getJobSocatImage();

  String getJobBusyboxImage();

  String getJobCurlImage();

  MaxWorkersConfig getMaxWorkers();

  String getTemporalHost();

  Set<Integer> getTemporalWorkerPorts();

  String getKubeNamespace();

  String getSubmitterNumThreads();

  String getJobsImagePullSecret();

  // Resources
  String getCpuRequest();

  String getCpuLimit();

  String getMemoryRequest();

  String getMemoryLimit();

  // Logging
  LogConfigs getLogConfigs();

  String getS3LogBucket();

  String getS3LogBucketRegion();

  String getAwsAccessKey();

  String getAwsSecretAccessKey();

  String getS3MinioEndpoint();

  String getGcpStorageBucket();

  String getGoogleApplicationCredentials();

  boolean getPublishMetrics();

  boolean getVersion32ForceUpgrade();

  SecretPersistenceType getSecretPersistenceType();

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
