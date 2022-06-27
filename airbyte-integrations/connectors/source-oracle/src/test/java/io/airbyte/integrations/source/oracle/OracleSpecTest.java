/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.oracle;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;

/**
 * Tests that the Oracle spec passes JsonSchema validation. While this may seem like overkill, we
 * are doing it because there are some gotchas in correctly configuring the oneOf.
 */
public class OracleSpecTest {

  private static final String CONFIGURATION = """
                                              {
                                                "host": "localhost",
                                                "port": 1521,
                                                "sid": "ora_db",
                                                "username": "ora",
                                                "password": "pwd",
                                                "schemas": [
                                                  "public"
                                                ],
                                                "jdbc_url_params": "property1=pValue1&property2=pValue2"
                                              }
                                              """;

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
  void testHostMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("host");
    assertFalse(validator.test(schema, config));
  }

  @Test
  void testPortMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("port");
    assertFalse(validator.test(schema, config));
  }

  @Test
  void testSsidMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("sid");
    assertFalse(validator.test(schema, config));
  }

  @Test
  void testUsernameMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("username");
    assertFalse(validator.test(schema, config));
  }

  @Test
  void testPasswordMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("password");
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testSchemaMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("schemas");
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testAdditionalJdbcParamMissing() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    ((ObjectNode) config).remove("jdbc_url_params");
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testWithJdbcAdditionalProperty() {
    final JsonNode config = Jsons.deserialize(CONFIGURATION);
    assertTrue(validator.test(schema, config));
  }

  @Test
  void testJdbcAdditionalProperty() throws Exception {
    final ConnectorSpecification spec = new OracleSource().spec();
    assertNotNull(spec.getConnectionSpecification().get("properties").get("jdbc_url_params"));
  }

}
