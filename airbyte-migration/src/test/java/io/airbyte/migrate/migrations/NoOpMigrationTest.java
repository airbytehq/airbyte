/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationTestUtils;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class NoOpMigrationTest {

  private static final String VERSION = "v9";
  private static final ResourceId SYNC_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");

  @Test
  void testMigration() throws IOException {
    final JsonNode schema = Jsons.deserialize(MoreResources.readResource("migrations/migrationV0_14_3/example_input_schema.json"));
    final JsonNode sync = Jsons.jsonNode(ImmutableMap.<String, Object>builder()
        .put("sourceId", UUID.randomUUID().toString())
        .put("destinationId", UUID.randomUUID().toString())
        .put("connectionId", UUID.randomUUID().toString())
        .put("name", "users_sync")
        .put("status", "active")
        .put("schema", schema)
        .build());

    final Map<ResourceId, Stream<JsonNode>> records = ImmutableMap.of(SYNC_RESOURCE_ID, Stream.of(sync));

    final Migration migration = new NoOpMigration(new MigrationV0_14_0(), VERSION);
    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils.createOutputConsumer(migration.getOutputSchema().keySet());
    migration.migrate(records, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap.of(SYNC_RESOURCE_ID, ImmutableList.of(sync));
    final Map<ResourceId, List<JsonNode>> expectedOutput =
        MigrationTestUtils.createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils.collectConsumersToList(outputConsumer);
    assertEquals(expectedOutput, outputAsList);
  }

}
