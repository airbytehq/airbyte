/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static java.time.temporal.ChronoUnit.SECONDS;
import static org.junit.Assert.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.base.ssh.SshHelpers;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.integrations.source.clickhouse.ClickHouseStrictEncryptSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.util.HostPortResolver;
import io.airbyte.protocol.models.ConnectorSpecification;
import java.sql.JDBCType;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.images.builder.ImageFromDockerfile;

public class ClickHouseStrictEncryptJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  public static final Integer HTTP_PORT = 8123;
  public static final Integer NATIVE_PORT = 9000;
  public static final Integer HTTPS_PORT = 8443;
  public static final Integer NATIVE_SECURE_PORT = 9440;
  private static final String DEFAULT_DB_NAME = "default";
  private static final String DEFAULT_USER_NAME = "default";

  private static GenericContainer container;
  private static JdbcDatabase db;
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
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s Array(UInt32)) ENGINE = MergeTree ORDER BY tuple();";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES([12, 13, 0, 1]);)";
    CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s Nullable(VARCHAR(20))) ENGINE = MergeTree ORDER BY tuple();";
    INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES('Hello world :)');";

    container = new GenericContainer<>(new ImageFromDockerfile("clickhouse-test")
        .withFileFromClasspath("Dockerfile", "docker/Dockerfile")
        .withFileFromClasspath("clickhouse_certs.sh", "docker/clickhouse_certs.sh"))
            .withEnv("TZ", "UTC")
            .withExposedPorts(HTTP_PORT, NATIVE_PORT, HTTPS_PORT, NATIVE_SECURE_PORT)
            .withClasspathResourceMapping("ssl_ports.xml", "/etc/clickhouse-server/config.d/ssl_ports.xml", BindMode.READ_ONLY)
            .waitingFor(Wait.forHttp("/ping").forPort(HTTP_PORT)
                .forStatusCode(200).withStartupTimeout(Duration.of(60, SECONDS)));
    container.start();
  }

  @BeforeEach
  public void setup() throws Exception {
    final JsonNode configWithoutDbName = Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveIpAddress(container))
        .put(JdbcUtils.PORT_KEY, HTTPS_PORT)
        .put(JdbcUtils.USERNAME_KEY, DEFAULT_USER_NAME)
        .put("database", DEFAULT_DB_NAME)
        .put(JdbcUtils.PASSWORD_KEY, "")
        .build());

    db = new DefaultJdbcDatabase(
        DataSourceFactory.create(
            configWithoutDbName.get(JdbcUtils.USERNAME_KEY).asText(),
            configWithoutDbName.get(JdbcUtils.PASSWORD_KEY).asText(),
            ClickHouseSource.DRIVER_CLASS,
            String.format(DatabaseDriver.CLICKHOUSE.getUrlFormatString() + "?sslmode=none",
                ClickHouseSource.HTTPS_PROTOCOL,
                configWithoutDbName.get(JdbcUtils.HOST_KEY).asText(),
                configWithoutDbName.get(JdbcUtils.PORT_KEY).asInt(),
                configWithoutDbName.get("database").asText())));

    dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();

    db.execute(ctx -> ctx.createStatement().execute(String.format("CREATE DATABASE %s;", dbName)));
    config = Jsons.clone(configWithoutDbName);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, dbName);

    super.setup();
  }

  @AfterEach
  public void tearDownMySql() throws Exception {
    db.execute(ctx -> ctx.createStatement().execute(String.format("DROP DATABASE %s;", dbName)));
    super.tearDown();
  }

  @AfterAll
  public static void cleanUp() throws Exception {
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

  @Override
  public Source getSource() {
    return new ClickHouseStrictEncryptSource();
  }

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source.spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"),
            ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

}
