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

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.migrate.migrations.MigrationV0_14_0;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

/**
 * This migration is for use in testing. It adds foo field to DestinationConnection and populates it
 * with bar.
 */
public class MigrationV0_14_1 implements Migration {

  private static final Path RESOURCE_PATH = Path.of("migrations/migrationV0_14_1");
  private static final ResourceId STANDARD_SOURCE_DEFINITION_RESOURCE_ID =
      ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SOURCE_DEFINITION");
  private static final ResourceId JOB_METADATA_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.JOB, "JOB");

  private final Map<ResourceId, JsonNode> inputSchema;
  private final Map<ResourceId, JsonNode> outputSchema;

  public MigrationV0_14_1() {
    inputSchema = new MigrationV0_14_0().getOutputSchema();
    outputSchema = new HashMap<>(inputSchema);
    final JsonNode standardSourceDefinitionSchema = Yamls.deserialize(Exceptions
        .toRuntime(() -> MoreResources
            .readResource(RESOURCE_PATH.resolve(ResourceType.CONFIG.getDirectoryName()).resolve("StandardSourceDefinition.yaml").toString())));
    final JsonNode jobSchema = Yamls.deserialize(Exceptions
        .toRuntime(
            () -> MoreResources.readResource(RESOURCE_PATH.resolve(ResourceType.JOB.getDirectoryName()).resolve("Jobs.yaml").toString())));
    outputSchema.put(STANDARD_SOURCE_DEFINITION_RESOURCE_ID, standardSourceDefinitionSchema);
    outputSchema.put(JOB_METADATA_RESOURCE_ID, jobSchema);
  }

  @Override
  public String getVersion() {
    return "v0.14.1-alpha";
  }

  @Override
  public Map<ResourceId, JsonNode> getInputSchema() {
    return inputSchema;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return outputSchema;
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

      entry.getValue().forEach(r -> {
        if (entry.getKey().equals(STANDARD_SOURCE_DEFINITION_RESOURCE_ID) || entry.getKey().equals(JOB_METADATA_RESOURCE_ID)) {
          ((ObjectNode) r).put("foo", "bar");
        }

        recordConsumer.accept(r);
      });
    }
  }

}
