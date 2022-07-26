/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static java.time.temporal.ChronoUnit.SECONDS;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import java.io.IOException;
import java.sql.JDBCType;
import java.time.Duration;
import java.util.List;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.images.builder.ImageFromDockerfile;

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
        .put(JdbcUtils.HOST_KEY, "localhost")
        .put(JdbcUtils.PORT_KEY, container.getMappedPort(8443))
        .put(JdbcUtils.USERNAME_KEY, "default")
        .put(JdbcUtils.PASSWORD_KEY, "")
        .build());

    config = Jsons.clone(configWithoutDbName);

    dataSource = DataSourceFactory.create(
        config.get(JdbcUtils.USERNAME_KEY).asText(),
        config.get(JdbcUtils.PASSWORD_KEY).asText(),
        ClickHouseSource.DRIVER_CLASS,
        String.format("jdbc:clickhouse:https://%s:%d?sslmode=NONE",
            config.get(JdbcUtils.HOST_KEY).asText(),
            config.get(JdbcUtils.PORT_KEY).asInt()));

    jdbcDatabase = new DefaultJdbcDatabase(dataSource);

    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    jdbcDatabase.execute(ctx -> ctx.createStatement().execute(String.format("CREATE DATABASE %s;", dbName)));
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, dbName);

    super.setup();
  }

  @AfterEach
  public void tearDownClickHouse() throws Exception {
    jdbcDatabase.execute(ctx -> ctx.createStatement().execute(String.format("DROP DATABASE %s;", dbName)));
    super.tearDown();
  }

  @AfterAll
  public static void cleanUp() throws Exception {
    DataSourceFactory.close(dataSource);
    container.close();
  }

}
