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

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Stream;

public class MigrationV0_26_0 extends BaseMigration implements Migration {

  protected static final ResourceId DESTINATION_CONNECTION_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "DESTINATION_CONNECTION");
  protected static final ResourceId STANDARD_SYNC_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");
  protected static final ResourceId STANDARD_SYNC_OPERATION_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC_OPERATION");

  private static final String MIGRATION_VERSION = "0.26.0-alpha";
  @VisibleForTesting
  protected final Migration previousMigration;

  public MigrationV0_26_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  private static final Path RESOURCE_PATH = Path.of("migrations/migrationV0_26_0/airbyte-config");

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    JsonNode schemaFromResourcePath = MigrationUtils.getSchemaFromResourcePath(RESOURCE_PATH, STANDARD_SYNC_OPERATION_RESOURCE_ID);

    HashMap<ResourceId, JsonNode> resourceIdJsonNodeHashMap = new HashMap<>(previousMigration.getOutputSchema());
    resourceIdJsonNodeHashMap.put(STANDARD_SYNC_OPERATION_RESOURCE_ID, schemaFromResourcePath);

    return resourceIdJsonNodeHashMap;
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData,
                      Map<ResourceId, Consumer<JsonNode>> outputData) {

    Set<String> destinationIds = new HashSet<>();

    inputData.getOrDefault(DESTINATION_CONNECTION_RESOURCE_ID, Stream.empty())
        .forEach(destinationConnection -> {
          JsonNode configuration = destinationConnection.get("configuration");
          if (configuration.get("basic_normalization") != null) {
            boolean basicNormalization = ((ObjectNode) configuration).remove("basic_normalization")
                .asBoolean();
            ((ObjectNode) destinationConnection).set("configuration", configuration);
            if (basicNormalization) {
              destinationIds.add(destinationConnection.get("destinationId").asText());
            }
          }

          final Consumer<JsonNode> destinationConnectionConsumer = outputData
              .get(DESTINATION_CONNECTION_RESOURCE_ID);
          if (destinationConnectionConsumer == null) {
            throw new RuntimeException("Could not find consumer for DESTINATION_CONNECTION");
          }
          destinationConnectionConsumer.accept(destinationConnection);
        });

    for (final Map.Entry<ResourceId, Stream<JsonNode>> inputEntry : inputData.entrySet()) {
      if (inputEntry.getKey().equals(DESTINATION_CONNECTION_RESOURCE_ID)) {
        continue;
      }

      inputEntry.getValue().forEach(jsonNode -> {
        if (inputEntry.getKey().equals(STANDARD_SYNC_RESOURCE_ID) && destinationIds
            .contains(jsonNode.get("destinationId").asText())) {
          Map<String, Object> standardSyncOperation = new LinkedHashMap<>();
          String operationId = uuid();
          standardSyncOperation.put("operationId", operationId);
          standardSyncOperation.put("name", "default-normalization");
          standardSyncOperation.put("operatorType", "normalization");
          standardSyncOperation
              .put("operatorNormalization", Jsons.jsonNode(ImmutableMap.of("option", "basic")));
          standardSyncOperation
              .put("tombstone", false);
          JsonNode standardSyncOperationAsJson = Jsons.jsonNode(standardSyncOperation);
          outputData.get(STANDARD_SYNC_OPERATION_RESOURCE_ID).accept(standardSyncOperationAsJson);
          if (jsonNode.get("operationIds") == null) {
            ((ObjectNode) jsonNode).put("operationIds", Jsons.jsonNode(Collections.singletonList(operationId)));
          } else {
            List<String> operationIds = Jsons
                .object(jsonNode.get("operationIds"), new TypeReference<List<String>>() {});
            operationIds.add(operationId);
            ((ObjectNode) jsonNode).set("operationIds", Jsons.jsonNode(operationIds));
          }
        }
        final Consumer<JsonNode> outputConsumer = outputData.get(inputEntry.getKey());
        outputConsumer.accept(jsonNode);
      });
    }
  }

  @VisibleForTesting
  protected String uuid() {
    return UUID.randomUUID().toString();
  }

}
