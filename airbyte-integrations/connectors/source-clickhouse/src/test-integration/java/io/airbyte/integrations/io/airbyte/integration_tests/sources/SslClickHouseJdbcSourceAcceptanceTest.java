/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import java.sql.JDBCType;
import java.util.List;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.GenericContainer;

public class SslClickHouseJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static GenericContainer container;
  private static JdbcDatabase jdbcDatabase;
  private static DataSource dataSource;
  private JsonNode config;
  private String dbName;

  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  public String getDriverClass() {
    return ClickHouseSource.DRIVER_CLASS;
  }

  @Override
  public String createTableQuery(final String tableName,
                                 final String columnClause,
                                 final String primaryKeyClause) {
    // ClickHouse requires Engine to be mentioned as part of create table query.
    // Refer : https://clickhouse.tech/docs/en/engines/table-engines/ for more information
    return String.format("CREATE TABLE %s(%s) %s",
        dbName + "." + tableName, columnClause, primaryKeyClause.equals("") ? "Engine = TinyLog"
            : "ENGINE = MergeTree() ORDER BY " + primaryKeyClause + " PRIMARY KEY "
                + primaryKeyClause);
  }

  @BeforeAll
  static void init() {
    container = new GenericContainer("etsybaev/clickhouse-with-ssl:dev").withExposedPorts(8443);
    container.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("username", "default")
        .put("password", "")
        .build());

    config = Jsons.clone(configWithoutDbName);

    dataSource = DataSourceFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        ClickHouseSource.DRIVER_CLASS,
        String.format("jdbc:clickhouse://%s:%d?ssl=true&sslmode=none",
            config.get("host").asText(),
            config.get("port").asInt()));

    jdbcDatabase = new DefaultJdbcDatabase(dataSource);

    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    jdbcDatabase.execute(ctx -> ctx.createStatement().execute(String.format("CREATE DATABASE %s;", dbName)));
    ((ObjectNode) config).put("database", dbName);

    super.setup();
  }

  @AfterEach
  public void tearDownMySql() throws Exception {
    jdbcDatabase.execute(ctx -> ctx.createStatement().execute(String.format("DROP DATABASE %s;", dbName)));
    super.tearDown();
  }

  @AfterAll
  public static void cleanUp() throws Exception {
    DataSourceFactory.close(dataSource);
    container.close();
  }

  @Override
  public String primaryKeyClause(final List<String> columns) {
    if (columns.isEmpty()) {
      return "";
    }

    final StringBuilder clause = new StringBuilder();
    clause.append("(");
    for (int i = 0; i < columns.size(); i++) {
      clause.append(columns.get(i));
      if (i != (columns.size() - 1)) {
        clause.append(",");
      }
    }
    clause.append(")");
    return clause.toString();
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new ClickHouseSource();
  }

}
