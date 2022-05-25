/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_DB_NAME;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_HOST_OR_PORT;
import static io.airbyte.integrations.base.errors.utils.ConnectionErrorType.INCORRECT_USERNAME_OR_PASSWORD;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import io.airbyte.protocol.models.AirbyteConnectionStatus;
import java.nio.file.Path;
import java.sql.JDBCType;
import java.sql.SQLException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

// Run as part of integration tests, instead of unit tests, because there is no test container for
// Redshift.
class RedshiftJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private JsonNode config;

  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @BeforeEach
  public void setup() throws Exception {
    config = getStaticConfig();
    super.setup();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new RedshiftSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return RedshiftSource.DRIVER_CLASS;
  }

  @AfterEach
  public void tearDownRedshift() throws SQLException {
    super.tearDown();
  }

  @Test
  void testCheckIncorrectPasswordFailure() throws Exception {
    ((ObjectNode) config).put("password", "fake");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_USERNAME_OR_PASSWORD.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectUsernameFailure() throws Exception {
    ((ObjectNode) config).put("username", "fake");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_USERNAME_OR_PASSWORD.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectHostFailure() throws Exception {
    ((ObjectNode) config).put("host", "localhost2");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_HOST_OR_PORT.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectPortFailure() throws Exception {
    ((ObjectNode) config).put("port", "0000");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_HOST_OR_PORT.getValue(), actual.getMessage());
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() throws Exception {
    ((ObjectNode) config).put("database", "wrongdatabase");
    final AirbyteConnectionStatus actual = source.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, actual.getStatus());
    Assertions.assertEquals(INCORRECT_DB_NAME.getValue(), actual.getMessage());
  }

}
