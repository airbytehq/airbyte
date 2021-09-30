/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MySQLContainer;

class MySqlJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  protected static final String TEST_USER = "test";
  protected static final String TEST_PASSWORD = "test";
  protected static MySQLContainer<?> container;

  protected JsonNode config;
  protected Database database;

  @BeforeAll
  static void init() throws SQLException {
    container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD)
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD);
    container.start();
    final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), "root", TEST_PASSWORD);
    connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
  }

  @BeforeEach
  public void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", Strings.addRandomSuffix("db", "_", 10))
        .put("username", TEST_USER)
        .put("password", TEST_PASSWORD)
        .build());

    database = Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:mysql://%s:%s",
            config.get("host").asText(),
            config.get("port").asText()),
        MySqlSource.DRIVER_CLASS,

        SQLDialect.MYSQL);

    database.query(ctx -> {
      ctx.fetch("CREATE DATABASE " + config.get("database").asText());
      return null;
    });
    database.close();

    super.setup();
  }

  @AfterEach
  void tearDownMySql() throws Exception {
    database.close();
    super.tearDown();
  }

  @AfterAll
  static void cleanUp() {
    container.close();
  }

  // MySql does not support schemas in the way most dbs do. Instead we namespace by db name.
  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public AbstractJdbcSource getJdbcSource() {
    return new MySqlSource();
  }

  @Override
  public String getDriverClass() {
    return MySqlSource.DRIVER_CLASS;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected = Jsons.deserialize(MoreResources.readResource("spec.json"), ConnectorSpecification.class);

    assertEquals(expected, actual);
  }

}
