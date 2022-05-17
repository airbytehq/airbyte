/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcStressTest;
import java.sql.Connection;
import java.sql.DriverManager;
import java.util.Optional;
import java.util.concurrent.Callable;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.containers.MySQLContainer;

@Disabled
class MySqlStressTest extends JdbcStressTest {

  private static final String TEST_USER = "test";
  private static final Callable<String> TEST_PASSWORD = () -> "test";
  private static MySQLContainer<?> container;

  private JsonNode config;
  private Database database;
  private DSLContext dslContext;

  @BeforeAll
  static void init() throws Exception {
    container = new MySQLContainer<>("mysql:8.0")
        .withUsername(TEST_USER)
        .withPassword(TEST_PASSWORD.call())
        .withEnv("MYSQL_ROOT_HOST", "%")
        .withEnv("MYSQL_ROOT_PASSWORD", TEST_PASSWORD.call());
    container.start();
    final Connection connection = DriverManager.getConnection(container.getJdbcUrl(), "root", TEST_PASSWORD.call());
    connection.createStatement().execute("GRANT ALL PRIVILEGES ON *.* TO '" + TEST_USER + "'@'%';\n");
  }

  @BeforeEach
  public void setup() throws Exception {
    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", container.getHost())
        .put("port", container.getFirstMappedPort())
        .put("database", Strings.addRandomSuffix("db", "_", 10))
        .put("username", TEST_USER)
        .put("password", TEST_PASSWORD.call())
        .build());

    dslContext = DSLContextFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.MYSQL.getDriverClassName(),
        String.format("jdbc:mysql://%s:%s",
            config.get("host").asText(),
            config.get("port").asText()), SQLDialect.MYSQL);
    database = new Database(dslContext);

    database.query(ctx -> {
      ctx.fetch("CREATE DATABASE " + config.get("database").asText());
      return null;
    });

    super.setup();
  }

  @AfterEach
  void tearDown() {
    dslContext.close();
  }

  @AfterAll
  static void cleanUp() {
    container.close();
  }

  // MySql does not support schemas in the way most dbs do. Instead we namespace by db name.
  @Override
  public Optional<String> getDefaultSchemaName() {
    return Optional.of(config.get("database").asText());
  }

  @Override
  public AbstractJdbcSource<MysqlType> getSource() {
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

}
