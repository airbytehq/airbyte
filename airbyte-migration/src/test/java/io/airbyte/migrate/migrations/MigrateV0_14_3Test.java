/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
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

class MigrateV0_14_3Test {

  private static final ResourceId SYNC_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");

  @Test
  void testMigration() throws IOException {
    // construct a sync object. in this migration we swap our schema for catalog, so we will use this as
    // a base.
    final JsonNode syncWithoutSchema = Jsons.jsonNode(ImmutableMap.<String, String>builder()
        .put("sourceId", UUID.randomUUID().toString())
        .put("destinationId", UUID.randomUUID().toString())
        .put("connectionId", UUID.randomUUID().toString())
        .put("name", "users_sync")
        .put("status", "active")
        .build());

    // sync with schema
    final JsonNode schema = Jsons.deserialize(MoreResources.readResource("migrations/migrationV0_14_3/example_input_schema.json"));
    final JsonNode syncWithSchema = Jsons.clone(syncWithoutSchema);
    ((ObjectNode) syncWithSchema).set("schema", schema);

    // sync with catalog
    final JsonNode configuredCatalog = Jsons.deserialize(MoreResources.readResource("migrations/migrationV0_14_3/example_output_schema.json"));
    final JsonNode syncWithCatalog = Jsons.clone(syncWithoutSchema);
    ((ObjectNode) syncWithCatalog).set("catalog", configuredCatalog);

    final Map<ResourceId, Stream<JsonNode>> records = ImmutableMap.of(SYNC_RESOURCE_ID, Stream.of(syncWithSchema));

    final MigrationV0_14_3 migration = new MigrationV0_14_3(new MigrationV0_14_0());
    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils.createOutputConsumer(migration.getOutputSchema().keySet());
    migration.migrate(records, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap.of(SYNC_RESOURCE_ID, ImmutableList.of(syncWithCatalog));
    final Map<ResourceId, List<JsonNode>> expectedOutput =
        MigrationTestUtils.createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils.collectConsumersToList(outputConsumer);
    assertEquals(expectedOutput, outputAsList);
  }

}
