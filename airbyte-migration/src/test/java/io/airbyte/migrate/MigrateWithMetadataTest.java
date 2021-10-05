/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.migrate.migrations.NoOpMigration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.Test;

class MigrateWithMetadataTest {

  private static final String VERSION = "v10";

  private static final UUID UUID1 = UUID.randomUUID();
  private static final UUID UUID2 = UUID.randomUUID();
  private static final JsonNode STANDARD_SOURCE_DEFINITION1 = Jsons.jsonNode(ImmutableMap.builder()
      .put("sourceDefinitionId", UUID1)
      .put("name", "gold")
      .put("dockerRepository", "fort knox")
      .put("dockerImageTag", "latest")
      .put("documentationUrl", "airbyte.io")
      .build());
  private static final JsonNode STANDARD_SOURCE_DEFINITION2 = Jsons.jsonNode(ImmutableMap.builder()
      .put("sourceDefinitionId", UUID2)
      .put("name", "clones")
      .put("dockerRepository", "bank of karabraxos")
      .put("dockerImageTag", "v1.2.0")
      .put("documentationUrl", "airbyte.io")
      .build());
  private static final JsonNode AIRBYTE_METADATA_SERVER_ID = Jsons.jsonNode(ImmutableMap.of("key", "server_uuid", "value", UUID1));
  private static final JsonNode AIRBYTE_METADATA_VERSION = Jsons.jsonNode(ImmutableMap.of("key", "airbyte_version", "value", "v9"));

  private static final ResourceId SOURCE_DEFINITION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SOURCE_DEFINITION");
  private static final ResourceId AIRBYTE_METADATA_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.JOB, "AIRBYTE_METADATA");
  private static final Map<ResourceId, List<JsonNode>> INPUT_RECORDS = ImmutableMap
      .<ResourceId, List<JsonNode>>builder()
      .put(SOURCE_DEFINITION_RESOURCE_ID, ImmutableList.of(STANDARD_SOURCE_DEFINITION1, STANDARD_SOURCE_DEFINITION2))
      .put(AIRBYTE_METADATA_RESOURCE_ID, ImmutableList.of(AIRBYTE_METADATA_SERVER_ID, AIRBYTE_METADATA_VERSION))
      .build();

  @Test
  void test() {
    final Migration migration = new NoOpMigration(mock(Migration.class), VERSION);

    final MigrateWithMetadata migrateWithMetadata = new MigrateWithMetadata(migration);

    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils.createOutputConsumer(INPUT_RECORDS.keySet());
    migrateWithMetadata.migrate(MigrationTestUtils.convertListsToValues(INPUT_RECORDS), MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));
    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils.collectConsumersToList(outputConsumer);

    // clone the records
    assertOutput(INPUT_RECORDS, outputAsList);
  }

  private void assertOutput(Map<ResourceId, List<JsonNode>> expectedRecords, Map<ResourceId, List<JsonNode>> actualRecords) {
    // we inject records with timestamp to migrate version changes. filter it out here so that we can
    // test everything else.
    final Map<Boolean, List<JsonNode>> partitionedRecords = actualRecords.get(AIRBYTE_METADATA_RESOURCE_ID)
        .stream()
        .collect(Collectors.partitioningBy(r -> r.get("key").asText().contains("migrate_to")));
    final List<JsonNode> migrateRecords = partitionedRecords.get(true);
    final List<JsonNode> otherRecords = partitionedRecords.get(false);

    final HashMap<ResourceId, List<JsonNode>> actualRecordsCleaned = new HashMap<>(actualRecords);
    actualRecordsCleaned.put(AIRBYTE_METADATA_RESOURCE_ID, otherRecords);

    final HashMap<ResourceId, List<JsonNode>> cleanedExpectedRecords = new HashMap<>(expectedRecords);
    ((ObjectNode) cleanedExpectedRecords.get(AIRBYTE_METADATA_RESOURCE_ID).get(1)).put("value", VERSION);
    assertEquals(cleanedExpectedRecords, actualRecordsCleaned);

    assertEquals(1, migrateRecords.size());
    assertEquals(VERSION, migrateRecords.get(0).get("value").asText());
  }

}
