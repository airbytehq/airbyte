/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.teradata;

import static io.airbyte.cdk.db.factory.DatabaseDriver.TERADATA;
import static io.airbyte.integrations.source.teradata.TeradataJdbcSourceAcceptanceTest.deleteDatabase;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.NonContainer;
import io.airbyte.cdk.testutils.TestDatabase;
import java.util.stream.Stream;
import org.jooq.SQLDialect;

public class TeradataTestDatabase extends TestDatabase<NonContainer, TeradataTestDatabase, TeradataTestDatabase.TeradataDbConfigBuilder> {

  private final String username;
  private final String password;
  private final String jdbcUrl;
  private final String databaseName;

  protected TeradataTestDatabase(final JsonNode teradataConfig) {
    super(new NonContainer(teradataConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        teradataConfig.has(JdbcUtils.PASSWORD_KEY) ? teradataConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        teradataConfig.get(JdbcUtils.JDBC_URL_KEY).asText(), TERADATA.getDriverClassName(), ""));
    this.username = teradataConfig.get(JdbcUtils.USERNAME_KEY).asText();
    this.password = teradataConfig.has(JdbcUtils.PASSWORD_KEY) ? teradataConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null;
    this.jdbcUrl = teradataConfig.get(JdbcUtils.JDBC_URL_KEY).asText();
    this.databaseName = teradataConfig.get(JdbcUtils.SCHEMA_KEY).asText();
  }

  @Override
  public String getDatabaseName() {
    return databaseName;
  }

  @Override
  public String getJdbcUrl() {
    return jdbcUrl;
  }

  @Override
  public String getPassword() {
    return password;
  }

  @Override
  public String getUserName() {
    return username;
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
    return TERADATA;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.DEFAULT;
  }

  @Override
  public void close() {
    deleteDatabase();
  }

  static public class TeradataDbConfigBuilder extends TestDatabase.ConfigBuilder<TeradataTestDatabase, TeradataDbConfigBuilder> {

    protected TeradataDbConfigBuilder(final TeradataTestDatabase testdb) {
      super(testdb);
    }

  }

}
