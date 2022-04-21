/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;

import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Tests that the postgres spec passes JsonSchema validation. While this may seem like overkill, we
 * are doing it because there are some gotchas in correctly configuring the oneOf.
 */
public class PostgresSpecTest {

  private static final String CONFIGURATION = "{  "
      + "\"password\" : \"pwd\",  "
      + "\"username\" : \"postgres\",  "
      + "\"database\" : \"postgres_db\",  "
      + "\"schemas\" : [\"public\"],  "
      + "\"port\" : 5432,  "
      + "\"host\" : \"localhost\",  "
      + "\"ssl\" : true, "
      + "\"jdbc_url_params\" : \"foo=bar\", "
      + "\"replication_method\" : {    \"method\" : \"CDC\", \"replication_slot\" : \"ab_slot\", \"publication\" : \"ab_publication\"  }"
      + "}";
  private static JsonNode schema;
  private static JsonSchemaValidator validator;

  private static final String EXPECTED_JDBC_URL = "jdbc:postgresql://localhost:1337/db?";

  private JsonNode buildConfigNoJdbcParameters() {
    return Jsons.jsonNode(ImmutableMap.of(
            "host", "localhost",
            "port", 1337,
            "username", "user",
            "database", "db"));
  }

  private JsonNode buildConfigWithExtraJdbcParameters(final String extraParam) {
    return Jsons.jsonNode(ImmutableMap.of(
            "host", "localhost",
            "port", 1337,
            "username", "user",
            "database", "db",
            "jdbc_url_params", extraParam));
  }

  private JsonNode buildConfigNoExtraJdbcParametersWithoutSsl() {
    return Jsons.jsonNode(ImmutableMap.of(
            "host", "localhost",
            "port", 1337,
            "username", "user",
            "database", "db",
            "ssl", false));
  }

  @BeforeAll
  static void init() throws IOException {
    final String spec = MoreResources.readResource("spec.json");
    final File schemaFile = IOs.writeFile(Files.createTempDirectory(Path.of("/tmp"), "pg-spec-test"), "schema.json", spec).toFile();
    schema = JsonSchemaValidator.getSchema(schemaFile).get("connectionSpecification");
    validator = new JsonSchemaValidator();
  }

  @Test
  void testDatabaseMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("database");
    assertFalse(validator.test(schema, config));
  }

  @Test
  void testSchemaMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("schemas");
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testWithoutReplicationMethod() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("replication_method");

    assertTrue(validator.test(schema, config));
  }

  @Test
  void testWithReplicationMethodWithReplicationSlot() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testWithReplicationMethodMissingPublication() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config.get("replication_method")).remove("replication_slot");

    assertFalse(validator.test(schema, config));
  }

  @Test
  void testWithReplicationMethodStandard() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config.get("replication_method")).remove("replication_slot");
    ((ObjectNode) config.get("replication_method")).remove("publication");
    ((ObjectNode) config.get("replication_method")).put("method", "Standard");
    assertTrue(validator.test(schema, config));

    final JsonNode configReplicationMethodNotSet = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) configReplicationMethodNotSet).remove("replication_method");
    assertTrue(validator.test(schema, configReplicationMethodNotSet));
  }

  @Test
  void testWithReplicationMethodWithReplicationSlotWithWrongType() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config.get("replication_method")).put("replication_slot", 10);

    assertFalse(validator.test(schema, config));
  }

  @Test
  void testWithReplicationMethodWithReplicationSlotWithNull() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config.get("replication_method")).set("replication_slot", null);

    assertFalse(validator.test(schema, config));
  }

  @Test
  void testJdbcUrlAndConfigNoExtraParams() {
    final JsonNode jdbcConfig = new PostgresSource().toDatabaseConfigStatic(buildConfigNoJdbcParameters());
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testJdbcUrlEmptyExtraParams() {
    final JsonNode jdbcConfig = new PostgresSource().toDatabaseConfigStatic(buildConfigWithExtraJdbcParameters(""));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testJdbcUrlExtraParams() {
    final String extraParam = "key1=value1&key2=value2&key3=value3";
    final JsonNode jdbcConfig = new PostgresSource().toDatabaseConfigStatic(buildConfigWithExtraJdbcParameters(extraParam));
    assertEquals(EXPECTED_JDBC_URL, jdbcConfig.get("jdbc_url").asText());
  }

  @Test
  void testDefaultParamsNoSSL() {
    final Map<String, String> defaultProperties = new PostgresSource().getDefaultConnectionProperties(
            Jsons.jsonNode(buildConfigNoExtraJdbcParametersWithoutSsl()));
    assertEquals(new HashMap<>(), defaultProperties);
  }

  @Test
  void testDefaultParamsWithSSL() {
    final Map<String, String> defaultProperties = new PostgresSource().getDefaultConnectionProperties(
            Jsons.jsonNode(buildConfigNoJdbcParameters()));
    assertEquals(PostgresSource.SSL_JDBC_PARAMETERS, defaultProperties);
  }

}
