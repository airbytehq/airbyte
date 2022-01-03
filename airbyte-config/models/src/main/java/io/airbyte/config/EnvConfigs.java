/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config;

import com.google.common.base.Preconditions;
import com.google.common.base.Splitter;
import com.google.common.base.Strings;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.storage.CloudStorageConfigs;
import io.airbyte.config.storage.CloudStorageConfigs.GcsConfig;
import io.airbyte.config.storage.CloudStorageConfigs.MinioConfig;
import io.airbyte.config.storage.CloudStorageConfigs.S3Config;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EnvConfigs implements Configs {

  private static final Logger LOGGER = LoggerFactory.getLogger(EnvConfigs.class);

  // env variable names
  public static final String AIRBYTE_ROLE = "AIRBYTE_ROLE";
  public static final String AIRBYTE_VERSION = "AIRBYTE_VERSION";
  public static final String INTERNAL_API_HOST = "INTERNAL_API_HOST";
  public static final String WORKER_ENVIRONMENT = "WORKER_ENVIRONMENT";
  public static final String SPEC_CACHE_BUCKET = "SPEC_CACHE_BUCKET";
  public static final String WORKSPACE_ROOT = "WORKSPACE_ROOT";
  public static final String WORKSPACE_DOCKER_MOUNT = "WORKSPACE_DOCKER_MOUNT";
  public static final String LOCAL_ROOT = "LOCAL_ROOT";
  public static final String LOCAL_DOCKER_MOUNT = "LOCAL_DOCKER_MOUNT";
  public static final String CONFIG_ROOT = "CONFIG_ROOT";
  public static final String DOCKER_NETWORK = "DOCKER_NETWORK";
  public static final String TRACKING_STRATEGY = "TRACKING_STRATEGY";
  public static final String DEPLOYMENT_MODE = "DEPLOYMENT_MODE";
  public static final String DATABASE_USER = "DATABASE_USER";
  public static final String DATABASE_PASSWORD = "DATABASE_PASSWORD";
  public static final String DATABASE_URL = "DATABASE_URL";
  public static final String CONFIG_DATABASE_USER = "CONFIG_DATABASE_USER";
  public static final String CONFIG_DATABASE_PASSWORD = "CONFIG_DATABASE_PASSWORD";
  public static final String CONFIG_DATABASE_URL = "CONFIG_DATABASE_URL";
  public static final String RUN_DATABASE_MIGRATION_ON_STARTUP = "RUN_DATABASE_MIGRATION_ON_STARTUP";
  public static final String WEBAPP_URL = "WEBAPP_URL";
  public static final String JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY = "JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY";
  public static final String JOB_KUBE_TOLERATIONS = "JOB_KUBE_TOLERATIONS";
  public static final String JOB_KUBE_NODE_SELECTORS = "JOB_KUBE_NODE_SELECTORS";
  public static final String JOB_KUBE_SOCAT_IMAGE = "JOB_KUBE_SOCAT_IMAGE";
  public static final String JOB_KUBE_BUSYBOX_IMAGE = "JOB_KUBE_BUSYBOX_IMAGE";
  public static final String JOB_KUBE_CURL_IMAGE = "JOB_KUBE_CURL_IMAGE";
  public static final String SYNC_JOB_MAX_ATTEMPTS = "SYNC_JOB_MAX_ATTEMPTS";
  public static final String SYNC_JOB_MAX_TIMEOUT_DAYS = "SYNC_JOB_MAX_TIMEOUT_DAYS";
  private static final String MINIMUM_WORKSPACE_RETENTION_DAYS = "MINIMUM_WORKSPACE_RETENTION_DAYS";
  private static final String MAXIMUM_WORKSPACE_RETENTION_DAYS = "MAXIMUM_WORKSPACE_RETENTION_DAYS";
  private static final String MAXIMUM_WORKSPACE_SIZE_MB = "MAXIMUM_WORKSPACE_SIZE_MB";
  public static final String MAX_SPEC_WORKERS = "MAX_SPEC_WORKERS";
  public static final String MAX_CHECK_WORKERS = "MAX_CHECK_WORKERS";
  public static final String MAX_DISCOVER_WORKERS = "MAX_DISCOVER_WORKERS";
  public static final String MAX_SYNC_WORKERS = "MAX_SYNC_WORKERS";
  private static final String TEMPORAL_HOST = "TEMPORAL_HOST";
  private static final String TEMPORAL_WORKER_PORTS = "TEMPORAL_WORKER_PORTS";
  private static final String JOB_KUBE_NAMESPACE = "JOB_KUBE_NAMESPACE";
  private static final String SUBMITTER_NUM_THREADS = "SUBMITTER_NUM_THREADS";
  public static final String JOB_MAIN_CONTAINER_CPU_REQUEST = "JOB_MAIN_CONTAINER_CPU_REQUEST";
  public static final String JOB_MAIN_CONTAINER_CPU_LIMIT = "JOB_MAIN_CONTAINER_CPU_LIMIT";
  public static final String JOB_MAIN_CONTAINER_MEMORY_REQUEST = "JOB_MAIN_CONTAINER_MEMORY_REQUEST";
  public static final String JOB_MAIN_CONTAINER_MEMORY_LIMIT = "JOB_MAIN_CONTAINER_MEMORY_LIMIT";
  private static final String SECRET_PERSISTENCE = "SECRET_PERSISTENCE";
  public static final String JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET = "JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET";
  private static final String PUBLISH_METRICS = "PUBLISH_METRICS";
  private static final String CONFIGS_DATABASE_MINIMUM_FLYWAY_MIGRATION_VERSION = "CONFIGS_DATABASE_MINIMUM_FLYWAY_MIGRATION_VERSION";
  private static final String CONFIGS_DATABASE_INITIALIZATION_TIMEOUT_MS = "CONFIGS_DATABASE_INITIALIZATION_TIMEOUT_MS";
  private static final String JOBS_DATABASE_MINIMUM_FLYWAY_MIGRATION_VERSION = "JOBS_DATABASE_MINIMUM_FLYWAY_MIGRATION_VERSION";
  private static final String JOBS_DATABASE_INITIALIZATION_TIMEOUT_MS = "JOBS_DATABASE_INITIALIZATION_TIMEOUT_MS";

  private static final String STATE_STORAGE_S3_BUCKET_NAME = "STATE_STORAGE_S3_BUCKET_NAME";
  private static final String STATE_STORAGE_S3_REGION = "STATE_STORAGE_S3_REGION";
  private static final String STATE_STORAGE_S3_ACCESS_KEY = "STATE_STORAGE_S3_ACCESS_KEY";
  private static final String STATE_STORAGE_S3_SECRET_ACCESS_KEY = "STATE_STORAGE_S3_SECRET_ACCESS_KEY";
  private static final String STATE_STORAGE_MINIO_BUCKET_NAME = "STATE_STORAGE_MINIO_BUCKET_NAME";
  private static final String STATE_STORAGE_MINIO_ENDPOINT = "STATE_STORAGE_MINIO_ENDPOINT";
  private static final String STATE_STORAGE_MINIO_ACCESS_KEY = "STATE_STORAGE_MINIO_ACCESS_KEY";
  private static final String STATE_STORAGE_MINIO_SECRET_ACCESS_KEY = "STATE_STORAGE_MINIO_SECRET_ACCESS_KEY";
  private static final String STATE_STORAGE_GCS_BUCKET_NAME = "STATE_STORAGE_GCS_BUCKET_NAME";
  private static final String STATE_STORAGE_GCS_APPLICATION_CREDENTIALS = "STATE_STORAGE_GCS_APPLICATION_CREDENTIALS";

  // defaults
  private static final String DEFAULT_SPEC_CACHE_BUCKET = "io-airbyte-cloud-spec-cache";
  public static final String DEFAULT_JOB_KUBE_NAMESPACE = "default";
  private static final String DEFAULT_JOB_CPU_REQUIREMENT = null;
  private static final String DEFAULT_JOB_MEMORY_REQUIREMENT = null;
  private static final String DEFAULT_JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY = "IfNotPresent";
  private static final String SECRET_STORE_GCP_PROJECT_ID = "SECRET_STORE_GCP_PROJECT_ID";
  private static final String SECRET_STORE_GCP_CREDENTIALS = "SECRET_STORE_GCP_CREDENTIALS";
  private static final String DEFAULT_JOB_KUBE_SOCAT_IMAGE = "alpine/socat:1.7.4.1-r1";
  private static final String DEFAULT_JOB_KUBE_BUSYBOX_IMAGE = "busybox:1.28";
  private static final String DEFAULT_JOB_KUBE_CURL_IMAGE = "curlimages/curl:7.77.0";
  private static final long DEFAULT_MINIMUM_WORKSPACE_RETENTION_DAYS = 1;
  private static final long DEFAULT_MAXIMUM_WORKSPACE_RETENTION_DAYS = 60;
  private static final long DEFAULT_MAXIMUM_WORKSPACE_SIZE_MB = 5000;
  private static final int DEFAULT_DATABASE_INITIALIZATION_TIMEOUT_MS = 60 * 1000;

  public static final long DEFAULT_MAX_SPEC_WORKERS = 5;
  public static final long DEFAULT_MAX_CHECK_WORKERS = 5;
  public static final long DEFAULT_MAX_DISCOVER_WORKERS = 5;
  public static final long DEFAULT_MAX_SYNC_WORKERS = 5;

  public static final String DEFAULT_NETWORK = "host";

  private final Function<String, String> getEnv;
  private final LogConfigs logConfigs;
  private final CloudStorageConfigs stateStorageCloudConfigs;

  public EnvConfigs() {
    this(System::getenv);
  }

  public EnvConfigs(final Function<String, String> getEnv) {
    this.getEnv = getEnv;
    this.logConfigs = new LogConfigs(getLogConfiguration().orElse(null));
    this.stateStorageCloudConfigs = getStateStorageConfiguration().orElse(null);
  }

  private Optional<CloudStorageConfigs> getLogConfiguration() {
    if (getEnv(LogClientSingleton.GCS_LOG_BUCKET) != null && !getEnv(LogClientSingleton.GCS_LOG_BUCKET).isBlank()) {
      return Optional.of(CloudStorageConfigs.gcs(new GcsConfig(
          getEnvOrDefault(LogClientSingleton.GCS_LOG_BUCKET, ""),
          getEnvOrDefault(LogClientSingleton.GOOGLE_APPLICATION_CREDENTIALS, ""))));
    } else if (getEnv(LogClientSingleton.S3_MINIO_ENDPOINT) != null && !getEnv(LogClientSingleton.S3_MINIO_ENDPOINT).isBlank()) {
      return Optional.of(CloudStorageConfigs.minio(new MinioConfig(
          getEnvOrDefault(LogClientSingleton.S3_LOG_BUCKET, ""),
          getEnvOrDefault(LogClientSingleton.AWS_ACCESS_KEY_ID, ""),
          getEnvOrDefault(LogClientSingleton.AWS_SECRET_ACCESS_KEY, ""),
          getEnvOrDefault(LogClientSingleton.S3_MINIO_ENDPOINT, ""))));
    } else if (getEnv(LogClientSingleton.S3_LOG_BUCKET_REGION) != null && !getEnv(LogClientSingleton.S3_LOG_BUCKET_REGION).isBlank()) {
      return Optional.of(CloudStorageConfigs.s3(new S3Config(
          getEnvOrDefault(LogClientSingleton.S3_LOG_BUCKET, ""),
          getEnvOrDefault(LogClientSingleton.AWS_ACCESS_KEY_ID, ""),
          getEnvOrDefault(LogClientSingleton.AWS_SECRET_ACCESS_KEY, ""),
          getEnvOrDefault(LogClientSingleton.S3_LOG_BUCKET_REGION, ""))));
    } else {
      return Optional.empty();
    }
  }

  private Optional<CloudStorageConfigs> getStateStorageConfiguration() {
    if (getEnv(STATE_STORAGE_GCS_BUCKET_NAME) != null) {
      return Optional.of(CloudStorageConfigs.gcs(new GcsConfig(
          getEnvOrDefault(STATE_STORAGE_GCS_BUCKET_NAME, ""),
          getEnvOrDefault(LogClientSingleton.GOOGLE_APPLICATION_CREDENTIALS, ""))));
    } else if (getEnv(STATE_STORAGE_MINIO_ENDPOINT) != null) {
      return Optional.of(CloudStorageConfigs.minio(new MinioConfig(
          getEnvOrDefault(STATE_STORAGE_MINIO_BUCKET_NAME, ""),
          getEnvOrDefault(LogClientSingleton.AWS_ACCESS_KEY_ID, ""),
          getEnvOrDefault(LogClientSingleton.AWS_SECRET_ACCESS_KEY, ""),
          getEnvOrDefault(STATE_STORAGE_MINIO_ENDPOINT, ""))));
    } else if (getEnv(STATE_STORAGE_S3_REGION) != null) {
      return Optional.of(CloudStorageConfigs.s3(new S3Config(
          getEnvOrDefault(STATE_STORAGE_S3_BUCKET_NAME, ""),
          getEnvOrDefault(LogClientSingleton.AWS_ACCESS_KEY_ID, ""),
          getEnvOrDefault(LogClientSingleton.AWS_SECRET_ACCESS_KEY, ""),
          getEnvOrDefault(STATE_STORAGE_S3_REGION, ""))));
    } else {
      return Optional.empty();
    }
  }

  // CORE
  // General
  @Override
  public String getAirbyteRole() {
    return getEnv(AIRBYTE_ROLE);
  }

  @Override
  public AirbyteVersion getAirbyteVersion() {
    return new AirbyteVersion(getEnsureEnv(AIRBYTE_VERSION));
  }

  @Override
  public String getAirbyteVersionOrWarning() {
    return Optional.ofNullable(getEnv(AIRBYTE_VERSION)).orElse("version not set");
  }

  @Override
  public String getSpecCacheBucket() {
    return getEnvOrDefault(SPEC_CACHE_BUCKET, DEFAULT_SPEC_CACHE_BUCKET);
  }

  @Override
  public DeploymentMode getDeploymentMode() {
    return getEnvOrDefault(DEPLOYMENT_MODE, DeploymentMode.OSS, s -> {
      try {
        return DeploymentMode.valueOf(s);
      } catch (final IllegalArgumentException e) {
        LOGGER.info(s + " not recognized, defaulting to " + DeploymentMode.OSS);
        return DeploymentMode.OSS;
      }
    });
  }

  @Override
  public WorkerEnvironment getWorkerEnvironment() {
    return getEnvOrDefault(WORKER_ENVIRONMENT, WorkerEnvironment.DOCKER, s -> WorkerEnvironment.valueOf(s.toUpperCase()));
  }

  @Override
  public Path getConfigRoot() {
    return getPath(CONFIG_ROOT);
  }

  @Override
  public Path getWorkspaceRoot() {
    return getPath(WORKSPACE_ROOT);
  }

  // Docker Only
  @Override
  public String getWorkspaceDockerMount() {
    return getEnvOrDefault(WORKSPACE_DOCKER_MOUNT, getWorkspaceRoot().toString());
  }

  @Override
  public String getLocalDockerMount() {
    return getEnvOrDefault(LOCAL_DOCKER_MOUNT, getLocalRoot().toString());
  }

  @Override
  public String getDockerNetwork() {
    return getEnvOrDefault(DOCKER_NETWORK, DEFAULT_NETWORK);
  }

  @Override
  public Path getLocalRoot() {
    return getPath(LOCAL_ROOT);
  }

  // Secrets
  @Override
  public String getSecretStoreGcpCredentials() {
    return getEnv(SECRET_STORE_GCP_CREDENTIALS);
  }

  @Override
  public String getSecretStoreGcpProjectId() {
    return getEnv(SECRET_STORE_GCP_PROJECT_ID);
  }

  @Override
  public SecretPersistenceType getSecretPersistenceType() {
    final var secretPersistenceStr = getEnvOrDefault(SECRET_PERSISTENCE, SecretPersistenceType.NONE.name());
    return SecretPersistenceType.valueOf(secretPersistenceStr);
  }

  // Database
  @Override
  public String getDatabaseUser() {
    return getEnsureEnv(DATABASE_USER);
  }

  @Override
  public String getDatabasePassword() {
    return getEnsureEnv(DATABASE_PASSWORD);
  }

  @Override
  public String getDatabaseUrl() {
    return getEnsureEnv(DATABASE_URL);
  }

  @Override
  public String getJobsDatabaseMinimumFlywayMigrationVersion() {
    return getEnsureEnv(JOBS_DATABASE_MINIMUM_FLYWAY_MIGRATION_VERSION);
  }

  @Override
  public long getJobsDatabaseInitializationTimeoutMs() {
    return getEnvOrDefault(JOBS_DATABASE_INITIALIZATION_TIMEOUT_MS, DEFAULT_DATABASE_INITIALIZATION_TIMEOUT_MS);
  }

  @Override
  public String getConfigDatabaseUser() {
    // Default to reuse the job database
    return getEnvOrDefault(CONFIG_DATABASE_USER, getDatabaseUser());
  }

  @Override
  public String getConfigDatabasePassword() {
    // Default to reuse the job database
    return getEnvOrDefault(CONFIG_DATABASE_PASSWORD, getDatabasePassword(), true);
  }

  @Override
  public String getConfigDatabaseUrl() {
    // Default to reuse the job database
    return getEnvOrDefault(CONFIG_DATABASE_URL, getDatabaseUrl());
  }

  @Override
  public String getConfigsDatabaseMinimumFlywayMigrationVersion() {
    return getEnsureEnv(CONFIGS_DATABASE_MINIMUM_FLYWAY_MIGRATION_VERSION);
  }

  @Override
  public long getConfigsDatabaseInitializationTimeoutMs() {
    return getEnvOrDefault(CONFIGS_DATABASE_INITIALIZATION_TIMEOUT_MS, DEFAULT_DATABASE_INITIALIZATION_TIMEOUT_MS);
  }

  @Override
  public boolean runDatabaseMigrationOnStartup() {
    return getEnvOrDefault(RUN_DATABASE_MIGRATION_ON_STARTUP, true);
  }

  // Airbyte Services
  @Override
  public String getTemporalHost() {
    return getEnvOrDefault(TEMPORAL_HOST, "airbyte-temporal:7233");
  }

  @Override
  public String getAirbyteApiHost() {
    return getEnsureEnv(INTERNAL_API_HOST).split(":")[0];
  }

  @Override
  public int getAirbyteApiPort() {
    return Integer.parseInt(getEnsureEnv(INTERNAL_API_HOST).split(":")[1]);
  }

  @Override
  public String getWebappUrl() {
    return getEnsureEnv(WEBAPP_URL);
  }

  // Jobs
  @Override
  public int getSyncJobMaxAttempts() {
    return Integer.parseInt(getEnvOrDefault(SYNC_JOB_MAX_ATTEMPTS, "3"));
  }

  @Override
  public int getSyncJobMaxTimeoutDays() {
    return Integer.parseInt(getEnvOrDefault(SYNC_JOB_MAX_TIMEOUT_DAYS, "3"));
  }

  /**
   * Returns worker pod tolerations parsed from its own environment variable. The value of the env is
   * a string that represents one or more tolerations.
   * <ul>
   * <li>Tolerations are separated by a `;`
   * <li>Each toleration contains k=v pairs mentioning some/all of key, effect, operator and value and
   * separated by `,`
   * </ul>
   * <p>
   * For example:- The following represents two tolerations, one checking existence and another
   * matching a value
   * <p>
   * key=airbyte-server,operator=Exists,effect=NoSchedule;key=airbyte-server,operator=Equals,value=true,effect=NoSchedule
   *
   * @return list of WorkerKubeToleration parsed from env
   */
  @Override
  public List<TolerationPOJO> getJobKubeTolerations() {
    final String tolerationsStr = getEnvOrDefault(JOB_KUBE_TOLERATIONS, "");

    final Stream<String> tolerations = Strings.isNullOrEmpty(tolerationsStr) ? Stream.of()
        : Splitter.on(";")
            .splitToStream(tolerationsStr)
            .filter(tolerationStr -> !Strings.isNullOrEmpty(tolerationStr));

    return tolerations
        .map(this::parseToleration)
        .filter(Objects::nonNull)
        .collect(Collectors.toList());
  }

  private TolerationPOJO parseToleration(final String tolerationStr) {
    final Map<String, String> tolerationMap = Splitter.on(",")
        .splitToStream(tolerationStr)
        .map(s -> s.split("="))
        .collect(Collectors.toMap(s -> s[0], s -> s[1]));

    if (tolerationMap.containsKey("key") && tolerationMap.containsKey("effect") && tolerationMap.containsKey("operator")) {
      return new TolerationPOJO(
          tolerationMap.get("key"),
          tolerationMap.get("effect"),
          tolerationMap.get("value"),
          tolerationMap.get("operator"));
    } else {
      LOGGER.warn(
          "Ignoring toleration {}, missing one of key,effect or operator",
          tolerationStr);
      return null;
    }
  }

  /**
   * Returns a map of node selectors from its own environment variable. The value of the env is a
   * string that represents one or more node selector labels. Each kv-pair is separated by a `,`
   * <p>
   * For example:- The following represents two node selectors
   * <p>
   * airbyte=server,type=preemptive
   *
   * @return map containing kv pairs of node selectors
   */
  @Override
  public Map<String, String> getJobKubeNodeSelectors() {
    return Splitter.on(",")
        .splitToStream(getEnvOrDefault(JOB_KUBE_NODE_SELECTORS, ""))
        .filter(s -> !Strings.isNullOrEmpty(s) && s.contains("="))
        .map(s -> s.split("="))
        .collect(Collectors.toMap(s -> s[0], s -> s[1]));
  }

  @Override
  public String getJobKubeMainContainerImagePullPolicy() {
    return getEnvOrDefault(JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY, DEFAULT_JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_POLICY);
  }

  /**
   * Returns the name of the secret to be used when pulling down docker images for jobs. Automatically
   * injected in the KubePodProcess class and used in the job pod templates. The empty string is a
   * no-op value.
   */
  @Override
  public String getJobKubeMainContainerImagePullSecret() {
    return getEnvOrDefault(JOB_KUBE_MAIN_CONTAINER_IMAGE_PULL_SECRET, "");
  }

  @Override
  public String getJobKubeSocatImage() {
    return getEnvOrDefault(JOB_KUBE_SOCAT_IMAGE, DEFAULT_JOB_KUBE_SOCAT_IMAGE);
  }

  @Override
  public String getJobKubeBusyboxImage() {
    return getEnvOrDefault(JOB_KUBE_BUSYBOX_IMAGE, DEFAULT_JOB_KUBE_BUSYBOX_IMAGE);
  }

  @Override
  public String getJobKubeCurlImage() {
    return getEnvOrDefault(JOB_KUBE_CURL_IMAGE, DEFAULT_JOB_KUBE_CURL_IMAGE);
  }

  @Override
  public String getJobKubeNamespace() {
    return getEnvOrDefault(JOB_KUBE_NAMESPACE, DEFAULT_JOB_KUBE_NAMESPACE);
  }

  @Override
  public String getJobMainContainerCpuRequest() {
    return getEnvOrDefault(JOB_MAIN_CONTAINER_CPU_REQUEST, DEFAULT_JOB_CPU_REQUIREMENT);
  }

  @Override
  public String getJobMainContainerCpuLimit() {
    return getEnvOrDefault(JOB_MAIN_CONTAINER_CPU_LIMIT, DEFAULT_JOB_CPU_REQUIREMENT);
  }

  @Override
  public String getJobMainContainerMemoryRequest() {
    return getEnvOrDefault(JOB_MAIN_CONTAINER_MEMORY_REQUEST, DEFAULT_JOB_MEMORY_REQUIREMENT);
  }

  @Override
  public String getJobMainContainerMemoryLimit() {
    return getEnvOrDefault(JOB_MAIN_CONTAINER_MEMORY_LIMIT, DEFAULT_JOB_MEMORY_REQUIREMENT);
  }

  @Override
  public LogConfigs getLogConfigs() {
    return logConfigs;
  }

  @Override
  public CloudStorageConfigs getStateStorageCloudConfigs() {
    return stateStorageCloudConfigs;
  }

  @Override
  public boolean getPublishMetrics() {
    return getEnvOrDefault(PUBLISH_METRICS, false);
  }

  @Override
  public TrackingStrategy getTrackingStrategy() {
    return getEnvOrDefault(TRACKING_STRATEGY, TrackingStrategy.LOGGING, s -> {
      try {
        return TrackingStrategy.valueOf(s.toUpperCase());
      } catch (final IllegalArgumentException e) {
        LOGGER.info(s + " not recognized, defaulting to " + TrackingStrategy.LOGGING);
        return TrackingStrategy.LOGGING;
      }
    });
  }

  // APPLICATIONS
  // Worker
  @Override
  public MaxWorkersConfig getMaxWorkers() {
    return new MaxWorkersConfig(
        Math.toIntExact(getEnvOrDefault(MAX_SPEC_WORKERS, DEFAULT_MAX_SPEC_WORKERS)),
        Math.toIntExact(getEnvOrDefault(MAX_CHECK_WORKERS, DEFAULT_MAX_CHECK_WORKERS)),
        Math.toIntExact(getEnvOrDefault(MAX_DISCOVER_WORKERS, DEFAULT_MAX_DISCOVER_WORKERS)),
        Math.toIntExact(getEnvOrDefault(MAX_SYNC_WORKERS, DEFAULT_MAX_SYNC_WORKERS)));
  }

  @Override
  public Set<Integer> getTemporalWorkerPorts() {
    final var ports = getEnvOrDefault(TEMPORAL_WORKER_PORTS, "");
    if (ports.isEmpty()) {
      return new HashSet<>();
    }
    return Arrays.stream(ports.split(",")).map(Integer::valueOf).collect(Collectors.toSet());
  }

  // Scheduler
  @Override
  public WorkspaceRetentionConfig getWorkspaceRetentionConfig() {
    final long minDays = getEnvOrDefault(MINIMUM_WORKSPACE_RETENTION_DAYS, DEFAULT_MINIMUM_WORKSPACE_RETENTION_DAYS);
    final long maxDays = getEnvOrDefault(MAXIMUM_WORKSPACE_RETENTION_DAYS, DEFAULT_MAXIMUM_WORKSPACE_RETENTION_DAYS);
    final long maxSizeMb = getEnvOrDefault(MAXIMUM_WORKSPACE_SIZE_MB, DEFAULT_MAXIMUM_WORKSPACE_SIZE_MB);

    return new WorkspaceRetentionConfig(minDays, maxDays, maxSizeMb);
  }

  @Override
  public String getSubmitterNumThreads() {
    return getEnvOrDefault(SUBMITTER_NUM_THREADS, "5");
  }

  @Override
  public boolean getContainerOrchestratorEnabled() {
    return getEnvOrDefault("CONTAINER_ORCHESTRATOR_ENABLED", false, Boolean::valueOf);
  }

  // Helpers
  public String getEnvOrDefault(final String key, final String defaultValue) {
    return getEnvOrDefault(key, defaultValue, Function.identity(), false);
  }

  public String getEnvOrDefault(final String key, final String defaultValue, final boolean isSecret) {
    return getEnvOrDefault(key, defaultValue, Function.identity(), isSecret);
  }

  public long getEnvOrDefault(final String key, final long defaultValue) {
    return getEnvOrDefault(key, defaultValue, Long::parseLong, false);
  }

  public boolean getEnvOrDefault(final String key, final boolean defaultValue) {
    return getEnvOrDefault(key, defaultValue, Boolean::parseBoolean);
  }

  public <T> T getEnvOrDefault(final String key, final T defaultValue, final Function<String, T> parser) {
    return getEnvOrDefault(key, defaultValue, parser, false);
  }

  public <T> T getEnvOrDefault(final String key, final T defaultValue, final Function<String, T> parser, final boolean isSecret) {
    final String value = getEnv.apply(key);
    if (value != null && !value.isEmpty()) {
      return parser.apply(value);
    } else {
      LOGGER.info("Using default value for environment variable {}: '{}'", key, isSecret ? "*****" : defaultValue);
      return defaultValue;
    }
  }

  public String getEnv(final String name) {
    return getEnv.apply(name);
  }

  public String getEnsureEnv(final String name) {
    final String value = getEnv(name);
    Preconditions.checkArgument(value != null, "'%s' environment variable cannot be null", name);

    return value;
  }

  private Path getPath(final String name) {
    final String value = getEnv.apply(name);
    if (value == null) {
      throw new IllegalArgumentException("Env variable not defined: " + name);
    }
    return Path.of(value);
  }

}
