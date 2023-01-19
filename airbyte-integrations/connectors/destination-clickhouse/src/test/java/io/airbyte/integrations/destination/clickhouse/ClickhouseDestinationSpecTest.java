/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.protocol.models.v0.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Tests that the clickhouse spec passes JsonSchema validation. While this may seem like overkill,
 * we are doing it because there are some gotchas in correctly configuring the oneOf.
 */
public class ClickhouseDestinationSpecTest {

  private static final String CONFIGURATION = "{  "
      + "\"password\" : \"pwd\",  "
      + "\"username\" : \"clickhouse\",  "
      + "\"database\" : \"clickhouse_db\",  "
      + "\"port\" : 8123,  "
      + "\"host\" : \"localhost\",  "
      + "\"jdbc_url_params\" : \"property1=pValue1&property2=pValue2\",  "
      + "\"ssl\" : true "
      + "}";

  private static JsonNode schema;
  private static JsonSchemaValidator validator;

  @BeforeAll
  static void init() throws IOException {
    final String spec = MoreResources.readResource("spec.json");
    final File schemaFile = IOs.writeFile(Files.createTempDirectory(Path.of("/tmp"), "cl-spec-test"), "schema.json", spec).toFile();
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
  void testWithJdbcAdditionalProperty() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testJdbcAdditionalProperty() throws Exception {
    final ConnectorSpecification spec = new ClickhouseDestination().spec();
    assertNotNull(spec.getConnectionSpecification().get("properties").get(JdbcUtils.JDBC_URL_PARAMS_KEY));
  }

}
