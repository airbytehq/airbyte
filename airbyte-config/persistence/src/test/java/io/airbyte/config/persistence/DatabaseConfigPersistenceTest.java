/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.ConfigSchema.*;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.DatabaseConfigPersistence.ConnectorInfo;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import java.time.Duration;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Stream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * See {@link DatabaseConfigPersistenceLoadDataTest},
 * {@link DatabaseConfigPersistenceMigrateFileConfigsTest}, and
 * {@link DatabaseConfigPersistenceUpdateConnectorDefinitionsTest} for testing of specific methods.
 */
public class DatabaseConfigPersistenceTest extends BaseDatabaseConfigPersistenceTest {

  @BeforeEach
  public void setup() throws Exception {
    database = new ConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DatabaseConfigPersistence(database));
    final ConfigsDatabaseMigrator configsDatabaseMigrator =
        new ConfigsDatabaseMigrator(database, DatabaseConfigPersistenceLoadDataTest.class.getName());
    final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(configsDatabaseMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
    database.query(ctx -> ctx
        .execute("TRUNCATE TABLE state, connection_operation, connection, operation, actor_oauth_parameter, actor, actor_definition, workspace"));
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  @Test
  public void testMultiWriteAndGetConfig() throws Exception {
    writeDestinations(configPersistence, Lists.newArrayList(DESTINATION_S3, DESTINATION_SNOWFLAKE));
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertThat(configPersistence
        .listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
            .hasSameElementsAs(List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3));
  }

  @Test
  public void testWriteAndGetConfig() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertThat(configPersistence
        .listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
            .hasSameElementsAs(List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3));
  }

  @Test
  public void testListConfigWithMetadata() throws Exception {
    final Instant now = Instant.now().minus(Duration.ofSeconds(1));
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);
    final List<ConfigWithMetadata<StandardDestinationDefinition>> configWithMetadata = configPersistence
        .listConfigsWithMetadata(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
    assertEquals(2, configWithMetadata.size());
    assertEquals("STANDARD_DESTINATION_DEFINITION", configWithMetadata.get(0).getConfigType());
    assertEquals("STANDARD_DESTINATION_DEFINITION", configWithMetadata.get(1).getConfigType());
    assertTrue(configWithMetadata.get(0).getCreatedAt().isAfter(now));
    assertTrue(configWithMetadata.get(0).getUpdatedAt().isAfter(now));
    assertTrue(configWithMetadata.get(1).getCreatedAt().isAfter(now));
    assertNotNull(configWithMetadata.get(0).getConfigId());
    assertNotNull(configWithMetadata.get(1).getConfigId());
    assertThat(List.of(configWithMetadata.get(0).getConfig(), configWithMetadata.get(1).getConfig()))
        .hasSameElementsAs(List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3));
  }

  @Test
  public void testDeleteConfig() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertThat(configPersistence
        .listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
            .hasSameElementsAs(List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3));
    deleteDestination(configPersistence, DESTINATION_S3);
    assertThrows(ConfigNotFoundException.class, () -> assertHasDestination(DESTINATION_S3));
    assertThat(configPersistence
        .listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
            .hasSameElementsAs(List.of(DESTINATION_SNOWFLAKE));
  }

  @Test
  public void testReplaceAllConfigs() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);

    final Map<AirbyteConfig, Stream<?>> newConfigs = Map.of(ConfigSchema.STANDARD_SOURCE_DEFINITION, Stream.of(SOURCE_GITHUB, SOURCE_POSTGRES));

    configPersistence.replaceAllConfigs(newConfigs, true);

    // dry run does not change anything
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    configPersistence.replaceAllConfigs(newConfigs, false);
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasSource(SOURCE_GITHUB);
    assertHasSource(SOURCE_POSTGRES);
  }

  @Test
  public void testDumpConfigs() throws Exception {
    writeSource(configPersistence, SOURCE_GITHUB);
    writeSource(configPersistence, SOURCE_POSTGRES);
    writeDestination(configPersistence, DESTINATION_S3);
    final Map<String, Stream<JsonNode>> actual = configPersistence.dumpConfigs();
    final Map<String, Stream<JsonNode>> expected = Map.of(
        STANDARD_SOURCE_DEFINITION.name(), Stream.of(Jsons.jsonNode(SOURCE_GITHUB), Jsons.jsonNode(SOURCE_POSTGRES)),
        STANDARD_DESTINATION_DEFINITION.name(), Stream.of(Jsons.jsonNode(DESTINATION_S3)));
    assertSameConfigDump(expected, actual);
  }

  @Test
  public void testGetConnectorRepositoryToInfoMap() throws Exception {
    final String connectorRepository = "airbyte/duplicated-connector";
    final String oldVersion = "0.1.10";
    final String newVersion = "0.2.0";
    final StandardSourceDefinition source1 = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withName("source-1")
        .withDockerRepository(connectorRepository)
        .withDockerImageTag(oldVersion);
    final StandardSourceDefinition source2 = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withName("source-2")
        .withDockerRepository(connectorRepository)
        .withDockerImageTag(newVersion);
    writeSource(configPersistence, source1);
    writeSource(configPersistence, source2);
    final Map<String, ConnectorInfo> result = database.query(ctx -> configPersistence.getConnectorRepositoryToInfoMap(ctx));
    // when there are duplicated connector definitions, the one with the latest version should be
    // retrieved
    assertEquals(newVersion, result.get(connectorRepository).dockerImageTag);
  }

  @Test
  public void testInsertConfigRecord() throws Exception {
    final UUID definitionId = UUID.randomUUID();
    final String connectorRepository = "airbyte/test-connector";

    // when the record does not exist, it is inserted
    final StandardSourceDefinition source1 = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.2")
        .withName("random-name");
    writeSource(configPersistence, source1);
    // write an irrelevant source to make sure that it is not changed
    writeSource(configPersistence, SOURCE_GITHUB);
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasSource(source1);
    assertHasSource(SOURCE_GITHUB);
    // when the record already exists, it is updated
    final StandardSourceDefinition source2 = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.5")
        .withName("random-name-2");
    writeSource(configPersistence, source2);
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasSource(source2);
    assertHasSource(SOURCE_GITHUB);
  }

  @Test
  public void testHasNewVersion() {
    assertTrue(DatabaseConfigPersistence.hasNewVersion("0.1.99", "0.2.0"));
    assertFalse(DatabaseConfigPersistence.hasNewVersion("invalid_version", "0.2.0"));
  }

  @Test
  public void testGetNewFields() {
    final JsonNode o1 = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode o2 = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3 }");
    assertEquals(Collections.emptySet(), DatabaseConfigPersistence.getNewFields(o1, o1));
    assertEquals(Collections.singleton("field3"), DatabaseConfigPersistence.getNewFields(o1, o2));
    assertEquals(Collections.singleton("field2"), DatabaseConfigPersistence.getNewFields(o2, o1));
  }

  @Test
  public void testGetDefinitionWithNewFields() {
    final JsonNode current = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode latest = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3, \"field4\": 4 }");
    final Set<String> newFields = Set.of("field3");

    assertEquals(current, DatabaseConfigPersistence.getDefinitionWithNewFields(current, latest, Collections.emptySet()));

    final JsonNode currentWithNewFields = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2, \"field3\": 3 }");
    assertEquals(currentWithNewFields, DatabaseConfigPersistence.getDefinitionWithNewFields(current, latest, newFields));
  }

}
