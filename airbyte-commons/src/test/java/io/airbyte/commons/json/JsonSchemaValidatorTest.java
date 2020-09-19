/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.commons.json;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
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

}
