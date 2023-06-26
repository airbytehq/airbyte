/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.source;

import com.google.common.base.Preconditions;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.version.AirbyteVersion;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.Set;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class passes environment variable to the DockerProcessFactory that runs the source in the
 * SourceAcceptanceTest.
 */
// todo (cgardens) - this cloud_deployment implicit interface is going to bite us.
public class TestEnvConfigs {

  private static final Logger LOGGER = LoggerFactory.getLogger(TestEnvConfigs.class);

  // env variable names
  public static final String AIRBYTE_ROLE = "AIRBYTE_ROLE";
  public static final String AIRBYTE_VERSION = "AIRBYTE_VERSION";
  public static final String WORKER_ENVIRONMENT = "WORKER_ENVIRONMENT";
  public static final String DEPLOYMENT_MODE = "DEPLOYMENT_MODE";
  public static final String JOB_DEFAULT_ENV_PREFIX = "JOB_DEFAULT_ENV_";

  public static final Map<String, Function<TestEnvConfigs, String>> JOB_SHARED_ENVS = Map.of(
      AIRBYTE_VERSION, (instance) -> instance.getAirbyteVersion().serialize(),
      AIRBYTE_ROLE, TestEnvConfigs::getAirbyteRole,
      DEPLOYMENT_MODE, (instance) -> instance.getDeploymentMode().name(),
      WORKER_ENVIRONMENT, (instance) -> instance.getWorkerEnvironment().name());

  enum DeploymentMode {
    OSS,
    CLOUD
  }

  enum WorkerEnvironment {
    DOCKER,
    KUBERNETES
  }

  private final Function<String, String> getEnv;
  private final Supplier<Set<String>> getAllEnvKeys;

  public TestEnvConfigs() {
    this(System.getenv());
  }

  private TestEnvConfigs(final Map<String, String> envMap) {
    getEnv = envMap::get;
    getAllEnvKeys = envMap::keySet;
  }

  // CORE
  // General
  public String getAirbyteRole() {
    return getEnv(AIRBYTE_ROLE);
  }

  public AirbyteVersion getAirbyteVersion() {
    return new AirbyteVersion(getEnsureEnv(AIRBYTE_VERSION));
  }

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

  public WorkerEnvironment getWorkerEnvironment() {
    return getEnvOrDefault(WORKER_ENVIRONMENT, WorkerEnvironment.DOCKER, s -> WorkerEnvironment.valueOf(s.toUpperCase()));
  }

  /**
   * There are two types of environment variables available to the job container:
   * <ul>
   * <li>Exclusive variables prefixed with JOB_DEFAULT_ENV_PREFIX</li>
   * <li>Shared variables defined in JOB_SHARED_ENVS</li>
   * </ul>
   */
  public Map<String, String> getJobDefaultEnvMap() {
    final Map<String, String> jobPrefixedEnvMap = getAllEnvKeys.get().stream()
        .filter(key -> key.startsWith(JOB_DEFAULT_ENV_PREFIX))
        .collect(Collectors.toMap(key -> key.replace(JOB_DEFAULT_ENV_PREFIX, ""), getEnv));
    // This method assumes that these shared env variables are not critical to the execution
    // of the jobs, and only serve as metadata. So any exception is swallowed and default to
    // an empty string. Change this logic if this assumption no longer holds.
    final Map<String, String> jobSharedEnvMap = JOB_SHARED_ENVS.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        entry -> Exceptions.swallowWithDefault(() -> Objects.requireNonNullElse(entry.getValue().apply(this), ""), "")));
    return MoreMaps.merge(jobPrefixedEnvMap, jobSharedEnvMap);
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

}
