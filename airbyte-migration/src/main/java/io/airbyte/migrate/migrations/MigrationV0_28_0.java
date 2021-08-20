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
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.stream.Stream;

public class MigrationV0_28_0 extends BaseMigration implements Migration {

  private static final UUID DEFAULT_WORKSPACE_ID = UUID.fromString("5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6");

  private static final Path RESOURCE_PATH = Path.of("migrations/migrationV0_28_0/airbyte_config");
  private static final String MIGRATION_VERSION = "0.28.0-alpha";

  private static final ResourceId CONNECTION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");
  private static final ResourceId SOURCE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "SOURCE_CONNECTION");
  private static final ResourceId OPERATION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC_OPERATION");

  private final Migration previousMigration;

  public MigrationV0_28_0(final Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(previousMigration.getOutputSchema());
    outputSchema.put(OPERATION_RESOURCE_ID, MigrationUtils.getSchemaFromResourcePath(RESOURCE_PATH, OPERATION_RESOURCE_ID));
    return outputSchema;
  }

  @Override
  public void migrate(final Map<ResourceId, Stream<JsonNode>> inputDataImmutable,
                      final Map<ResourceId, Consumer<JsonNode>> outputData) {
    // we need to figure out which workspace to associate an operation with. we use the following
    // strategy to avoid ever storing too much info in memory:
    // 1. iterate over connectors stream
    // 2. build mapping of connections to source
    // 3. build mapping of operation ids to connections
    // 4. iterate over sources stream
    // 5. build mapping of sources to workspaces
    // 6. iterate over operations stream,
    // 7. map from operation => connection => source => workspace. set that workspace for the operation.
    // 8. if no mapping use default workspace id

    final Map<UUID, UUID> connectionIdToSourceId = new HashMap<>();
    final Map<UUID, UUID> operationIdToConnectionId = new HashMap<>();
    final Map<UUID, UUID> sourceIdToWorkspaceId = new HashMap<>();

    final Map<ResourceId, Stream<JsonNode>> inputData = new HashMap<>(inputDataImmutable);
    // process connections.
    inputData.getOrDefault(CONNECTION_RESOURCE_ID, Stream.empty()).forEach(r -> {
      final UUID connectionId = UUID.fromString(r.get("connectionId").asText());
      final UUID sourceId = UUID.fromString(r.get("sourceId").asText());
      connectionIdToSourceId.put(connectionId, sourceId);
      if (r.hasNonNull("operationIds")) {
        r.get("operationIds").forEach(operationIdString -> {
          final UUID operationId = UUID.fromString(operationIdString.asText());
          operationIdToConnectionId.put(operationId, connectionId);
        });
      }

      outputData.get(CONNECTION_RESOURCE_ID).accept(r);
    });
    inputData.remove(CONNECTION_RESOURCE_ID);

    // process sources.
    inputData.getOrDefault(SOURCE_RESOURCE_ID, Stream.empty()).forEach(r -> {
      final UUID sourceId = UUID.fromString(r.get("sourceId").asText());
      final UUID workspaceId = UUID.fromString(r.get("workspaceId").asText());
      sourceIdToWorkspaceId.put(sourceId, workspaceId);

      outputData.get(SOURCE_RESOURCE_ID).accept(r);
    });
    inputData.remove(SOURCE_RESOURCE_ID);

    // process operations.
    inputData.getOrDefault(OPERATION_RESOURCE_ID, Stream.empty()).forEach(r -> {
      final UUID operationId = UUID.fromString(r.get("operationId").asText());

      final UUID workspaceId;
      final UUID connectionId = operationIdToConnectionId.get(operationId);
      if (connectionId == null) {
        workspaceId = DEFAULT_WORKSPACE_ID;
      } else {
        final UUID sourceId = connectionIdToSourceId.get(connectionId);
        workspaceId = sourceIdToWorkspaceId.getOrDefault(sourceId, DEFAULT_WORKSPACE_ID);
      }
      ((ObjectNode) r).put("workspaceId", workspaceId.toString());

      outputData.get(OPERATION_RESOURCE_ID).accept(r);
    });
    inputData.remove(OPERATION_RESOURCE_ID);

    // process the remaining resources.
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(recordConsumer);
    }
  }

}
