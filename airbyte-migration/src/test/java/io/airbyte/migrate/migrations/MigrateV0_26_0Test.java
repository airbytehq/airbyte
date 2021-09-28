/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static io.airbyte.migrate.migrations.MigrationV0_26_0.DESTINATION_CONNECTION_RESOURCE_ID;
import static io.airbyte.migrate.migrations.MigrationV0_26_0.STANDARD_SYNC_OPERATION_RESOURCE_ID;
import static io.airbyte.migrate.migrations.MigrationV0_26_0.STANDARD_SYNC_RESOURCE_ID;
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
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Spliterators;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.Test;

public class MigrateV0_26_0Test {

  private static final String INPUT_CONFIG_PATH = "migrations/migrationV0_26_0/input_config";
  private static final String OUTPUT_CONFIG_PATH = "migrations/migrationV0_26_0/output_config";
  public static final ResourceId STANDARD_WORKSPACE_RESOURCE_ID = ResourceId
      .fromConstantCase(ResourceType.CONFIG, "STANDARD_WORKSPACE");

  private Stream<JsonNode> getResourceStream(String resourcePath) throws IOException {
    final ArrayNode nodeArray = (ArrayNode) Yamls
        .deserialize(MoreResources.readResource(resourcePath));
    return StreamSupport
        .stream(Spliterators.spliteratorUnknownSize(nodeArray.iterator(), 0), false);
  }

  @Test
  void testMigration() throws IOException {
    MigrationV0_26_0 migration = (MigrationV0_26_0) Migrations.MIGRATIONS
        .stream()
        .filter(m -> m instanceof MigrationV0_26_0)
        .findAny()
        .orElse(null);
    assertNotNull(migration);
    migration = new MigrationTest(migration.previousMigration);

    final Map<ResourceId, Stream<JsonNode>> inputConfigs = ImmutableMap.of(
        STANDARD_SYNC_RESOURCE_ID,
        getResourceStream(INPUT_CONFIG_PATH + "/STANDARD_SYNC.yaml"),
        DESTINATION_CONNECTION_RESOURCE_ID,
        getResourceStream(INPUT_CONFIG_PATH + "/DESTINATION_CONNECTION.yaml"),
        STANDARD_WORKSPACE_RESOURCE_ID,
        getResourceStream(INPUT_CONFIG_PATH + "/STANDARD_WORKSPACE.yaml"));

    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils
        .createOutputConsumer(migration.getOutputSchema().keySet());
    migration.migrate(inputConfigs, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap
        .of(STANDARD_SYNC_RESOURCE_ID,
            getResourceStream(OUTPUT_CONFIG_PATH + "/STANDARD_SYNC.yaml")
                .collect(Collectors.toList()),
            DESTINATION_CONNECTION_RESOURCE_ID,
            getResourceStream(OUTPUT_CONFIG_PATH + "/DESTINATION_CONNECTION.yaml")
                .collect(Collectors.toList()),
            STANDARD_WORKSPACE_RESOURCE_ID,
            getResourceStream(OUTPUT_CONFIG_PATH + "/STANDARD_WORKSPACE.yaml")
                .collect(Collectors.toList()),
            STANDARD_SYNC_OPERATION_RESOURCE_ID,
            getResourceStream(OUTPUT_CONFIG_PATH + "/STANDARD_SYNC_OPERATION.yaml")
                .collect(Collectors.toList()));
    final Map<ResourceId, List<JsonNode>> expectedOutput =
        MigrationTestUtils
            .createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils
        .collectConsumersToList(outputConsumer);

    assertEquals(expectedOutput, outputAsList);
  }

  public static class MigrationTest extends MigrationV0_26_0 {

    public MigrationTest(Migration previousMigration) {
      super(previousMigration);
    }

    @Override
    protected String uuid() {
      return "8f75e15a-a427-4f12-94ff-b3130df50f92";
    }

  }

}
