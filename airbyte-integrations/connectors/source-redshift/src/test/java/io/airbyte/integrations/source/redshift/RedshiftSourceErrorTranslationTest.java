/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.redshift;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.mockStatic;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.factory.DataSourceFactory;
import io.airbyte.cdk.integrations.util.ConnectorExceptionUtil;
import io.airbyte.commons.exceptions.ConfigErrorException;
import io.airbyte.commons.exceptions.ConnectionErrorException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.sql.SQLTransientConnectionException;
import java.util.Map;
import javax.sql.DataSource;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.mockito.MockedStatic;

class RedshiftSourceErrorTranslationTest {

  private static final String DRIVER_AUTH_MESSAGE =
      "[Amazon](500310) Invalid operation: password authentication failed for user \"test_user\";";

  private static final JsonNode CONFIG = Jsons.jsonNode(Map.of(
      "host", "example.redshift.amazonaws.com",
      "port", 5439,
      "database", "dev",
      "username", "test_user",
      "password", "wrong_password",
      "schemas", new String[] {"public"}));

  private MockedStatic<DataSourceFactory> dataSourceFactory;
  private PrintStream originalOut;
  private ByteArrayOutputStream capturedOut;

  @BeforeEach
  void setUp() {
    originalOut = System.out;
    capturedOut = new ByteArrayOutputStream();
    System.setOut(new PrintStream(capturedOut, true, StandardCharsets.UTF_8));
  }

  @AfterEach
  void tearDown() {
    System.setOut(originalOut);
    if (dataSourceFactory != null) {
      dataSourceFactory.close();
    }
  }

  /**
   * Mimics what HikariCP throws when the Redshift driver rejects the credentials: a
   * SQLTransientConnectionException carrying the driver's SQLSTATE, with the driver exception as
   * cause.
   */
  private void mockDataSourceFailingWith(final String sqlState, final int errorCode, final String driverMessage) throws SQLException {
    final SQLException driverException = new SQLException(driverMessage, sqlState, errorCode);
    final DataSource dataSource = mock(DataSource.class);
    when(dataSource.getConnection()).thenThrow(new SQLTransientConnectionException(
        "HikariPool-1 - Connection is not available, request timed out after 60001ms", sqlState, driverException));
    dataSourceFactory = mockStatic(DataSourceFactory.class);
    dataSourceFactory.when(() -> DataSourceFactory.create(any(), any(), any(), any(), anyMap(), any())).thenReturn(dataSource);
  }

  @ParameterizedTest
  @ValueSource(strings = {"28000", "28P01"})
  void testInvalidAuthorizationSqlStateIsTranslatedToConfigError(final String sqlState) {
    final ConnectionErrorException original = new ConnectionErrorException(sqlState, 500310, DRIVER_AUTH_MESSAGE, new SQLException());

    final RuntimeException translated = RedshiftSource.translateConnectionError(original);

    final ConfigErrorException configError = assertInstanceOf(ConfigErrorException.class, translated);
    assertEquals(RedshiftSource.AUTHENTICATION_FAILED_MESSAGE, configError.getDisplayMessage());
    assertSame(original, configError.getCause());
  }

  @ParameterizedTest
  @ValueSource(strings = {"08001", "HY000", "3D000"})
  void testNonAuthorizationConnectionErrorIsUnchanged(final String sqlState) {
    final ConnectionErrorException original = new ConnectionErrorException(sqlState, 0, "some other failure", new SQLException());

    assertSame(original, RedshiftSource.translateConnectionError(original));
  }

  @Test
  void testConnectionErrorWithoutSqlStateIsUnchanged() {
    final ConnectionErrorException original = new ConnectionErrorException("no state");

    assertSame(original, RedshiftSource.translateConnectionError(original));
  }

  @Test
  void testCheckReturnsCleanMessageOnAuthenticationFailure() throws Exception {
    mockDataSourceFailingWith("28000", 500310, DRIVER_AUTH_MESSAGE);

    final AirbyteConnectionStatus status = new RedshiftSource().check(CONFIG);

    assertEquals(Status.FAILED, status.getStatus());
    assertEquals(RedshiftSource.AUTHENTICATION_FAILED_MESSAGE, status.getMessage());
    final String output = capturedOut.toString(StandardCharsets.UTF_8);
    assertTrue(output.contains("\"failure_type\":\"config_error\""), output);
    assertTrue(output.contains("\"message\":\"" + RedshiftSource.AUTHENTICATION_FAILED_MESSAGE + "\""), output);
  }

  @Test
  void testCheckKeepsExistingMessageForOtherConnectionErrors() throws Exception {
    mockDataSourceFailingWith("08001", 0, "Connection refused");

    final AirbyteConnectionStatus status = new RedshiftSource().check(CONFIG);

    assertEquals(Status.FAILED, status.getStatus());
    assertEquals("State code: 08001; Message: Connection refused", status.getMessage());
  }

  @Test
  void testDiscoverSurfacesCleanConfigErrorOnAuthenticationFailure() throws Exception {
    mockDataSourceFailingWith("28000", 500310, DRIVER_AUTH_MESSAGE);

    final Exception thrown = assertThrows(Exception.class, () -> new RedshiftSource().discover(CONFIG));

    // Same resolution IntegrationRunner applies before emitting the config_error trace for
    // discover and read.
    final Throwable root = ConnectorExceptionUtil.getRootConfigError(thrown);
    assertTrue(ConnectorExceptionUtil.isConfigError(root));
    assertEquals(RedshiftSource.AUTHENTICATION_FAILED_MESSAGE, ConnectorExceptionUtil.getDisplayMessage(root));
  }

}
