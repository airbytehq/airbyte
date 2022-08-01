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

public class SslClickHouseJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static GenericContainer container;
  private static JdbcDatabase jdbcDatabase;
  private static DataSource dataSource;
  private JsonNode config;
  private String dbName;

  @BeforeAll
  static void init() throws IOException, InterruptedException {
    container = new GenericContainer<>(new ImageFromDockerfile("clickhouse-test")
        .withFileFromClasspath("Dockerfile", "docker/Dockerfile")
        .withFileFromClasspath("clickhouse_certs.sh", "docker/clickhouse_certs.sh"))
            .withEnv("TZ", "UTC")
            .withExposedPorts(8123, 8443)
            .withClasspathResourceMapping("ssl_ports.xml", "/etc/clickhouse-server/config.d/ssl_ports.xml", BindMode.READ_ONLY)
            .waitingFor(Wait.forHttp("/ping").forPort(8123)
                .forStatusCode(200).withStartupTimeout(Duration.of(60, SECONDS)));
    container.start();
  }

  @AfterAll
  public static void cleanUp() throws Exception {
    DataSourceFactory.close(dataSource);
    container.close();
  }

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
