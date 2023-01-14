/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

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
      + "\"jdbc_url_params\" : \"property1=pValue1&property2=pValue2\",  "
      + "\"ssl\" : true, "
      + "\"replication_method\" : {    \"method\" : \"CDC\", \"replication_slot\" : \"ab_slot\", \"publication\" : \"ab_publication\"  }"
      + "}";
  private static JsonNode schema;
  private static JsonSchemaValidator validator;

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
    ((ObjectNode) config).remove(JdbcUtils.DATABASE_KEY);
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
  void testWithJdbcAdditionalProperty() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testJdbcAdditionalProperty() throws Exception {
    final ConnectorSpecification spec = new PostgresSource().spec();
    assertNotNull(spec.getConnectionSpecification().get("properties").get(JdbcUtils.JDBC_URL_PARAMS_KEY));
  }

}
