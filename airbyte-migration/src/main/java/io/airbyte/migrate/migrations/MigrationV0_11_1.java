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
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.enums.Enums;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.migrations.MigrationV0_11_0.ConfigKeys;
import java.nio.file.Path;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

// todo (cgardens) - this migration is just an example. i will not commit it to master.
/**
 * This migration adds foo field to DestinationConnection and populates it with bar.
 */
public class MigrationV0_11_1 implements Migration {

  private static final Path DESTINATION_CONNECTION_PATH = Path.of("config/DESTINATION_CONNECTION.yaml");

  @Override
  public String getVersion() {
    return "v0.11.1-alpha";
  }

  @Override
  public Map<ResourceId, JsonNode> getInputSchema() {
    return new MigrationV0_11_0().getOutputSchema();
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    final Map<Path, JsonNode> outputSchema = getInputSchema();
    outputSchema.putAll(
        MigrationUtils.getNameToSchemasFromPath(Path.of("migrations/migrationV0_11_1"), Path.of("config"), Enums.valuesAsStrings(ConfigKeys.class)));
    return outputSchema;
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (Map.Entry<Path, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

      entry.getValue().forEach(r -> {
        if (entry.getKey().equals(DESTINATION_CONNECTION_PATH)) {
          ((ObjectNode) r).put("foo", "bar");
        }

        recordConsumer.accept(r);
      });
    }
  }

}
