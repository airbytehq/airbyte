/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.cdk.db.factory.DatabaseDriver.REDSHIFT;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DatabaseDriver;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.NonContainer;
import io.airbyte.cdk.testutils.TestDatabase;
import java.util.stream.Stream;
import org.jooq.SQLDialect;

public class RedshiftTestDatabase extends TestDatabase<NonContainer, RedshiftTestDatabase, RedshiftTestDatabase.RedshiftConfigBuilder> {

  private final String username;
  private final String password;
  private final String jdbcUrl;

  protected RedshiftTestDatabase(final JsonNode redshiftConfig) {
    super(new NonContainer(redshiftConfig.get(JdbcUtils.USERNAME_KEY).asText(),
        redshiftConfig.has(JdbcUtils.PASSWORD_KEY) ? redshiftConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null,
        redshiftConfig.get(JdbcUtils.JDBC_URL_KEY).asText(), REDSHIFT.getDriverClassName(), ""));
    this.username = redshiftConfig.get(JdbcUtils.USERNAME_KEY).asText();
    this.password = redshiftConfig.has(JdbcUtils.PASSWORD_KEY) ? redshiftConfig.get(JdbcUtils.PASSWORD_KEY).asText() : null;
    this.jdbcUrl = redshiftConfig.get(JdbcUtils.JDBC_URL_KEY).asText();
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
    return REDSHIFT;
  }

  @Override
  public SQLDialect getSqlDialect() {
    return SQLDialect.POSTGRES;
  }

  @Override
  public void close() {}

  static public class RedshiftConfigBuilder extends TestDatabase.ConfigBuilder<RedshiftTestDatabase, RedshiftConfigBuilder> {

    protected RedshiftConfigBuilder(RedshiftTestDatabase testdb) {
      super(testdb);
    }

  }

}
