/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import static io.airbyte.cdk.db.factory.DatabaseDriver.SNOWFLAKE;

import org.testcontainers.containers.JdbcDatabaseContainer;

public class NonContainer extends JdbcDatabaseContainer<NonContainer> {

  private final String username;
  private final String password;
  private final String jdbcUrl;

  public NonContainer(final String userName,
                      final String password,
                      final String jdbcUrl,
                      final String dockerImageName) {
    super(dockerImageName);
    this.username = userName;
    this.password = password;
    this.jdbcUrl = jdbcUrl;
  }

  @Override
  public String getDriverClassName() {
    return SNOWFLAKE.getDriverClassName();
  }

  @Override
  public String getJdbcUrl() {
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
    return "SELECT 1";
  }

}
