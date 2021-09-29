/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static io.airbyte.migrate.migrations.MigrationV0_24_0.STANDARD_SYNC_RESOURCE_ID;
import static io.airbyte.migrate.migrations.MigrationV0_24_0.STANDARD_SYNC_SCHEDULE_RESOURCE_ID;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationTestUtils;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.Migrations;
import io.airbyte.migrate.ResourceId;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.Test;

public class MigrateV0_24_0Test {

  /**
   * The test resource directory is named differently from the main resource directory (with the extra
   * "Test" suffix). If their names are the same, the main one will somehow be overridden by the test
   * one. Consequently, {@link MigrationV0_24_0} cannot correctly get the new standard sync file and
   * resolve the output schema.
   */
  private static final String INPUT_CONFIG_PATH = "migrations/migrationV0_24_0Test/input_config";
  private static final String OUTPUT_CONFIG_PATH = "migrations/migrationV0_24_0Test/output_config";

  private Stream<JsonNode> getResourceStream(String resourcePath) throws IOException {
    final ArrayNode nodeArray = (ArrayNode) Yamls
        .deserialize(MoreResources.readResource(resourcePath));
    return StreamSupport
        .stream(Spliterators.spliteratorUnknownSize(nodeArray.iterator(), 0), false);
  }

  @Test
  void testMigration() throws IOException {
    final Migration migration = Migrations.MIGRATIONS
        .stream()
        .filter(m -> m instanceof MigrationV0_24_0)
        .findAny()
        .orElse(null);
    assertNotNull(migration);

    final Map<ResourceId, Stream<JsonNode>> inputConfigs = ImmutableMap.of(
        STANDARD_SYNC_RESOURCE_ID,
        getResourceStream(INPUT_CONFIG_PATH + "/STANDARD_SYNC.yaml"),
        STANDARD_SYNC_SCHEDULE_RESOURCE_ID,
        getResourceStream(INPUT_CONFIG_PATH + "/STANDARD_SYNC_SCHEDULE.yaml"));

    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils
        .createOutputConsumer(migration.getOutputSchema().keySet());
    migration.migrate(inputConfigs, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap
        .of(STANDARD_SYNC_RESOURCE_ID,
            getResourceStream(OUTPUT_CONFIG_PATH + "/STANDARD_SYNC.yaml")
                .collect(Collectors.toList()));
    final Map<ResourceId, List<JsonNode>> expectedOutput = MigrationTestUtils
        .createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils
        .collectConsumersToList(outputConsumer);
    assertEquals(expectedOutput, outputAsList);
  }

}
