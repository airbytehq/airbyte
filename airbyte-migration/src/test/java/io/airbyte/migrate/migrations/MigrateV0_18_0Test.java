/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationTestUtils;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.Migrations;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class MigrateV0_18_0Test {

  private static final ResourceId SYNC_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");

  @Test
  void testMigration() throws IOException {
    final Migration migration = Migrations.MIGRATIONS
        .stream()
        .filter(m -> m instanceof MigrationV0_18_0)
        .findAny()
        .orElse(null);
    assertNotNull(migration);

    // construct a sync object. in this migration we modify the catalog, so we will use this as
    // a base.
    final JsonNode syncWithoutCatalog = Jsons.jsonNode(ImmutableMap.<String, String>builder()
        .put("sourceId", UUID.randomUUID().toString())
        .put("destinationId", UUID.randomUUID().toString())
        .put("connectionId", UUID.randomUUID().toString())
        .put("name", "users_sync")
        .put("status", "active")
        .build());

    // input Catalog
    final JsonNode inputCatalog = Jsons.deserialize(MoreResources.readResource("migrations/migrationV0_18_0/example_input_catalog.json"));
    final JsonNode syncInputCatalog = Jsons.clone(syncWithoutCatalog);
    ((ObjectNode) syncInputCatalog).set("catalog", inputCatalog);

    // Output Catalog
    final JsonNode outputCatalog = Jsons.deserialize(MoreResources.readResource("migrations/migrationV0_18_0/example_output_catalog.json"));
    final JsonNode syncOutputCatalog = Jsons.clone(syncWithoutCatalog);
    ((ObjectNode) syncOutputCatalog).set("catalog", outputCatalog);

    final Map<ResourceId, Stream<JsonNode>> records = ImmutableMap.of(SYNC_RESOURCE_ID, Stream.of(syncInputCatalog));

    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils.createOutputConsumer(migration.getOutputSchema().keySet());
    migration.migrate(records, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap.of(SYNC_RESOURCE_ID, ImmutableList.of(syncOutputCatalog));
    final Map<ResourceId, List<JsonNode>> expectedOutput =
        MigrationTestUtils.createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils.collectConsumersToList(outputConsumer);
    assertEquals(expectedOutput, outputAsList);
  }

}
