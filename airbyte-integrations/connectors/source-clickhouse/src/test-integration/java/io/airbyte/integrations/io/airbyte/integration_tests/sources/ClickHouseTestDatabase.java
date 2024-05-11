/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.clickhouse.ClickHouseContainer;

public class ClickHouseTestDatabase extends
    TestDatabase<ClickHouseContainer, ClickHouseTestDatabase, ClickHouseTestDatabase.ClickHouseConfigBuilder> {

  private static final String SCHEMA_NAME = "default";

  private final ClickHouseContainer container;

  protected ClickHouseTestDatabase(final ClickHouseContainer container) {
    super(container);
    this.container = container;
  }

  @Override
  public String getJdbcUrl() {
    return container.getJdbcUrl();
  }

  @Override
  public String getUserName() {
    return container.getUsername();
  }

  @Override
  public String getPassword() {
    return container.getPassword();
  }

  @Override
  public String getDatabaseName() {
    return SCHEMA_NAME;
  }

  @Override
  public ClickHouseConfigBuilder configBuilder() {
    return new ClickHouseConfigBuilder(this)
        .with(JdbcUtils.HOST_KEY, container.getHost())
        .with(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .with(JdbcUtils.DATABASE_KEY, SCHEMA_NAME)
        .with(JdbcUtils.USERNAME_KEY, container.getUsername())
        .with(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .with(JdbcUtils.SSL_KEY, false);
  }

  @Override
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    return Stream.empty();
  }

  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return Stream.empty();
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return DatabaseDriver.CLICKHOUSE;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.DEFAULT;
  }

  @Override
  public void close() {
    container.close();
  }

  @Override
  public ClickHouseConfigBuilder integrationTestConfigBuilder() {
    return super.integrationTestConfigBuilder();
  }

  static public class ClickHouseConfigBuilder extends TestDatabase.ConfigBuilder<ClickHouseTestDatabase, ClickHouseConfigBuilder> {

    protected ClickHouseConfigBuilder(final ClickHouseTestDatabase testdb) {
      super(testdb);
    }

  }

}
