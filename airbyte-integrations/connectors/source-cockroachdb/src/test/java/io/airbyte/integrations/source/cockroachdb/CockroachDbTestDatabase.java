/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.cockroachdb;

import static io.airbyte.integrations.source.cockroachdb.CockroachDbJdbcSourceAcceptanceTest.DB_NAME;

import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.containers.CockroachContainer;

public class CockroachDbTestDatabase extends
    TestDatabase<CockroachContainer, CockroachDbTestDatabase, CockroachDbTestDatabase.CockroachDbConfigBuilder> {

  private final CockroachContainer container;

  protected CockroachDbTestDatabase(final CockroachContainer container) {
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
    return DB_NAME;
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
    return DatabaseDriver.POSTGRESQL;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.POSTGRES;
  }

  @Override
  public void close() {
    container.close();
  }

  @Override
  public CockroachDbConfigBuilder configBuilder() {
    return new CockroachDbConfigBuilder(this)
        .with(JdbcUtils.HOST_KEY, container.getHost())
        .with(JdbcUtils.PORT_KEY, container.getMappedPort(26257))
        .with(JdbcUtils.DATABASE_KEY, DB_NAME)
        .with(JdbcUtils.USERNAME_KEY, container.getUsername())
        .with(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .with(JdbcUtils.SSL_KEY, false);
  }

  static public class CockroachDbConfigBuilder extends TestDatabase.ConfigBuilder<CockroachDbTestDatabase, CockroachDbConfigBuilder> {

    protected CockroachDbConfigBuilder(final CockroachDbTestDatabase testdb) {
      super(testdb);
    }

  }

}
