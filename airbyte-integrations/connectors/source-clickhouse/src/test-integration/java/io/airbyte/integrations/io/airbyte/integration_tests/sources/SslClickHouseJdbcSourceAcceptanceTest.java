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
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.GenericContainer;

public class SslClickHouseJdbcSourceAcceptanceTest extends ClickHouseJdbcSourceAcceptanceTest {

  private static GenericContainer container;
  private static JdbcDatabase jdbcDatabase;
  private static DataSource dataSource;
  private JsonNode config;
  private String dbName;

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

}
