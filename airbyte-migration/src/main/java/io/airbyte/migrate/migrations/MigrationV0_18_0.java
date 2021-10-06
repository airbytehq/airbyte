/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This migration makes sure that ConfiguredAirbyteCatalog always have values for the now required
 * fields: syncMode (used by source to specify full_refresh/incremental) and destinationSyncMode
 * (used by destination to specify append/overwrite/append_dedup)
 *
 * The primaryKey column is filled if available from the stream if defined by source
 *
 * Additionally, this migration updates the JSON Schema for StandardWorkspace with a new field
 * 'tombstone' introduced in 0.17.1
 */
public class MigrationV0_18_0 extends BaseMigration implements Migration {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationV0_18_0.class);

  private static final ResourceId STANDARD_WORKSPACE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_WORKSPACE");
  private static final ResourceId STANDARD_SYNC_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");

  private static final String MIGRATION_VERSION = "0.18.0-alpha";

  private final Migration previousMigration;

  public MigrationV0_18_0(Migration previousMigration) {
    super(previousMigration);
    this.previousMigration = previousMigration;
  }

  @Override
  public String getVersion() {
    return MIGRATION_VERSION;
  }

  @Override
  public Map<ResourceId, JsonNode> getInputSchema() {
    final Map<ResourceId, JsonNode> outputSchema = new HashMap<>(previousMigration.getOutputSchema());
    outputSchema.put(
        STANDARD_WORKSPACE_RESOURCE_ID,
        MigrationUtils.getSchemaFromResourcePath(Path.of("migrations/migrationV0_18_0"), STANDARD_WORKSPACE_RESOURCE_ID));
    return outputSchema;
  }

  @Override
  public Map<ResourceId, JsonNode> getOutputSchema() {
    return getInputSchema();
  }

  @Override
  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    for (final Map.Entry<ResourceId, Stream<JsonNode>> entry : inputData.entrySet()) {
      final Consumer<JsonNode> recordConsumer = outputData.get(entry.getKey());

      entry.getValue().forEach(r -> {
        if (entry.getKey().equals(STANDARD_SYNC_RESOURCE_ID)) {
          ((ObjectNode) r).set("catalog", migrateCatalog(r.get("catalog")));
        }
        recordConsumer.accept(r);
      });
    }
  }

  private JsonNode migrateCatalog(JsonNode catalog) {
    final List<Map<String, JsonNode>> configuredStreams = MoreIterators.toList(catalog.get("streams").elements())
        .stream()
        .map(stream -> {
          final JsonNode airbyteStream = stream.get("stream");
          assert airbyteStream != null;
          JsonNode syncMode = stream.get("sync_mode");
          if (syncMode == null) {
            syncMode = Jsons.jsonNode(SyncMode.FULL_REFRESH.toString());
            LOGGER.info("Migrating {} to default source sync_mode: {}", airbyteStream.get("name"), syncMode);
          }
          JsonNode destinationSyncMode = stream.get("destination_sync_mode");
          if (destinationSyncMode == null) {
            if (SyncMode.fromValue(syncMode.asText()) == SyncMode.FULL_REFRESH) {
              destinationSyncMode = Jsons.jsonNode(DestinationSyncMode.OVERWRITE.toString());
              LOGGER.debug("Migrating {} to source sync_mode: {} destination_sync_mode: {}", airbyteStream.get("name"), syncMode,
                  destinationSyncMode);
            } else if (SyncMode.fromValue(syncMode.asText()) == SyncMode.INCREMENTAL) {
              destinationSyncMode = Jsons.jsonNode(DestinationSyncMode.APPEND.toString());
              LOGGER.debug("Migrating {} to source sync_mode: {} destination_sync_mode: {}", airbyteStream.get("name"), syncMode,
                  destinationSyncMode);
            } else {
              syncMode = Jsons.jsonNode(SyncMode.FULL_REFRESH.toString());
              destinationSyncMode = Jsons.jsonNode(DestinationSyncMode.OVERWRITE.toString());
              LOGGER.info("Migrating {} to default source sync_mode: {} destination_sync_mode: {}", airbyteStream.get("name"), syncMode,
                  destinationSyncMode);
            }
          }
          JsonNode primaryKey = stream.get("primary_key");
          if (primaryKey == null) {
            JsonNode sourceDefinedPrimaryKey = airbyteStream.get("source_defined_primary_key");
            primaryKey = sourceDefinedPrimaryKey != null ? sourceDefinedPrimaryKey : Jsons.jsonNode(Collections.emptyList());
          }
          // configured catalog fields
          return (Map<String, JsonNode>) ImmutableMap.<String, JsonNode>builder()
              .put("stream", airbyteStream)
              .put("sync_mode", syncMode)
              .put("cursor_field", stream.get("cursor_field") != null ? stream.get("cursor_field") : Jsons.jsonNode(Collections.emptyList()))
              .put("destination_sync_mode", destinationSyncMode)
              .put("primary_key", primaryKey)
              .build();
        })
        .collect(Collectors.toList());
    return Jsons.jsonNode(ImmutableMap.of("streams", configuredStreams));
  }

  public enum SyncMode {

    FULL_REFRESH("full_refresh"),

    INCREMENTAL("incremental");

    private String value;

    SyncMode(String value) {
      this.value = value;
    }

    public String toString() {
      return String.valueOf(value);
    }

    public static SyncMode fromValue(String value) {
      for (SyncMode b : SyncMode.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }

  }

  public enum DestinationSyncMode {

    APPEND("append"),
    OVERWRITE("overwrite"),
    APPEND_DEDUP("append_dedup");

    private final String value;

    private DestinationSyncMode(String value) {
      this.value = value;
    }

    public String toString() {
      return String.valueOf(value);
    }

    public static DestinationSyncMode fromValue(String value) {
      for (DestinationSyncMode b : DestinationSyncMode.values()) {
        if (b.value.equals(value)) {
          return b;
        }
      }
      throw new IllegalArgumentException("Unexpected value '" + value + "'");
    }

  }

}
