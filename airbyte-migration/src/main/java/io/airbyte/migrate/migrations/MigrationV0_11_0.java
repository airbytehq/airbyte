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

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.CaseFormat;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.JsonSchemas;
import io.airbyte.migrate.Migration;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

public class MigrationV0_11_0 implements Migration {

  @Override
  public String getVersion() {
    return "v0.11.0-alpha";
  }

  @Override
  public Map<String, JsonNode> getInputSchema() {
    final Map<String, JsonNode> schemas = new HashMap<>();

    // add config schemas.
    schemas.putAll(getNameToSchemasFromPath(Path.of("migrations/migrationV0_11_0/config")));
    // add db schemas.
    schemas.putAll(getNameToSchemasFromPath(Path.of("migrations/migrationV0_11_0/jobs")));

    return schemas;
  }

  private Map<String, JsonNode> getNameToSchemasFromPath(Path path) {
    final Map<String, JsonNode> schemas = new HashMap<>();

    final Path pathToSchemas = JsonSchemas.prepareSchemas(path.toString(), MigrationV0_11_0.class);
    IOs.listFiles(pathToSchemas)
        .stream()
        .map(f -> JsonSchemaValidator.getSchema(f.toFile()))
        .forEach(j -> schemas.put(CaseFormat.UPPER_CAMEL.to(CaseFormat.UPPER_UNDERSCORE, j.get("title").asText()), j));

    return schemas;
  }

  @Override
  public Map<String, JsonNode> getOutputSchema() {
    return getInputSchema();
  }

  // no op migration.
  @Override
  public void migrate(Map<String, Stream<JsonNode>> inputData, Map<String, Consumer<JsonNode>> outputData) {
    for (Map.Entry<String, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(recordConsumer);
    }
  }

}
