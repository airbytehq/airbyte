/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.db2;

import static io.airbyte.integrations.source.db2.Db2JdbcSourceAcceptanceTest.deleteTablesAndSchema;

import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.TestDatabase;
import io.airbyte.commons.json.Jsons;
import java.util.stream.Stream;
import org.jooq.SQLDialect;
import org.testcontainers.containers.Db2Container;

public class Db2TestDatabase extends
    TestDatabase<Db2Container, Db2TestDatabase, Db2TestDatabase.Db2DbConfigBuilder> {

  private final Db2Container container;

  protected Db2TestDatabase(final Db2Container container) {
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
    return container.getDatabaseName();
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
    return DatabaseDriver.DB2;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.DEFAULT;
  }

  @Override
  public void close() {
    deleteTablesAndSchema(this);
  }

  @Override
  public Db2DbConfigBuilder configBuilder() {
    return new Db2DbConfigBuilder(this)
        .with(JdbcUtils.HOST_KEY, container.getHost())
        .with(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .with("db", container.getDatabaseName())
        .with(JdbcUtils.USERNAME_KEY, container.getUsername())
        .with(JdbcUtils.PASSWORD_KEY, container.getPassword())
        .with(JdbcUtils.ENCRYPTION_KEY, Jsons.jsonNode(ImmutableMap.builder()
            .put("encryption_method", "unencrypted")
            .build()));
  }

  static public class Db2DbConfigBuilder extends TestDatabase.ConfigBuilder<Db2TestDatabase, Db2DbConfigBuilder> {

    protected Db2DbConfigBuilder(final Db2TestDatabase testdb) {
      super(testdb);
    }

  }

}
