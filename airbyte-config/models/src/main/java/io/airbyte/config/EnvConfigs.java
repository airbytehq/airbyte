/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.config;

import com.google.common.base.Preconditions;
import java.nio.file.Path;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class EnvConfigs implements Configs {

  private static final Logger LOGGER = LoggerFactory.getLogger(EnvConfigs.class);

  public static final String AIRBYTE_ROLE = "AIRBYTE_ROLE";
  public static final String AIRBYTE_VERSION = "AIRBYTE_VERSION";
  public static final String JOB_ENVIRONMENT = "JOB_ENVIRONMENT";
  public static final String WORKSPACE_ROOT = "WORKSPACE_ROOT";
  public static final String WORKSPACE_DOCKER_MOUNT = "WORKSPACE_DOCKER_MOUNT";
  public static final String LOCAL_ROOT = "LOCAL_ROOT";
  public static final String LOCAL_DOCKER_MOUNT = "LOCAL_DOCKER_MOUNT";
  public static final String CONFIG_ROOT = "CONFIG_ROOT";
  public static final String DOCKER_NETWORK = "DOCKER_NETWORK";
  public static final String TRACKING_STRATEGY = "TRACKING_STRATEGY";
  public static final String DATABASE_USER = "DATABASE_USER";
  public static final String DATABASE_PASSWORD = "DATABASE_PASSWORD";
  public static final String DATABASE_URL = "DATABASE_URL";

  public static final String DEFAULT_NETWORK = "host";

  private final Function<String, String> getEnv;

  public EnvConfigs() {
    this(System::getenv);
  }

  EnvConfigs(final Function<String, String> getEnv) {
    this.getEnv = getEnv;
  }

  @Override
  public String getAirbyteRole() {
    return getEnv(AIRBYTE_ROLE);
  }

  @Override
  public String getAirbyteVersion() {
    return getEnsureEnv(AIRBYTE_VERSION);
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
  public String getWorkspaceDockerMount() {
    final String mount = getEnv.apply(WORKSPACE_DOCKER_MOUNT);
    if (mount != null) {
      return mount;
    }

    LOGGER.info(WORKSPACE_DOCKER_MOUNT + " not found, defaulting to " + WORKSPACE_ROOT);
    return getWorkspaceRoot().toString();
  }

  @Override
  public String getLocalDockerMount() {
    final String mount = getEnv.apply(LOCAL_DOCKER_MOUNT);
    if (mount != null) {
      return mount;
    }

    LOGGER.info(LOCAL_DOCKER_MOUNT + " not found, defaulting to " + LOCAL_ROOT);
    return getLocalRoot().toString();
  }

  @Override
  public String getDockerNetwork() {
    final String network = getEnv.apply(DOCKER_NETWORK);
    if (network != null) {
      return network;
    }

    LOGGER.info(DOCKER_NETWORK + " not found, defaulting to " + DEFAULT_NETWORK);
    return DEFAULT_NETWORK;
  }

  @Override
  public TrackingStrategy getTrackingStrategy() {
    final String trackingStrategy = getEnv.apply(TRACKING_STRATEGY);
    if (trackingStrategy == null) {
      LOGGER.info("TRACKING_STRATEGY not set, defaulting to " + TrackingStrategy.LOGGING);
      return TrackingStrategy.LOGGING;
    }

    try {
      return TrackingStrategy.valueOf(trackingStrategy.toUpperCase());
    } catch (IllegalArgumentException e) {
      LOGGER.info(trackingStrategy + " not recognized, defaulting to " + TrackingStrategy.LOGGING);
      return TrackingStrategy.LOGGING;
    }
  }

  @Override
  public JobEnvironment getWorkerEnvironment() {
    final String jobEnvironment = getEnv.apply(JOB_ENVIRONMENT);
    if (jobEnvironment != null) {
      return JobEnvironment.valueOf(jobEnvironment.toUpperCase());
    }

    LOGGER.info(JOB_ENVIRONMENT + " not found, defaulting to " + JobEnvironment.DOCKER);
    return JobEnvironment.DOCKER;
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
