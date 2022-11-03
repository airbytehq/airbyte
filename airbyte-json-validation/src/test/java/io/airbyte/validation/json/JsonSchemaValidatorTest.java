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

  private static final String PROPERTIES = "properties";

  private static final JsonNode VALID_SCHEMA = Jsons.deserialize(
      "{\n" +
          "    \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n" +
          "    \"title\": \"test\",\n" +
          "    \"type\": \"object\",\n" +
          "    \"required\": [\"host\"],\n" +
          "    \"additionalProperties\": false,\n" +
          "    \"properties\": {\n" +
          "      \"host\": {\n" +
          "        \"type\": \"string\"\n" +
          "      },\n" +
          "      \"port\": {\n" +
          "        \"type\": \"integer\",\n" +
          "        \"minimum\": 0,\n" +
          "        \"maximum\": 65536\n" +
          "      }" +
          "    }\n" +
          "  }");

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
    final String schema = "{\n"
        + "  \"$schema\": \"http://json-schema.org/draft-07/schema#\",\n"
        + "  \"title\": \"OuterObject\",\n"
        + "  \"type\": \"object\",\n"
        + "  \"properties\": {\n"
        + "    \"field1\": {\n"
        + "      \"type\": \"string\"\n"
        + "    }\n"
        + "  },\n"
        + "  \"definitions\": {\n"
        + "    \"InnerObject\": {\n"
        + "      \"type\": \"object\",\n"
        + "      \"properties\": {\n"
        + "        \"field2\": {\n"
        + "          \"type\": \"string\"\n"
        + "        }\n"
        + "      }\n"
        + "    }\n"
        + "  }\n"
        + "}\n";

    final File schemaFile = IOs.writeFile(Files.createTempDirectory("test"), "schema.json", schema).toFile();

    // outer object
    assertTrue(JsonSchemaValidator.getSchema(schemaFile).get(PROPERTIES).has("field1"));
    assertFalse(JsonSchemaValidator.getSchema(schemaFile).get(PROPERTIES).has("field2"));
    // inner object
    assertTrue(JsonSchemaValidator.getSchema(schemaFile, "InnerObject").get(PROPERTIES).has("field2"));
    assertFalse(JsonSchemaValidator.getSchema(schemaFile, "InnerObject").get(PROPERTIES).has("field1"));
    // non-existent object
    assertNull(JsonSchemaValidator.getSchema(schemaFile, "NonExistentObject"));
  }

}
