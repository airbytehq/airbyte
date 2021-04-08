/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
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
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class JsonSchemaValidatorTest {

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

    JsonNode object1 = Jsons.deserialize("{\"host\":\"abc\"}");
    assertTrue(validator.validate(VALID_SCHEMA, object1).isEmpty());
    assertDoesNotThrow(() -> validator.ensure(VALID_SCHEMA, object1));

    JsonNode object2 = Jsons.deserialize("{\"host\":\"abc\", \"port\":1}");
    assertTrue(validator.validate(VALID_SCHEMA, object2).isEmpty());
    assertDoesNotThrow(() -> validator.ensure(VALID_SCHEMA, object2));
  }

  @Test
  void testValidateFail() {
    final JsonSchemaValidator validator = new JsonSchemaValidator();

    JsonNode object1 = Jsons.deserialize("{}");
    assertFalse(validator.validate(VALID_SCHEMA, object1).isEmpty());
    assertThrows(JsonValidationException.class, () -> validator.ensure(VALID_SCHEMA, object1));

    JsonNode object2 = Jsons.deserialize("{\"host\":\"abc\", \"port\":9999999}");
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
    assertTrue(JsonSchemaValidator.getSchema(schemaFile).get("properties").has("field1"));
    assertFalse(JsonSchemaValidator.getSchema(schemaFile).get("properties").has("field2"));
    // inner object
    assertTrue(JsonSchemaValidator.getSchema(schemaFile, "InnerObject").get("properties").has("field2"));
    assertFalse(JsonSchemaValidator.getSchema(schemaFile, "InnerObject").get("properties").has("field1"));
    // non-existent object
    assertNull(JsonSchemaValidator.getSchema(schemaFile, "NonExistentObject"));
  }

//  @Test
//  void test2() throws JsonValidationException {
//    final Path schemaPath = Path.of("/Users/charles/code/airbyte/airbyte-integrations/connectors/source-postgres/src/main/resources/spec.json");
//    final Path objectPath = Path.of("/Users/charles/code/airbyte/airbyte-integrations/connectors/source-postgres/src/main/resources/object.json");
//    final JsonNode schema = JsonSchemaValidator.getSchema(schemaPath.toFile());
//    final JsonNode object = Jsons.deserialize(IOs.readFile(objectPath));
//
//    new JsonSchemaValidator().ensure(schema, object);
//  }

  @Test
  void test3() {
    final Path schemaPath = Path.of("/Users/charles/code/airbyte/airbyte-integrations/connectors/source-postgres/src/main/resources/spec.json");
//    final Path objectPath = Path.of("/Users/charles/code/airbyte/airbyte-integrations/connectors/source-postgres/src/main/resources/object.json");
//    final String objectString = "{  \"password\" : \"**********\",  \"username\" : \"fbwiigwttroxfr\",  \"database\" : \"df2398b8h9cmec\",  \"port\" : 5432,  \"host\" : \"ec2-184-72-235-80.compute-1.amazonaws.com\",  \"replication_method\" : {    \"replication_slot\" : \"ewq\"  }}";
    final JsonNode schema = JsonSchemaValidator.getSchema(schemaPath.toFile());
//    final JsonNode object = Jsons.deserialize(objectString);

    final JsonNode connectionSpecification = schema.get("connectionSpecification");
    // missing database
    assertFalse(new JsonSchemaValidator().test(connectionSpecification, Jsons.deserialize("{  \"password\" : \"**********\",  \"username\" : \"fbwiigwttroxfr\",  \"port\" : 5432,  \"host\" : \"ec2-184-72-235-80.compute-1.amazonaws.com\",  \"replication_method\" : {    \"replication_slot\" : \"ewq\"  }}")));
    // replication_method with replication slot
    assertTrue(new JsonSchemaValidator().test(connectionSpecification, Jsons.deserialize("{  \"password\" : \"**********\",  \"username\" : \"fbwiigwttroxfr\",  \"database\" : \"df2398b8h9cmec\",  \"port\" : 5432,  \"host\" : \"ec2-184-72-235-80.compute-1.amazonaws.com\",  \"replication_method\" : {    \"replication_slot\" : \"ewq\"  }}")));
    // replication_method with empty object
    assertTrue(new JsonSchemaValidator().test(connectionSpecification, Jsons.deserialize("{  \"password\" : \"**********\",  \"username\" : \"fbwiigwttroxfr\",  \"database\" : \"df2398b8h9cmec\",  \"port\" : 5432,  \"host\" : \"ec2-184-72-235-80.compute-1.amazonaws.com\",  \"replication_method\" : {}}")));
    // replication_method not set
    assertFalse(new JsonSchemaValidator().test(connectionSpecification, Jsons.deserialize("{  \"password\" : \"**********\",  \"username\" : \"fbwiigwttroxfr\",  \"database\" : \"df2398b8h9cmec\",  \"port\" : 5432,  \"host\" : \"ec2-184-72-235-80.compute-1.amazonaws.com\"}")));
    // replication_method with replication slot set to an int
    assertFalse(new JsonSchemaValidator().test(connectionSpecification, Jsons.deserialize("{  \"password\" : \"**********\",  \"username\" : \"fbwiigwttroxfr\",  \"database\" : \"df2398b8h9cmec\",  \"port\" : 5432,  \"host\" : \"ec2-184-72-235-80.compute-1.amazonaws.com\",  \"replication_method\" : {    \"replication_slot\" : 3  }}")));
    // replication_method with replication slot set to null
    // todo (cgardens) - i would expect this to return false but it returns true.
    assertTrue(new JsonSchemaValidator().test(connectionSpecification, Jsons.deserialize("{  \"password\" : \"**********\",  \"username\" : \"fbwiigwttroxfr\",  \"database\" : \"df2398b8h9cmec\",  \"port\" : 5432,  \"host\" : \"ec2-184-72-235-80.compute-1.amazonaws.com\",  \"replication_method\" : {    \"replication_slot\" : null  }}")));
  }

}
