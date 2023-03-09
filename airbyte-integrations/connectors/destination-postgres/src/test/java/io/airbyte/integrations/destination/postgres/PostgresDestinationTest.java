/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.AirbyteMessageConsumer;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.test.utils.PostgreSQLContainerHelper;
import java.time.Instant;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import java.util.stream.IntStream;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class PostgresDestinationTest {

  private static PostgreSQLContainer<?> PSQL_DB;

  private static final String USERNAME = "new_user";
  private static final String DATABASE = "new_db";
  private static final String PASSWORD = "new_password";

  private static final String SCHEMA_NAME = "public";
  private static final String STREAM_NAME = "id_and_name";

  static final Map<String, String> SSL_JDBC_PARAMETERS = ImmutableMap.of(
      "ssl", "true",
      "sslmode", "require");
  private static final ConfiguredAirbyteCatalog CATALOG = new ConfiguredAirbyteCatalog().withStreams(List.of(
      CatalogHelpers.createConfiguredAirbyteStream(
          STREAM_NAME,
          SCHEMA_NAME,
          Field.of("id", JsonSchemaType.NUMBER),
          Field.of("name", JsonSchemaType.STRING))));

  private JsonNode config;

  private static final String EXPECTED_JDBC_URL = "jdbc:postgresql://localhost:1337/db?";

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 1337,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.SSL_KEY, true,
        "ssl_mode", ImmutableMap.of("mode", "require")));
  }

  private static final String EXPECTED_JDBC_ESCAPED_URL = "jdbc:postgresql://localhost:1337/db%2Ffoo?";

  private JsonNode buildConfigEscapingNeeded() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 1337,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db/foo"));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 1337,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.JDBC_URL_PARAMS_KEY, extraParam));
  }

  private JsonNode buildConfigNoExtraJdbcParametersWithoutSsl() {
    return Jsons.jsonNode(ImmutableMap.of(
        JdbcUtils.HOST_KEY, "localhost",
        JdbcUtils.PORT_KEY, 1337,
        JdbcUtils.USERNAME_KEY, "user",
        JdbcUtils.DATABASE_KEY, "db",
        JdbcUtils.SSL_KEY, false));
  }

  @BeforeAll
  static void init() {
    PSQL_DB = new PostgreSQLContainer<>("postgres:13-alpine");
    PSQL_DB.start();
  }

  @BeforeEach
  void setup() {
    config = PostgreSQLContainerHelper.createDatabaseWithRandomNameAndGetPostgresConfig(PSQL_DB);
  }

  @AfterAll
  static void cleanUp() {
    PSQL_DB.close();
  }

  @Test
  void testJdbcUrlAndConfigNoExtraParams() {
    final JsonNode jdbcConfig = new PostgresDestination().toJdbcConfig(buildConfigNoJdbcParameters());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlWithEscapedDatabaseName() {
    final JsonNode jdbcConfig = new PostgresDestination().toJdbcConfig(buildConfigEscapingNeeded());
    assertEquals(EXPECTED_JDBC_ESCAPED_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlEmptyExtraParams() {
    final JsonNode jdbcConfig = new PostgresDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(""));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testJdbcUrlExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = new PostgresDestination().toJdbcConfig(buildConfigWithExtraJdbcParameters(extraParam));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get(JdbcUtils.JDBC_URL_KEY).asText());
  }

  @Test
  void testDefaultParamsNoSSL() {
    final Map<String, String> defaultProperties = new PostgresDestination().getDefaultConnectionProperties(
        buildConfigNoExtraJdbcParametersWithoutSsl());
    assertEquals(new HashMap<>(), defaultProperties);
  }

  @Test
  void testDefaultParamsWithSSL() {
    final Map<String, String> defaultProperties = new PostgresDestination().getDefaultConnectionProperties(
        buildConfigNoJdbcParameters());
    assertEquals(SSL_JDBC_PARAMETERS, defaultProperties);
  }

  @Test
  void testCheckIncorrectPasswordFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, "fake");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final PostgresDestination destination = new PostgresDestination();
    final var actual = destination.check(config);
    assertTrue(actual.getMessage().contains("State code: 08001;"));
  }

  @Test
  public void testCheckIncorrectUsernameFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, "");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final PostgresDestination destination = new PostgresDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertTrue(status.getMessage().contains("State code: 08001;"));
  }

  @Test
  public void testCheckIncorrectHostFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.HOST_KEY, "localhost2");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final PostgresDestination destination = new PostgresDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertTrue(status.getMessage().contains("State code: 08001;"));
  }

  @Test
  public void testCheckIncorrectPortFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.PORT_KEY, "30000");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final PostgresDestination destination = new PostgresDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertTrue(status.getMessage().contains("State code: 08001;"));
  }

  @Test
  public void testCheckIncorrectDataBaseFailure() {
    final var config = buildConfigNoJdbcParameters();
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, "wrongdatabase");
    ((ObjectNode) config).put(JdbcUtils.SCHEMA_KEY, "public");
    final PostgresDestination destination = new PostgresDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    assertTrue(status.getMessage().contains("State code: 08001;"));
  }

  @Test
  public void testUserHasNoPermissionToDataBase() throws Exception {
    final JdbcDatabase database = PostgreSQLContainerHelper.getJdbcDatabaseFromConfig(PostgreSQLContainerHelper.getDataSourceFromConfig(config));

    database.execute(connection -> connection.createStatement()
        .execute(String.format("create user %s with password '%s';", USERNAME, PASSWORD)));
    database.execute(connection -> connection.createStatement()
        .execute(String.format("create database %s;", DATABASE)));
    // deny access for database for all users from group public
    database.execute(connection -> connection.createStatement()
        .execute(String.format("revoke all on database %s from public;", DATABASE)));

    ((ObjectNode) config).put(JdbcUtils.USERNAME_KEY, USERNAME);
    ((ObjectNode) config).put(JdbcUtils.PASSWORD_KEY, PASSWORD);
    ((ObjectNode) config).put(JdbcUtils.DATABASE_KEY, DATABASE);

    final Destination destination = new PostgresDestination();
    final AirbyteConnectionStatus status = destination.check(config);
    Assertions.assertEquals(AirbyteConnectionStatus.Status.FAILED, status.getStatus());
  }

  // This test is a bit redundant with PostgresIntegrationTest. It makes it easy to run the
  // destination in the same process as the test allowing us to put breakpoint in, which is handy for
  // debugging (especially since we use postgres as a guinea pig for most features).
  @Test
  void sanityTest() throws Exception {
    final Destination destination = new PostgresDestination();
    final AirbyteMessageConsumer consumer = destination.getConsumer(config, CATALOG, Destination::defaultOutputRecordCollector);
    final List<AirbyteMessage> expectedRecords = getNRecords(10);

    consumer.start();
    expectedRecords.forEach(m -> {
      try {
        consumer.accept(m);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
    consumer.accept(new AirbyteMessage()
        .withType(Type.STATE)
        .withState(new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(SCHEMA_NAME + "." + STREAM_NAME, 10)))));
    consumer.close();

    final JdbcDatabase database = PostgreSQLContainerHelper.getJdbcDatabaseFromConfig(PostgreSQLContainerHelper.getDataSourceFromConfig(config));

    final List<JsonNode> actualRecords = database.bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery("SELECT * FROM public._airbyte_raw_id_and_name;"),
        JdbcUtils.getDefaultSourceOperations()::rowToJson);

    assertEquals(
        expectedRecords.stream().map(AirbyteMessage::getRecord).map(AirbyteRecordMessage::getData).collect(Collectors.toList()),
        actualRecords.stream().map(o -> o.get("_airbyte_data").asText()).map(Jsons::deserialize).collect(Collectors.toList()));
  }

  private List<AirbyteMessage> getNRecords(final int n) {
    return IntStream.range(0, n)
        .boxed()
        .map(i -> new AirbyteMessage()
            .withType(Type.RECORD)
            .withRecord(new AirbyteRecordMessage()
                .withStream(STREAM_NAME)
                .withNamespace(SCHEMA_NAME)
                .withEmittedAt(Instant.now().toEpochMilli())
                .withData(Jsons.jsonNode(ImmutableMap.of("id", i, "name", "human " + i)))))
        .collect(Collectors.toList());
  }

}
