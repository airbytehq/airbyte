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
import io.airbyte.config.helpers.LogConfiguration;
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
  public static final String JOB_IMAGE_PULL_POLICY = "JOB_IMAGE_PULL_POLICY";
  public static final String WORKER_POD_TOLERATIONS = "WORKER_POD_TOLERATIONS";
  public static final String WORKER_POD_NODE_SELECTORS = "WORKER_POD_NODE_SELECTORS";
  public static final String MAX_SYNC_JOB_ATTEMPTS = "MAX_SYNC_JOB_ATTEMPTS";
  public static final String MAX_SYNC_TIMEOUT_DAYS = "MAX_SYNC_TIMEOUT_DAYS";
  private static final String MINIMUM_WORKSPACE_RETENTION_DAYS = "MINIMUM_WORKSPACE_RETENTION_DAYS";
  private static final String MAXIMUM_WORKSPACE_RETENTION_DAYS = "MAXIMUM_WORKSPACE_RETENTION_DAYS";
  private static final String MAXIMUM_WORKSPACE_SIZE_MB = "MAXIMUM_WORKSPACE_SIZE_MB";
  public static final String MAX_SPEC_WORKERS = "MAX_SPEC_WORKERS";
  public static final String MAX_CHECK_WORKERS = "MAX_CHECK_WORKERS";
  public static final String MAX_DISCOVER_WORKERS = "MAX_DISCOVER_WORKERS";
  public static final String MAX_SYNC_WORKERS = "MAX_SYNC_WORKERS";
  private static final String TEMPORAL_HOST = "TEMPORAL_HOST";
  private static final String TEMPORAL_WORKER_PORTS = "TEMPORAL_WORKER_PORTS";
  private static final String KUBE_NAMESPACE = "KUBE_NAMESPACE";
  private static final String SUBMITTER_NUM_THREADS = "SUBMITTER_NUM_THREADS";
  private static final String RESOURCE_CPU_REQUEST = "RESOURCE_CPU_REQUEST";
  private static final String RESOURCE_CPU_LIMIT = "RESOURCE_CPU_LIMIT";
  private static final String RESOURCE_MEMORY_REQUEST = "RESOURCE_MEMORY_REQUEST";
  private static final String RESOURCE_MEMORY_LIMIT = "RESOURCE_MEMORY_LIMIT";
  private static final String SECRET_PERSISTENCE = "SECRET_PERSISTENCE";
  private static final String JOBS_IMAGE_PULL_SECRET = "JOBS_IMAGE_PULL_SECRET";
  private static final String PUBLISH_METRICS = "PUBLISH_METRICS";

  // defaults
  private static final String DEFAULT_SPEC_CACHE_BUCKET = "io-airbyte-cloud-spec-cache";
  private static final String DEFAULT_KUBE_NAMESPACE = "default";
  private static final String DEFAULT_RESOURCE_REQUIREMENT_CPU = null;
  private static final String DEFAULT_RESOURCE_REQUIREMENT_MEMORY = null;
  private static final String DEFAULT_JOB_IMAGE_PULL_POLICY = "IfNotPresent";
  private static final String SECRET_STORE_GCP_PROJECT_ID = "SECRET_STORE_GCP_PROJECT_ID";
  private static final String SECRET_STORE_GCP_CREDENTIALS = "SECRET_STORE_GCP_CREDENTIALS";
  private static final long DEFAULT_MINIMUM_WORKSPACE_RETENTION_DAYS = 1;
  private static final long DEFAULT_MAXIMUM_WORKSPACE_RETENTION_DAYS = 60;
  private static final long DEFAULT_MAXIMUM_WORKSPACE_SIZE_MB = 5000;

  public static final long DEFAULT_MAX_SPEC_WORKERS = 5;
  public static final long DEFAULT_MAX_CHECK_WORKERS = 5;
  public static final long DEFAULT_MAX_DISCOVER_WORKERS = 5;
  public static final long DEFAULT_MAX_SYNC_WORKERS = 5;

  public static final String DEFAULT_NETWORK = "host";

  private final Function<String, String> getEnv;
  private LogConfiguration logConfiguration;

  public EnvConfigs() {
    this(System::getenv);
  }

  EnvConfigs(final Function<String, String> getEnv) {
    this.getEnv = getEnv;
    this.logConfiguration = new LogConfiguration(
        getEnvOrDefault(LogClientSingleton.S3_LOG_BUCKET, ""),
        getEnvOrDefault(LogClientSingleton.S3_LOG_BUCKET_REGION, ""),
        getEnvOrDefault(LogClientSingleton.AWS_ACCESS_KEY_ID, ""),
        getEnvOrDefault(LogClientSingleton.AWS_SECRET_ACCESS_KEY, ""),
        getEnvOrDefault(LogClientSingleton.S3_MINIO_ENDPOINT, ""),
        getEnvOrDefault(LogClientSingleton.GCP_STORAGE_BUCKET, ""),
        getEnvOrDefault(LogClientSingleton.GOOGLE_APPLICATION_CREDENTIALS, ""));
  }

  @Override
  public String getAirbyteRole() {
    return getEnv(AIRBYTE_ROLE);
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
  public AirbyteVersion getAirbyteVersion() {
    return new AirbyteVersion(getEnsureEnv(AIRBYTE_VERSION));
  }

  @Override
  public String getAirbyteVersionOrWarning() {
    return Optional.ofNullable(getEnv(AIRBYTE_VERSION)).orElse("version not set");
  }

  @Override
  public Path getConfigRoot() {
    return getPath(CONFIG_ROOT);
  }

  @Override
  public Path getWorkspaceRoot() {
    return getPath(WORKSPACE_ROOT);
  }

  @Override
  public Path getLocalRoot() {
    return getPath(LOCAL_ROOT);
  }

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
  public int getMaxSyncJobAttempts() {
    return Integer.parseInt(getEnvOrDefault(MAX_SYNC_JOB_ATTEMPTS, "3"));
  }

  @Override
  public int getMaxSyncTimeoutDays() {
    return Integer.parseInt(getEnvOrDefault(MAX_SYNC_TIMEOUT_DAYS, "3"));
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
  public String getSecretStoreGcpCredentials() {
    return getEnv(SECRET_STORE_GCP_CREDENTIALS);
  }

  @Override
  public String getSecretStoreGcpProjectId() {
    return getEnv(SECRET_STORE_GCP_PROJECT_ID);
  }

  @Override
  public boolean runDatabaseMigrationOnStartup() {
    return getEnvOrDefault(RUN_DATABASE_MIGRATION_ON_STARTUP, true);
  }

  @Override
  public String getWebappUrl() {
    return getEnsureEnv(WEBAPP_URL);
  }

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
  public String getSpecCacheBucket() {
    return getEnvOrDefault(SPEC_CACHE_BUCKET, DEFAULT_SPEC_CACHE_BUCKET);
  }

  @Override
  public WorkspaceRetentionConfig getWorkspaceRetentionConfig() {
    final long minDays = getEnvOrDefault(MINIMUM_WORKSPACE_RETENTION_DAYS, DEFAULT_MINIMUM_WORKSPACE_RETENTION_DAYS);
    final long maxDays = getEnvOrDefault(MAXIMUM_WORKSPACE_RETENTION_DAYS, DEFAULT_MAXIMUM_WORKSPACE_RETENTION_DAYS);
    final long maxSizeMb = getEnvOrDefault(MAXIMUM_WORKSPACE_SIZE_MB, DEFAULT_MAXIMUM_WORKSPACE_SIZE_MB);

    return new WorkspaceRetentionConfig(minDays, maxDays, maxSizeMb);
  }

  private WorkerPodToleration workerPodToleration(final String tolerationStr) {
    final Map<String, String> tolerationMap = Splitter.on(",")
        .splitToStream(tolerationStr)
        .map(s -> s.split("="))
        .collect(Collectors.toMap(s -> s[0], s -> s[1]));

    if (tolerationMap.containsKey("key") && tolerationMap.containsKey("effect") && tolerationMap.containsKey("operator")) {
      return new WorkerPodToleration(tolerationMap.get("key"),
          tolerationMap.get("effect"),
          tolerationMap.get("value"),
          tolerationMap.get("operator"));
    } else {
      LOGGER.warn("Ignoring toleration {}, missing one of key,effect or operator",
          tolerationStr);
      return null;
    }
  }

  @Override
  public String getJobImagePullPolicy() {
    return getEnvOrDefault(JOB_IMAGE_PULL_POLICY, DEFAULT_JOB_IMAGE_PULL_POLICY);
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
   * @return list of WorkerPodToleration parsed from env
   */
  @Override
  public List<WorkerPodToleration> getWorkerPodTolerations() {
    final String tolerationsStr = getEnvOrDefault(WORKER_POD_TOLERATIONS, "");

    final Stream<String> tolerations = Strings.isNullOrEmpty(tolerationsStr) ? Stream.of()
        : Splitter.on(";")
            .splitToStream(tolerationsStr)
            .filter(tolerationStr -> !Strings.isNullOrEmpty(tolerationStr));

    return tolerations
        .map(this::workerPodToleration)
        .filter(Objects::nonNull)
        .collect(Collectors.toList());
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
  public Map<String, String> getWorkerNodeSelectors() {
    return Splitter.on(",")
        .splitToStream(getEnvOrDefault(WORKER_POD_NODE_SELECTORS, ""))
        .filter(s -> !Strings.isNullOrEmpty(s) && s.contains("="))
        .map(s -> s.split("="))
        .collect(Collectors.toMap(s -> s[0], s -> s[1]));
  }

  @Override
  public MaxWorkersConfig getMaxWorkers() {
    return new MaxWorkersConfig(
        Math.toIntExact(getEnvOrDefault(MAX_SPEC_WORKERS, DEFAULT_MAX_SPEC_WORKERS)),
        Math.toIntExact(getEnvOrDefault(MAX_CHECK_WORKERS, DEFAULT_MAX_CHECK_WORKERS)),
        Math.toIntExact(getEnvOrDefault(MAX_DISCOVER_WORKERS, DEFAULT_MAX_DISCOVER_WORKERS)),
        Math.toIntExact(getEnvOrDefault(MAX_SYNC_WORKERS, DEFAULT_MAX_SYNC_WORKERS)));
  }

  @Override
  public String getTemporalHost() {
    return getEnvOrDefault(TEMPORAL_HOST, "airbyte-temporal:7233");
  }

  @Override
  public Set<Integer> getTemporalWorkerPorts() {
    final var ports = getEnvOrDefault(TEMPORAL_WORKER_PORTS, "");
    if (ports.isEmpty()) {
      return new HashSet<>();
    }
    return Arrays.stream(ports.split(",")).map(Integer::valueOf).collect(Collectors.toSet());
  }

  @Override
  public String getKubeNamespace() {
    return getEnvOrDefault(KUBE_NAMESPACE, DEFAULT_KUBE_NAMESPACE);
  }

  @Override
  public String getSubmitterNumThreads() {
    return getEnvOrDefault(SUBMITTER_NUM_THREADS, "5");
  }

  @Override
  public String getCpuRequest() {
    return getEnvOrDefault(RESOURCE_CPU_REQUEST, DEFAULT_RESOURCE_REQUIREMENT_CPU);
  }

  @Override
  public String getCpuLimit() {
    return getEnvOrDefault(RESOURCE_CPU_LIMIT, DEFAULT_RESOURCE_REQUIREMENT_CPU);
  }

  @Override
  public String getMemoryRequest() {
    return getEnvOrDefault(RESOURCE_MEMORY_REQUEST, DEFAULT_RESOURCE_REQUIREMENT_MEMORY);
  }

  @Override
  public String getMemoryLimit() {
    return getEnvOrDefault(RESOURCE_MEMORY_LIMIT, DEFAULT_RESOURCE_REQUIREMENT_MEMORY);
  }

  /**
   * Returns the name of the secret to be used when pulling down docker images for jobs. Automatically
   * injected in the KubePodProcess class and used in the job pod templates. The empty string is a
   * no-op value.
   */
  @Override
  public String getJobsImagePullSecret() {
    return getEnvOrDefault(JOBS_IMAGE_PULL_SECRET, "");
  }

  @Override
  public String getS3LogBucket() {
    return logConfiguration.getS3LogBucket();
  }

  @Override
  public String getS3LogBucketRegion() {
    return logConfiguration.getS3LogBucketRegion();
  }

  @Override
  public String getAwsAccessKey() {
    return logConfiguration.getAwsAccessKey();
  }

  @Override
  public String getAwsSecretAccessKey() {
    return logConfiguration.getAwsSecretAccessKey();
  }

  @Override
  public String getS3MinioEndpoint() {
    return logConfiguration.getS3MinioEndpoint();
  }

  @Override
  public String getGcpStorageBucket() {
    return logConfiguration.getGcpStorageBucket();
  }

  @Override
  public String getGoogleApplicationCredentials() {
    return logConfiguration.getGoogleApplicationCredentials();
  }

  public LogConfigs getLogConfigs() {
    return logConfiguration;
  }

  @Override
  public boolean getPublishMetrics() {
    return getEnvOrDefault(PUBLISH_METRICS, false);
  }

  @Override
  public SecretPersistenceType getSecretPersistenceType() {
    final var secretPersistenceStr = getEnvOrDefault(SECRET_PERSISTENCE, SecretPersistenceType.NONE.name());
    return SecretPersistenceType.valueOf(secretPersistenceStr);
  }

  protected String getEnvOrDefault(final String key, final String defaultValue) {
    return getEnvOrDefault(key, defaultValue, Function.identity(), false);
  }

  private String getEnvOrDefault(final String key, final String defaultValue, final boolean isSecret) {
    return getEnvOrDefault(key, defaultValue, Function.identity(), isSecret);
  }

  private long getEnvOrDefault(final String key, final long defaultValue) {
    return getEnvOrDefault(key, defaultValue, Long::parseLong, false);
  }

  private boolean getEnvOrDefault(final String key, final boolean defaultValue) {
    return getEnvOrDefault(key, defaultValue, Boolean::parseBoolean);
  }

  private <T> T getEnvOrDefault(final String key, final T defaultValue, final Function<String, T> parser) {
    return getEnvOrDefault(key, defaultValue, parser, false);
  }

  private <T> T getEnvOrDefault(final String key, final T defaultValue, final Function<String, T> parser, final boolean isSecret) {
    final String value = getEnv.apply(key);
    if (value != null && !value.isEmpty()) {
      return parser.apply(value);
    } else {
      LOGGER.info("Using default value for environment variable {}: '{}'", key, isSecret ? "*****" : defaultValue);
      return defaultValue;
    }
  }

  private String getEnv(final String name) {
    return getEnv.apply(name);
  }

  private String getEnsureEnv(final String name) {
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
