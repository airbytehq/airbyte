/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.nio.file.Path;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// This migration does the following:
// 1. Merge StandardSyncSchedule into StandardSync.
// 2. Remove StandardSyncSchedule.
public class MigrationV0_24_0 extends BaseMigration implements Migration {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationV0_24_0.class);

  protected static final ResourceId STANDARD_SYNC_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");
  protected static final ResourceId STANDARD_SYNC_SCHEDULE_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC_SCHEDULE");

  private static final String MIGRATION_VERSION = "0.24.0-alpha";
  private static final Path CONFIG_PATH = Path.of("migrations/migrationV0_24_0");

  private final Migration previousMigration;

  public MigrationV0_24_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(
        previousMigration.getOutputSchema());
    outputSchema.remove(STANDARD_SYNC_SCHEDULE_RESOURCE_ID);
    outputSchema.put(
        STANDARD_SYNC_RESOURCE_ID,
        MigrationUtils.getSchemaFromResourcePath(CONFIG_PATH, STANDARD_SYNC_RESOURCE_ID));
    return outputSchema;
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData,
                      Map<ResourceId, Consumer<JsonNode>> outputData) {
    // Create a map from connection id to standard sync schedule nodes
    // to "join" the schedule onto the standard sync node later.
    final Map<String, JsonNode> connectionToScheduleNodes = inputData
        .get(STANDARD_SYNC_SCHEDULE_RESOURCE_ID)
        .collect(Collectors.toMap(r -> r.get("connectionId").asText(), r -> r));

    for (final Map.Entry<ResourceId, Stream<JsonNode>> inputEntry : inputData.entrySet()) {
      // Skip standard sync schedule.
      if (inputEntry.getKey().equals(STANDARD_SYNC_SCHEDULE_RESOURCE_ID)) {
        continue;
      }

      inputEntry.getValue().forEach(jsonNode -> {
        if (inputEntry.getKey().equals(STANDARD_SYNC_RESOURCE_ID)) {
          // "Join" the standard sync schedule node onto the standard sync.
          final String connectionId = jsonNode.get("connectionId").asText();
          final ObjectNode standardSync = (ObjectNode) jsonNode;
          final ObjectNode syncSchedule = (ObjectNode) connectionToScheduleNodes.get(connectionId);
          if (syncSchedule == null) {
            LOGGER.warn(
                "No standard sync schedule config exists for connection {}, will default to manual sync",
                connectionId);
            standardSync.set("manual", Jsons.jsonNode(true));
            return;
          }

          final JsonNode manual = syncSchedule.get("manual");
          standardSync.set("manual", manual);

          final JsonNode schedule = syncSchedule.get("schedule");
          if (schedule != null && !manual.asBoolean()) {
            standardSync.set("schedule", schedule);
          }

          LOGGER.info(
              "Schedule added to standard sync config for connection {} (manual: {}, schedule: {})",
              connectionId, manual, schedule);
        }

        final Consumer<JsonNode> outputConsumer = outputData.get(inputEntry.getKey());
        outputConsumer.accept(jsonNode);
      });
    }
  }

}
