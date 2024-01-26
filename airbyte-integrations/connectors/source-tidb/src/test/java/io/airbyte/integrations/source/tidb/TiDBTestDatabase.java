/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.tidb.TiDBContainer;

public class TiDBTestDatabase extends
    TestDatabase<TiDBContainer, TiDBTestDatabase, TiDBTestDatabase.TiDBDbConfigBuilder> {

  protected static final String USER = "root";
  protected static final String DATABASE = "test";
  private final TiDBContainer container;

  protected TiDBTestDatabase(final TiDBContainer container) {
    super(container);
    this.container = container;
  }

  @Override
  public String getJdbcUrl() {
    return container.getJdbcUrl();
  }

  @Override
  public String getDatabaseName() {
    return DATABASE;
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
  protected Stream<Stream<String>> inContainerBootstrapCmd() {
    return Stream.empty();
  }

  @Override
  protected Stream<String> inContainerUndoBootstrapCmd() {
    return Stream.empty();
  }

  @Override
  public DatabaseDriver getDatabaseDriver() {
    return DatabaseDriver.MYSQL;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.MYSQL;
  }

  @Override
  public void close() {
    container.close();
  }

  @Override
  public TiDBDbConfigBuilder configBuilder() {
    return new TiDBDbConfigBuilder(this)
        .with(JdbcUtils.HOST_KEY, "127.0.0.1")
        .with(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .with(JdbcUtils.USERNAME_KEY, USER)
        .with(JdbcUtils.DATABASE_KEY, DATABASE);
  }

  static public class TiDBDbConfigBuilder extends TestDatabase.ConfigBuilder<TiDBTestDatabase, TiDBDbConfigBuilder> {

    protected TiDBDbConfigBuilder(final TiDBTestDatabase testdb) {
      super(testdb);
    }

  }

}
