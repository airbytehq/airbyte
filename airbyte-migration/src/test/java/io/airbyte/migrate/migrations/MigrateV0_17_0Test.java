/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.ListConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.migrate.Migration;
import io.airbyte.migrate.MigrationTestUtils;
import io.airbyte.migrate.MigrationUtils;
import io.airbyte.migrate.Migrations;
import io.airbyte.migrate.ResourceId;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;

class MigrateV0_17_0Test {

  private static final ImmutableMap<String, String> POSTGRES_DESTINATION = ImmutableMap.<String, String>builder()
      .put("destinationDefinitionId", "25c5221d-dce2-4163-ade9-739ef790f503")
      .put("name", "Postgres")
      .put("dockerRepository", "airbyte/destination-postgres")
      .put("documentationUrl", "https://docs.airbyte.io/integrations/destinations/postgres")
      .build();
  private static final ImmutableMap<String, String> BIGQUERY_DESTINATION = ImmutableMap.<String, String>builder()
      .put("destinationDefinitionId", "22f6c74f-5699-40ff-833c-4a879ea40133")
      .put("name", "BigQuery")
      .put("dockerRepository", "airbyte/destination-bigquery")
      .put("documentationUrl", "https://docs.airbyte.io/integrations/destinations/bigquery")
      .build();
  private static final ImmutableMap<String, String> CUSTOM_DESTINATION = ImmutableMap.<String, String>builder()
      .put("destinationDefinitionId", UUID.randomUUID().toString())
      .put("name", "Custom Destination")
      .put("dockerRepository", "my-own-repo/destination-custom")
      .put("documentationUrl", "https://docs.airbyte.io/integrations/destinations/custom")
      .build();

  private static final ImmutableMap<String, String> POSTGRES_SOURCE = ImmutableMap.<String, String>builder()
      .put("sourceDefinitionId", "decd338e-5647-4c0b-adf4-da0e75f5a750")
      .put("name", "Postgres")
      .put("dockerRepository", "airbyte/source-postgres")
      .put("documentationUrl", "https://hub.docker.com/r/airbyte/source-postgres")
      .build();
  private static final ImmutableMap<String, String> FILE_SOURCE = ImmutableMap.<String, String>builder()
      .put("sourceDefinitionId", "778daa7c-feaf-4db6-96f3-70fd645acc77")
      .put("name", "File")
      .put("dockerRepository", "airbyte/source-file")
      .put("documentationUrl", "https://hub.docker.com/r/airbyte/source-file")
      .build();
  private static final ImmutableMap<String, String> CUSTOM_SOURCE = ImmutableMap.<String, String>builder()
      .put("sourceDefinitionId", UUID.randomUUID().toString())
      .put("name", "Custom Source")
      .put("dockerRepository", "my-own-repo/source-custom")
      .put("documentationUrl", "https://hub.docker.com/r/airbyte/source-custom")
      .build();
  private static final ImmutableMap<String, String> UNKNOWN_SOURCE = ImmutableMap.<String, String>builder()
      .put("sourceDefinitionId", UUID.randomUUID().toString())
      .put("name", "Unknown Source")
      .build();

  @Test
  void testMigration() {
    final Migration migration = Migrations.MIGRATIONS
        .stream()
        .filter(m -> m instanceof MigrationV0_17_0)
        .findAny()
        .orElse(null);
    assertNotNull(migration);

    final Map<ResourceId, Stream<JsonNode>> records = ImmutableMap.of(
        MigrationV0_17_0.STANDARD_DESTINATION_DEFINITION_RESOURCE_ID, Stream.of(
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(POSTGRES_DESTINATION).put("dockerImageTag", "0.1.42").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(BIGQUERY_DESTINATION).put("dockerImageTag", "0.3.51").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(CUSTOM_DESTINATION).put("dockerImageTag", "0.1.42").build())),
        MigrationV0_17_0.STANDARD_SOURCE_DEFINITION_RESOURCE_ID, Stream.of(
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(POSTGRES_SOURCE).build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(FILE_SOURCE).put("dockerImageTag", "My own custom version").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(CUSTOM_SOURCE).put("dockerImageTag", "dev").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(UNKNOWN_SOURCE).put("dockerImageTag", "0.1.0").build())));

    final Map<ResourceId, ListConsumer<JsonNode>> outputConsumer = MigrationTestUtils.createOutputConsumer(migration.getOutputSchema().keySet());
    migration.migrate(records, MigrationUtils.mapRecordConsumerToConsumer(outputConsumer));

    final Map<ResourceId, List<JsonNode>> expectedOutputOverrides = ImmutableMap.of(
        MigrationV0_17_0.STANDARD_DESTINATION_DEFINITION_RESOURCE_ID, ImmutableList.of(
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(POSTGRES_DESTINATION).put("dockerImageTag", "0.2.0").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(BIGQUERY_DESTINATION).put("dockerImageTag", "0.3.51").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(CUSTOM_DESTINATION).put("dockerImageTag", "0.1.42").build())),
        MigrationV0_17_0.STANDARD_SOURCE_DEFINITION_RESOURCE_ID, ImmutableList.of(
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(POSTGRES_SOURCE).build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(FILE_SOURCE).put("dockerImageTag", "My own custom version").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(CUSTOM_SOURCE).put("dockerImageTag", "dev").build()),
            Jsons.jsonNode(ImmutableMap.<String, String>builder().putAll(UNKNOWN_SOURCE).put("dockerImageTag", "0.1.0").build())));
    final Map<ResourceId, List<JsonNode>> expectedOutput =
        MigrationTestUtils.createExpectedOutput(migration.getOutputSchema().keySet(), expectedOutputOverrides);

    final Map<ResourceId, List<JsonNode>> outputAsList = MigrationTestUtils.collectConsumersToList(outputConsumer);
    assertEquals(expectedOutput, outputAsList);
  }

}
