/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.testutils;

import org.testcontainers.containers.JdbcDatabaseContainer;

public class NonContainer extends JdbcDatabaseContainer<NonContainer> {

  private final String username;
  private final String password;
  private final String jdbcUrl;

  private final String driverClassName;

  public NonContainer(final String userName,
                      final String password,
                      final String jdbcUrl,
                      final String driverClassName,
                      final String dockerImageName) {
    super(dockerImageName);
    this.username = userName;
    this.password = password;
    this.jdbcUrl = jdbcUrl;
    this.driverClassName = driverClassName;
  }

  @Override
  public String getDriverClassName() {
    return driverClassName;
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
