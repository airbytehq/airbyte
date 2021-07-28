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
import com.google.common.collect.ImmutableSet;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.function.Consumer;
import java.util.function.Supplier;
import java.util.stream.Stream;

/**
 * Migrates 2 concepts:
 * <ul>
 * <li>Deprecates the default workspace id. It finds all instances of it and sets it to a new
 * randomly generated id.</li>
 * <li>Makes namespaceDefinition required in StandardSync. If it is not set, defaults to
 * destination.</li>
 * </ul>
 */
public class MigrationV0_29_0 extends BaseMigration implements Migration {

  private static final UUID DEFAULT_WORKSPACE_ID = UUID.fromString("5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6");
  private static final String MIGRATION_VERSION = "0.29.0-alpha";

  private static final ResourceId WORKSPACE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_WORKSPACE");
  private static final ResourceId SOURCE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "SOURCE_CONNECTION");
  private static final ResourceId DESTINATION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "DESTINATION_CONNECTION");
  private static final ResourceId OPERATION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC_OPERATION");
  private static final ImmutableSet<ResourceId> RESOURCE_WITH_WORKSPACE_ID = ImmutableSet.of(
      WORKSPACE_RESOURCE_ID,
      SOURCE_RESOURCE_ID,
      DESTINATION_RESOURCE_ID,
      OPERATION_RESOURCE_ID);

  private static final ResourceId CONNECTION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");
  private static Set<String> NAMESPACE_DEFINITIONS = ImmutableSet.of("source", "destination", "customformat");

  private final Migration previousMigration;
  private final Supplier<UUID> uuidSupplier;

  public MigrationV0_29_0(Migration previousMigration) {
    this(previousMigration, UUID::randomUUID);
  }

  public MigrationV0_29_0(Migration previousMigration, Supplier<UUID> uuidSupplier) {
    super(previousMigration);
    this.previousMigration = previousMigration;
    this.uuidSupplier = uuidSupplier;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return previousMigration.getOutputSchema();
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData,
                      Map<ResourceId, Consumer<JsonNode>> outputData) {
    final UUID newWorkspaceId = uuidSupplier.get();

    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());
      entry.getValue().forEach(r -> {
        // if standard sync make sure namespaceDefinition is set. it is now a required property. default to
        // destination.
        if (entry.getKey().equals(CONNECTION_RESOURCE_ID)) {
          if (!r.hasNonNull("namespaceDefinition") || !NAMESPACE_DEFINITIONS.contains(r.get("namespaceDefinition").asText())) {
            ((ObjectNode) r).put("namespaceDefinition", "destination");
          }
        }

        // if the resource contains a workspace id. figure out if it is the default one and switch it.
        if (RESOURCE_WITH_WORKSPACE_ID.contains(entry.getKey())) {
          final UUID workspaceId = UUID.fromString(r.get("workspaceId").asText());
          if (workspaceId.equals(DEFAULT_WORKSPACE_ID)) {
            ((ObjectNode) r).put("workspaceId", newWorkspaceId.toString());
          }
        }
        recordConsumer.accept(r);
      });
    }
  }

}
