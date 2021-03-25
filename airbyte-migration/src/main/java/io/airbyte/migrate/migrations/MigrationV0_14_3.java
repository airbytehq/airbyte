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
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Maps;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;

/**
 * This migration fixes a mistake. We should have done a minor version bump from 0.14.2 => 0.14.3
 * but we did not. This migration cleans up any problems that might have arisen from that. Then we
 * will do another migration to 0.15 forcing everyone to migrate (guaranteeing they hit this one)
 * and getting into a good state. The only change here is that instead of using StandardDataSchema
 * in the API, we now use ConfiguredCatalog.
 */
public class MigrationV0_14_3 extends BaseMigration implements Migration {

  private static final ResourceId STANDARD_SYNC_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");

  public MigrationV0_14_3(MigrationV0_14_0 previousMigration) {
    super(previousMigration);
  }

  @Override
  public String getVersion() {
    return "0.14.3-alpha";
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(new MigrationV0_14_0().getOutputSchema());

    try {
      outputSchema.put(STANDARD_SYNC_RESOURCE_ID,
          Jsons.jsonNode(MoreResources.readResource("migrations/migrationV0_14_0/airbyte_config/StandardSync.yaml")));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    return outputSchema;
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

      entry.getValue().forEach(r -> {
        // replace schema object with a catalog object.
        if (entry.getKey().equals(STANDARD_SYNC_RESOURCE_ID)) {
          final JsonNode schema = ((ObjectNode) r).remove("schema");
          ((ObjectNode) r).set("catalog", toConfiguredCatalog(schema));
        }

        recordConsumer.accept(r);
      });
    }
  }

  private static JsonNode toConfiguredCatalog(JsonNode schema) {
    final List<Map<String, JsonNode>> configuredStreams = MoreIterators.toList(schema.get("streams").elements())
        .stream()
        .map(stream -> {
          final List<String> supportedSyncModes = MoreIterators.toList(stream.get("supportedSyncModes").iterator())
              .stream()
              // sync mode enum is identical in Schema and ConfiguredCatalog.
              .map(JsonNode::asText)
              .collect(Collectors.toList());
          // catalog fields
          final Map<String, JsonNode> airbyteStream = Maps.newHashMap();
          airbyteStream.put("name", stream.get("name"));
          airbyteStream.put("supported_sync_modes", Jsons.jsonNode(supportedSyncModes));
          airbyteStream.put("json_schema", fieldsToJsonSchema(stream.get("fields")));
          airbyteStream.put("source_defined_cursor", stream.get("sourceDefinedCursor"));
          airbyteStream.put("default_cursor_field", stream.get("defaultCursorField"));
          // configured catalog fields
          final Map<String, JsonNode> catalog = Maps.newHashMap();
          catalog.put("stream", Jsons.jsonNode(airbyteStream));
          catalog.put("sync_mode", Jsons.jsonNode(stream.get("syncMode").asText()));
          catalog.put("cursor_field", stream.get("cursorField"));
          return catalog;
        })
        .collect(Collectors.toList());

    return Jsons.jsonNode(ImmutableMap.of("streams", configuredStreams));
  }

  private static JsonNode fieldsToJsonSchema(JsonNode fields) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("type", "object")
        .put("properties", MoreIterators.toList(fields.elements())
            .stream()
            .collect(Collectors.toMap(
                field -> field.get("name").asText(),
                // data type enum is identical in Schema and ConfiguredCatalog.
                field -> ImmutableMap.of("type", field.get("dataType").asText()))))
        .build());
  }

}
