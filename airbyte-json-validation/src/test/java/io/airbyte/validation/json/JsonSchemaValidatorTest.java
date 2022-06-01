/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.validation.json;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import org.junit.jupiter.api.Test;

class JsonSchemaValidatorTest {

  private static final JsonNode VALID_SCHEMA = Jsons.deserialize(
      """
      {
          "$schema": "http://json-schema.org/draft-07/schema#",
          "title": "test",
          "type": "object",
          "required": ["host"],
          "additionalProperties": false,
          "properties": {
            "host": {
              "type": "string"
            },
            "port": {
              "type": "integer",
              "minimum": 0,
              "maximum": 65536
            }    }
        }""");

  @Test
  void testISO8601DateTime() {
    final JsonNode schema = Jsons.deserialize(
        """
        {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
              "host": {
                "type": "string",
                "format": "date-time"
              }
            }
          }""");

    final JsonSchemaValidator validator = new JsonSchemaValidator();
    assertFalse(validator.test(schema, Jsons.deserialize("{ \"host\": \"2022-05-16 19:13:09.369000\" }")));
    assertTrue(validator.test(schema, Jsons.deserialize("{ \"host\": \"2022-05-16T19:13:09.369000\" }")));
  }

  @Test
  void testValidateSuccess() {
    final JsonSchemaValidator validator = new JsonSchemaValidator();

    final JsonNode object1 = Jsons.deserialize("{\"host\":\"abc\"}");
    assertTrue(validator.validate(VALID_SCHEMA, object1).isEmpty());
    assertDoesNotThrow(() -> validator.ensure(VALID_SCHEMA, object1));

    final JsonNode object2 = Jsons.deserialize("{\"host\":\"abc\", \"port\":1}");
    assertTrue(validator.validate(VALID_SCHEMA, object2).isEmpty());
    assertDoesNotThrow(() -> validator.ensure(VALID_SCHEMA, object2));
  }

  @Test
  void testValidateFail() {
    final JsonSchemaValidator validator = new JsonSchemaValidator();

    final JsonNode object1 = Jsons.deserialize("{}");
    assertFalse(validator.validate(VALID_SCHEMA, object1).isEmpty());
    assertThrows(JsonValidationException.class, () -> validator.ensure(VALID_SCHEMA, object1));

    final JsonNode object2 = Jsons.deserialize("{\"host\":\"abc\", \"port\":9999999}");
    assertFalse(validator.validate(VALID_SCHEMA, object2).isEmpty());
    assertThrows(JsonValidationException.class, () -> validator.ensure(VALID_SCHEMA, object2));
  }

  @Test
  void test() throws IOException {
    final String schema = """
                          {
                            "$schema": "http://json-schema.org/draft-07/schema#",
                            "title": "OuterObject",
                            "type": "object",
                            "properties": {
                              "field1": {
                                "type": "string"
                              }
                            },
                            "definitions": {
                              "InnerObject": {
                                "type": "object",
                                "properties": {
                                  "field2": {
                                    "type": "string"
                                  }
                                }
                              }
                            }
                          }
                          """;

    final File schemaFile = IOs.writeFile(Files.createTempDirectory("test"), "schema.json", schema).toFile();

    // outer object
    assertTrue(JsonSchemaValidator.getSchema(schemaFile).get("properties").has("field1"));
    assertFalse(JsonSchemaValidator.getSchema(schemaFile).get("properties").has("field2"));
    // inner object
    assertTrue(JsonSchemaValidator.getSchema(schemaFile, "InnerObject").get("properties").has("field2"));
    assertFalse(JsonSchemaValidator.getSchema(schemaFile, "InnerObject").get("properties").has("field1"));
    // non-existent object
    assertNull(JsonSchemaValidator.getSchema(schemaFile, "NonExistentObject"));
  }

}
