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

package io.airbyte.integrations.source.cockroachdb;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
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
public class CockroachDbSpecTest {

  private static final String CONFIGURATION = "{  "
      + "\"password\" : \"pwd\",  "
      + "\"username\" : \"postgres\",  "
      + "\"database\" : \"postgres_db\",  "
      + "\"port\" : 5432,  "
      + "\"host\" : \"localhost\",  "
      + "\"ssl\" : true }";

  private static JsonNode schema;
  private static JsonSchemaValidator validator;

  @BeforeAll
  static void init() throws IOException {
    final String spec = MoreResources.readResource("spec.json");
    final File schemaFile = IOs
        .writeFile(Files.createTempDirectory(Path.of("/tmp"), "pg-spec-test"), "schema.json", spec)
        .toFile();
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

}
