/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql;

import static io.airbyte.cdk.integrations.debezium.DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.JdbcConnector;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.MSSQLServerContainer;

public class MssqlAgentStateTest {

  private static MsSQLTestDatabase testdb;
  private static DataSource testDataSource;
  private static MSSQLServerContainer privateContainer;

  @BeforeAll
  public static void setup() {
    privateContainer = new MsSQLContainerFactory().exclusive(
        MsSQLTestDatabase.BaseImage.MSSQL_2022.reference,
        MsSQLTestDatabase.ContainerModifier.AGENT);
    testdb = new MsSQLTestDatabase(privateContainer);
    testdb
        .withConnectionProperty("encrypt", "false")
        .withConnectionProperty("trustServerCertificate", "true")
        .withConnectionProperty("databaseName", testdb.getDatabaseName())
        .initialized()
        .withWaitUntilAgentRunning()
        .withCdc();
    testDataSource = DataSourceFactory.create(
        testdb.getUserName(),
        testdb.getPassword(),
        testdb.getDatabaseDriver().getDriverClassName(),
        testdb.getJdbcUrl(),
        Map.of("encrypt", "false", "trustServerCertificate", "true"),
        JdbcConnector.CONNECT_TIMEOUT_DEFAULT);
  }

  @AfterAll
  static void tearDown() {
    try {
      DataSourceFactory.close(testDataSource);
      testdb.close();
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
    privateContainer.close();
  }

  protected MssqlSource source() {
    return new MssqlSource();
  }

  private JdbcDatabase testDatabase() {
    return new DefaultJdbcDatabase(testDataSource);
  }

  protected JsonNode config() {
    return testdb.configBuilder()
        .withHostAndPort()
        .withDatabase()
        .with(JdbcUtils.USERNAME_KEY, testdb.getUserName())
        .with(JdbcUtils.PASSWORD_KEY, testdb.getPassword())
        .withCdcReplication()
        .withoutSsl()
        .with(SYNC_CHECKPOINT_RECORDS_PROPERTY, 1)
        .build();
  }

  @Test
  void testAssertSqlServerAgentRunning() throws Exception {
    testdb.withAgentStopped().withWaitUntilAgentStopped();
    // assert expected failure if sql server agent stopped
    assertThrows(RuntimeException.class,
        () -> source().assertSqlServerAgentRunning(testDatabase()));
    // assert success if sql server agent running
    testdb.withAgentStarted().withWaitUntilAgentRunning();
    assertDoesNotThrow(() -> source().assertSqlServerAgentRunning(testDatabase()));
  }

  // Ensure the CDC check operations are included when CDC is enabled
  // todo: make this better by checking the returned checkOperations from source.getCheckOperations
  @Test
  void testCdcCheckOperations() throws Exception {
    // assertCdcEnabledInDb
    testdb.withoutCdc();
    AirbyteConnectionStatus status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.withCdc();
    // assertCdcSchemaQueryable
    testdb.with("REVOKE SELECT ON SCHEMA :: [cdc] TO %s", testdb.getUserName());
    status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.with("GRANT SELECT ON SCHEMA :: [cdc] TO %s", testdb.getUserName());

    // assertSqlServerAgentRunning

    testdb.withAgentStopped().withWaitUntilAgentStopped();
    status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
    testdb.withAgentStarted().withWaitUntilAgentRunning();
    status = source().check(config());
    assertEquals(status.getStatus(), AirbyteConnectionStatus.Status.FAILED);
  }

}
