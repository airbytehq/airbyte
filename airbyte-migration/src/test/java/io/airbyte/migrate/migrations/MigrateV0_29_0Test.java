/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.migrate.MigrationTestUtils;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.Migrations;
import io.airbyte.migrate.ResourceId;
import io.airbyte.migrate.ResourceType;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Spliterators;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.junit.jupiter.api.Test;

public class MigrateV0_29_0Test {

  private static final UUID NEW_WORKSPACE_ID = UUID.fromString("763a9b47-f5fa-45c0-8caa-00b51f108183");
  private static final String INPUT_CONFIG_PATH = "migrations/migrationV0_29_0/input_config";
  private static final String OUTPUT_CONFIG_PATH = "migrations/migrationV0_29_0/output_config";

  private static final ResourceId SOURCE_DEF_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SOURCE_DEFINITION");
  private static final ResourceId DEST_DEF_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_DESTINATION_DEFINITION");
  private static final ResourceId WORKSPACE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_WORKSPACE");
  private static final ResourceId SOURCE_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "SOURCE_CONNECTION");
  private static final ResourceId DESTINATION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "DESTINATION_CONNECTION");
  private static final ResourceId CONNECTION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC");
  private static final ResourceId OPERATION_RESOURCE_ID = ResourceId.fromConstantCase(ResourceType.CONFIG, "STANDARD_SYNC_OPERATION");

  private Stream<JsonNode> getResourceStream(String resourcePath) throws IOException {
    final ArrayNode nodeArray = (ArrayNode) Yamls.deserialize(MoreResources.readResource(resourcePath));
    return StreamSupport.stream(Spliterators.spliteratorUnknownSize(nodeArray.iterator(), 0), false);
  }

  private List<JsonNode> getResourceList(String resourcePath) throws IOException {
    return getResourceStream(resourcePath).collect(Collectors.toList());
  }

  @Test
  void testMigration() throws IOException {
    final MigrationV0_29_0 migration = new MigrationV0_29_0(Migrations.MIGRATION_V_0_28_0, () -> NEW_WORKSPACE_ID);

    final Map<ResourceId, Stream<JsonNode>> inputConfigs = ImmutableMap.<ResourceId, Stream<JsonNode>>builder()
        .put(SOURCE_DEF_RESOURCE_ID, getResourceStream(INPUT_CONFIG_PATH + "/SOURCE_DEFINITION.yaml"))
        .put(DEST_DEF_RESOURCE_ID, getResourceStream(INPUT_CONFIG_PATH + "/DESTINATION_DEFINITION.yaml"))
        .put(WORKSPACE_RESOURCE_ID, getResourceStream(INPUT_CONFIG_PATH + "/STANDARD_WORKSPACE.yaml"))
        .put(SOURCE_RESOURCE_ID, getResourceStream(INPUT_CONFIG_PATH + "/SOURCE_CONNECTION.yaml"))
        .put(DESTINATION_RESOURCE_ID, getResourceStream(INPUT_CONFIG_PATH + "/DESTINATION_CONNECTION.yaml"))
        .put(CONNECTION_RESOURCE_ID, getResourceStream(INPUT_CONFIG_PATH + "/STANDARD_SYNC.yaml"))
        .put(OPERATION_RESOURCE_ID, getResourceStream(INPUT_CONFIG_PATH + "/STANDARD_SYNC_OPERATION.yaml"))
        .build();

    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils
        .createOutputConsumer(migration.getOutputSchema().keySet());

    migration.migrate(inputConfigs, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap.<ResourceId, List<JsonNode>>builder()
        .put(SOURCE_DEF_RESOURCE_ID, getResourceList(INPUT_CONFIG_PATH + "/SOURCE_DEFINITION.yaml"))
        .put(DEST_DEF_RESOURCE_ID, getResourceList(INPUT_CONFIG_PATH + "/DESTINATION_DEFINITION.yaml"))
        .put(WORKSPACE_RESOURCE_ID, getResourceList(OUTPUT_CONFIG_PATH + "/STANDARD_WORKSPACE.yaml"))
        .put(SOURCE_RESOURCE_ID, getResourceList(OUTPUT_CONFIG_PATH + "/SOURCE_CONNECTION.yaml"))
        .put(DESTINATION_RESOURCE_ID, getResourceList(OUTPUT_CONFIG_PATH + "/DESTINATION_CONNECTION.yaml"))
        .put(CONNECTION_RESOURCE_ID, getResourceList(OUTPUT_CONFIG_PATH + "/STANDARD_SYNC.yaml"))
        .put(OPERATION_RESOURCE_ID, getResourceList(OUTPUT_CONFIG_PATH + "/STANDARD_SYNC_OPERATION.yaml"))
        .build();

    final Map<ResourceId, List<JsonNode>> expectedOutput = MigrationTestUtils
        .createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils.collectConsumersToList(outputConsumer);

    assertExpectedOutput(expectedOutput, outputAsList);
  }

  private void assertExpectedOutput(Map<ResourceId, List<JsonNode>> expected, Map<ResourceId, List<JsonNode>> actual) {
    assertEquals(expected.keySet(), actual.keySet());
    expected.forEach((key, value) -> assertEquals(value, actual.get(key), String.format("Resources output do not match for %s:", key.getName())));
    assertEquals(expected, actual);
  }

}
