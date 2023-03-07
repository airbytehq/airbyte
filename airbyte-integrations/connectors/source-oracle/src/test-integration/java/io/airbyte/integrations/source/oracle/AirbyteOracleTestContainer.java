/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import static java.time.temporal.ChronoUnit.SECONDS;
import static java.util.Collections.singleton;

import java.time.Duration;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
import java.util.concurrent.Future;
import org.apache.commons.lang3.StringUtils;
import org.testcontainers.containers.JdbcDatabaseContainer;
import org.testcontainers.containers.wait.strategy.LogMessageWaitStrategy;
import org.testcontainers.utility.DockerImageName;

public class AirbyteOracleTestContainer extends JdbcDatabaseContainer<AirbyteOracleTestContainer> {

  public static final String NAME = "oracle";
  private static final DockerImageName DEFAULT_IMAGE_NAME = DockerImageName.parse("gvenzl/oracle-xe");

  static final String DEFAULT_TAG = "18.4.0-slim";
  static final String IMAGE = DEFAULT_IMAGE_NAME.getUnversionedPart();

  private static final int ORACLE_PORT = 1521;
  private static final int APEX_HTTP_PORT = 8080;

  private static final int DEFAULT_STARTUP_TIMEOUT_SECONDS = 240;
  private static final int DEFAULT_CONNECT_TIMEOUT_SECONDS = 120;

  // Container defaults
  static final String DEFAULT_DATABASE_NAME = "xepdb1";
  static final String DEFAULT_SID = "xe";
  static final String DEFAULT_SYSTEM_USER = "system";
  static final String DEFAULT_SYS_USER = "sys";

  // Test container defaults
  static final String APP_USER = "test";
  static final String APP_USER_PASSWORD = "test";

  // Restricted user and database names
  private static final List<String> ORACLE_SYSTEM_USERS = Arrays.asList(DEFAULT_SYSTEM_USER, DEFAULT_SYS_USER);

  private String databaseName = DEFAULT_DATABASE_NAME;
  private String username = APP_USER;
  private String password = APP_USER_PASSWORD;
  private boolean usingSid = false;

  public AirbyteOracleTestContainer() {
    this(DEFAULT_IMAGE_NAME.withTag(DEFAULT_TAG));
  }

  public AirbyteOracleTestContainer(final String dockerImageName) {
    this(DockerImageName.parse(dockerImageName));
  }

  public AirbyteOracleTestContainer(final DockerImageName dockerImageName) {
    super(dockerImageName);
    dockerImageName.assertCompatibleWith(DEFAULT_IMAGE_NAME);
    preconfigure();
  }

  public AirbyteOracleTestContainer(final Future<String> dockerImageName) {
    super(dockerImageName);
    preconfigure();
  }

  private void preconfigure() {
    this.waitStrategy = new LogMessageWaitStrategy()
        .withRegEx(".*DATABASE IS READY TO USE!.*\\s")
        .withTimes(1)
        .withStartupTimeout(Duration.of(DEFAULT_STARTUP_TIMEOUT_SECONDS, SECONDS));

    withConnectTimeoutSeconds(DEFAULT_CONNECT_TIMEOUT_SECONDS);
    addExposedPorts(ORACLE_PORT, APEX_HTTP_PORT);
  }

  @Override
  protected void waitUntilContainerStarted() {
    getWaitStrategy().waitUntilReady(this);
  }

  @Override
  public Set<Integer> getLivenessCheckPortNumbers() {
    return singleton(getMappedPort(ORACLE_PORT));
  }

  @Override
  public String getDriverClassName() {
    return "oracle.jdbc.OracleDriver";
  }

  @Override
  public String getJdbcUrl() {
    return isUsingSid() ? "jdbc:oracle:thin:" + "@" + getHost() + ":" + getOraclePort() + ":" + getSid()
        : "jdbc:oracle:thin:" + "@" + getHost() + ":" + getOraclePort() + "/" + getDatabaseName();
  }

  @Override
  public String getUsername() {
    // An application user is tied to the database, and therefore not authenticated to connect to SID.
    return isUsingSid() ? DEFAULT_SYSTEM_USER : username;
  }

  @Override
  public String getPassword() {
    return password;
  }

  @Override
  public String getDatabaseName() {
    return databaseName;
  }

  protected boolean isUsingSid() {
    return usingSid;
  }

  @Override
  public AirbyteOracleTestContainer withUsername(final String username) {
    if (StringUtils.isEmpty(username)) {
      throw new IllegalArgumentException("Username cannot be null or empty");
    }
    if (ORACLE_SYSTEM_USERS.contains(username.toLowerCase())) {
      throw new IllegalArgumentException("Username cannot be one of " + ORACLE_SYSTEM_USERS);
    }
    this.username = username;
    return self();
  }

  @Override
  public AirbyteOracleTestContainer withPassword(final String password) {
    if (StringUtils.isEmpty(password)) {
      throw new IllegalArgumentException("Password cannot be null or empty");
    }
    this.password = password;
    return self();
  }

  @Override
  public AirbyteOracleTestContainer withDatabaseName(final String databaseName) {
    if (StringUtils.isEmpty(databaseName)) {
      throw new IllegalArgumentException("Database name cannot be null or empty");
    }

    if (DEFAULT_DATABASE_NAME.equals(databaseName.toLowerCase())) {
      throw new IllegalArgumentException("Database name cannot be set to " + DEFAULT_DATABASE_NAME);
    }

    this.databaseName = databaseName;
    return self();
  }

  public AirbyteOracleTestContainer usingSid() {
    this.usingSid = true;
    return self();
  }

  @Override
  public AirbyteOracleTestContainer withUrlParam(final String paramName, final String paramValue) {
    throw new UnsupportedOperationException("The Oracle Database driver does not support this");
  }

  @SuppressWarnings("SameReturnValue")
  public String getSid() {
    return DEFAULT_SID;
  }

  public Integer getOraclePort() {
    return getMappedPort(ORACLE_PORT);
  }

  @SuppressWarnings("unused")
  public Integer getWebPort() {
    return getMappedPort(APEX_HTTP_PORT);
  }

  @Override
  public String getTestQueryString() {
    return "SELECT 1 FROM DUAL";
  }

  @Override
  protected void configure() {
    withEnv("ORACLE_PASSWORD", password);

    // Only set ORACLE_DATABASE if different than the default.
    if (databaseName != DEFAULT_DATABASE_NAME) {
      withEnv("ORACLE_DATABASE", databaseName);
    }

    withEnv("APP_USER", username);
    withEnv("APP_USER_PASSWORD", password);
  }

}
