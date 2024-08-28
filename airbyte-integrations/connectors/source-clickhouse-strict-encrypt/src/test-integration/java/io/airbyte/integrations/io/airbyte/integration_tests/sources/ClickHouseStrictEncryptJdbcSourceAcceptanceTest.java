/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.integrations.io.airbyte.integration_tests.sources.ClickHouseStrictEncryptTestDatabase.DEFAULT_DB_NAME;
import static io.airbyte.integrations.io.airbyte.integration_tests.sources.ClickHouseStrictEncryptTestDatabase.HTTPS_PORT;
import static java.time.temporal.ChronoUnit.SECONDS;
import static org.junit.Assert.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.base.ssh.SshHelpers;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.integrations.source.clickhouse.ClickHouseStrictEncryptSource;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import java.time.Duration;
import java.util.List;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.testcontainers.clickhouse.ClickHouseContainer;
import org.testcontainers.containers.BindMode;
import org.testcontainers.containers.wait.strategy.Wait;
import org.testcontainers.utility.MountableFile;

@Disabled
public class ClickHouseStrictEncryptJdbcSourceAcceptanceTest
    extends JdbcSourceAcceptanceTest<ClickHouseStrictEncryptSource, ClickHouseStrictEncryptTestDatabase> {

  public static final Integer HTTP_PORT = 8123;
  public static final Integer NATIVE_PORT = 9000;

  public static final Integer NATIVE_SECURE_PORT = 9440;

  @Override
  protected ClickHouseStrictEncryptTestDatabase createTestDatabase() {
    final ClickHouseContainer db = new ClickHouseContainer("clickhouse/clickhouse-server:22.5")
        .withEnv("TZ", "UTC")
        .withExposedPorts(HTTP_PORT, NATIVE_PORT, HTTPS_PORT, NATIVE_SECURE_PORT)
        .withCopyFileToContainer(MountableFile.forClasspathResource("/docker/clickhouse_certs.sh"),
            "/docker-entrypoint-initdb.d/clickhouse_certs.sh")
        .withClasspathResourceMapping("ssl_ports.xml", "/etc/clickhouse-server/config.d/ssl_ports.xml", BindMode.READ_ONLY)
        .waitingFor(Wait.forHttp("/ping").forPort(HTTP_PORT)
            .forStatusCode(200).withStartupTimeout(Duration.of(60, SECONDS)));
    db.start();
    return new ClickHouseStrictEncryptTestDatabase(db).initialized();
  }

  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public JsonNode config() {
    return Jsons.clone(testdb.configBuilder().build());
  }

  @Override
  protected ClickHouseStrictEncryptSource source() {
    return new ClickHouseStrictEncryptSource();
  }

  @Override
  public String createTableQuery(final String tableName,
                                 final String columnClause,
                                 final String primaryKeyClause) {
    // ClickHouse requires Engine to be mentioned as part of create table query.
    // Refer : https://clickhouse.tech/docs/en/engines/table-engines/ for more information
    return String.format("CREATE TABLE %s(%s) %s",
        DEFAULT_DB_NAME + "." + tableName, columnClause, primaryKeyClause.equals("") ? "Engine = TinyLog"
            : "ENGINE = MergeTree() ORDER BY " + primaryKeyClause + " PRIMARY KEY "
                + primaryKeyClause);
  }

  @BeforeAll
  static void init() {
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s Array(UInt32)) ENGINE = MergeTree ORDER BY tuple();";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES([12, 13, 0, 1]);";
    CREATE_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s Nullable(VARCHAR(20))) ENGINE = MergeTree ORDER BY tuple();";
    INSERT_TABLE_WITH_NULLABLE_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES('Hello world :)');";
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

  @Test
  void testSpec() throws Exception {
    final ConnectorSpecification actual = source().spec();
    final ConnectorSpecification expected =
        SshHelpers.injectSshIntoSpec(Jsons.deserialize(MoreResources.readResource("expected_spec.json"),
            ConnectorSpecification.class));
    assertEquals(expected, actual);
  }

}
