/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.functional.Consumers;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.stream.Stream;

/**
 * Additionally there are some migration metadata fields that are important to fill in on each
 * migration. Instead of leaving this up to the person writing the migration, this class handles it
 * for them. It writes a record saying when the migration happens. It also updates the version in
 * the AIRBYTE_METADATA table.
 */
public class MigrateWithMetadata {

  private final Migration migration;

  public MigrateWithMetadata(Migration migration) {
    this.migration = migration;
  }

  public void migrate(Map<ResourceId, Stream<JsonNode>> inputData, Map<ResourceId, Consumer<JsonNode>> outputData) {
    final String version = migration.getVersion();
    final Map<ResourceId, Consumer<JsonNode>> decoratedOutputData = decorateAirbyteMetadataConsumerWithVersionBump(outputData, version);
    migration.migrate(inputData, decoratedOutputData);

    MigrationUtils.registerMigrationRecord(outputData, MigrationConstants.AIRBYTE_METADATA, version);
  }

  /**
   * We inject a mapper in front of the original metadata consumer. This mapper, when it finds the
   * airbyte version record, bumps it to the correct version.
   *
   * @param consumerMap Map of resource ids to output consumer.
   * @return Map of resource ids to output consumer. The AirbyteMetadata consumer will be altered to
   *         bump the version.
   */
  private static Map<ResourceId, Consumer<JsonNode>> decorateAirbyteMetadataConsumerWithVersionBump(Map<ResourceId, Consumer<JsonNode>> consumerMap,
                                                                                                    String version) {
    final HashMap<ResourceId, Consumer<JsonNode>> resourceIdConsumerHashMap = new HashMap<>(consumerMap);
    final ResourceId metadataResourceId = ResourceId.fromConstantCase(ResourceType.JOB, MigrationConstants.AIRBYTE_METADATA);

    resourceIdConsumerHashMap.put(metadataResourceId, Consumers.wrapConsumer(
        (json) -> {
          bumpVersionOnAirbyteMetadata(json, version);
          return json;
        },
        resourceIdConsumerHashMap.get(metadataResourceId)));

    return resourceIdConsumerHashMap;
  }

  // warning: mutates in place.
  private static void bumpVersionOnAirbyteMetadata(JsonNode input, String version) {
    if (input.get("key").asText().equals("airbyte_version")) {
      ((ObjectNode) input).put("value", version);
    }
  }

}
