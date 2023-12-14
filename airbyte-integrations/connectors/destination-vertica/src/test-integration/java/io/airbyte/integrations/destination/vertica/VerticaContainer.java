/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.vertica;

import static java.time.temporal.ChronoUnit.SECONDS;

import java.time.Duration;
import java.util.concurrent.Future;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.wait.strategy.LogMessageWaitStrategy;
import org.testcontainers.utility.DockerImageName;

public class VerticaContainer extends JdbcDatabaseContainer<VerticaContainer> {

  private static final DockerImageName DEFAULT_IMAGE_NAME = DockerImageName.parse("vertica/vertica-ce");

  private static final int VERTICA_PORT = 5433;
  // Container defaults
  static final String DEFAULT_DATABASE_NAME = "airbyte";
  static final String DEFAULT_USER = "airbyte";
  static final String DEFAULT_PASSWORD = "airbyte123";

  private String databaseName = DEFAULT_DATABASE_NAME;
  private String username = DEFAULT_USER;
  private String password = DEFAULT_PASSWORD;
  private static final int DEFAULT_STARTUP_TIMEOUT_SECONDS = 600;
  private static final int DEFAULT_CONNECT_TIMEOUT_SECONDS = 120;
  static final String DEFAULT_TAG = "latest";

  private int startupTimeoutSeconds = 480;

  public VerticaContainer() {
    this(DEFAULT_IMAGE_NAME.withTag(DEFAULT_TAG));
  }

  public VerticaContainer(final String dockerImageName) {
    this(DockerImageName.parse(dockerImageName));
  }

  public VerticaContainer(final DockerImageName dockerImageName) {
    super(dockerImageName);
    preconfigure();
  }

  public VerticaContainer(final Future<String> dockerImageName) {
    super(dockerImageName);
    preconfigure();
  }

  private void preconfigure() {
    this.waitStrategy = new LogMessageWaitStrategy()
        .withRegEx(".*Vertica is now running.*\\s")
        .withTimes(1)
        .withStartupTimeout(Duration.of(DEFAULT_STARTUP_TIMEOUT_SECONDS, SECONDS));
    withConnectTimeoutSeconds(DEFAULT_CONNECT_TIMEOUT_SECONDS);
    addExposedPorts(VERTICA_PORT);
  }

  @Override
  public String getDriverClassName() {
    return "com.vertica.jdbc.Driver";
  }

  @Override
  public String getJdbcUrl() {
    String jdbcUrl = "jdbc:vertica://140.236.88.151:5433/PartPub80DB";
    return jdbcUrl;
  }

  @Override
  public String getUsername() {
    return username;
  }

  @Override
  public String getPassword() {
    return password;
  }

  @Override
  protected String getTestQueryString() {
    return "select * from airbyte.employe";
  }

  public Integer getVerticaPort() {
    return getMappedPort(VERTICA_PORT);
  }

  @Override
  public String getDatabaseName() {
    return databaseName;
  }

  @Override
  public VerticaContainer withStartupTimeoutSeconds(int startupTimeoutSeconds) {
    this.startupTimeoutSeconds = startupTimeoutSeconds;
    return this;
  }

}
