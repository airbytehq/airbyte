/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.ConfigSchema.STANDARD_DESTINATION_DEFINITION;
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
import io.airbyte.config.persistence.DeprecatedDatabaseConfigPersistence.ConnectorInfo;
import io.airbyte.db.instance.configs.DeprecatedConfigsDatabaseInstance;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
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
 * See {@link DeprecatedDatabaseConfigPersistenceLoadDataTest},
 * {@link DeprecatedDatabaseConfigPersistenceMigrateFileConfigsTest}, and
 * {@link DeprecatedDatabaseConfigPersistenceUpdateConnectorDefinitionsTest} for testing of specific
 * methods.
 */
public class DeprecatedDatabaseConfigPersistenceTest extends BaseDeprecatedDatabaseConfigPersistenceTest {

  @BeforeEach
  public void setup() throws Exception {
    database = new DeprecatedConfigsDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
    configPersistence = spy(new DeprecatedDatabaseConfigPersistence(database));
    database.query(ctx -> ctx.execute("TRUNCATE TABLE airbyte_configs"));
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  @Test
  public void testMultiWriteAndGetConfig() throws Exception {
    writeDestinations(configPersistence, Lists.newArrayList(DESTINATION_S3, DESTINATION_SNOWFLAKE));
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3),
        configPersistence.listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
  }

  @Test
  public void testWriteAndGetConfig() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3),
        configPersistence.listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
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
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3),
        List.of(configWithMetadata.get(0).getConfig(), configWithMetadata.get(1).getConfig()));
  }

  @Test
  public void testDeleteConfig() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3),
        configPersistence.listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
    deleteDestination(configPersistence, DESTINATION_S3);
    assertThrows(ConfigNotFoundException.class, () -> assertHasDestination(DESTINATION_S3));
    assertEquals(
        List.of(DESTINATION_SNOWFLAKE),
        configPersistence.listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class));
  }

  @Test
  public void testReplaceAllConfigs() throws Exception {
    writeDestination(configPersistence, DESTINATION_S3);
    writeDestination(configPersistence, DESTINATION_SNOWFLAKE);

    final Map<AirbyteConfig, Stream<?>> newConfigs = Map.of(ConfigSchema.STANDARD_SOURCE_DEFINITION, Stream.of(SOURCE_GITHUB, SOURCE_POSTGRES));

    configPersistence.replaceAllConfigs(newConfigs, true);

    // dry run does not change anything
    assertRecordCount(2);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);

    configPersistence.replaceAllConfigs(newConfigs, false);
    assertRecordCount(2);
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
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), Stream.of(Jsons.jsonNode(SOURCE_GITHUB), Jsons.jsonNode(SOURCE_POSTGRES)),
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
        .withDockerRepository(connectorRepository)
        .withDockerImageTag(oldVersion);
    final StandardSourceDefinition source2 = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
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
    final OffsetDateTime timestamp = OffsetDateTime.now();
    final UUID definitionId = UUID.randomUUID();
    final String connectorRepository = "airbyte/test-connector";

    // when the record does not exist, it is inserted
    final StandardSourceDefinition source1 = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.2");
    int insertionCount = database.query(ctx -> configPersistence.insertConfigRecord(
        ctx,
        timestamp,
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        Jsons.jsonNode(source1),
        ConfigSchema.STANDARD_SOURCE_DEFINITION.getIdFieldName()));
    assertEquals(1, insertionCount);
    // write an irrelevant source to make sure that it is not changed
    writeSource(configPersistence, SOURCE_GITHUB);
    assertRecordCount(2);
    assertHasSource(source1);
    assertHasSource(SOURCE_GITHUB);

    // when the record already exists, it is ignored
    final StandardSourceDefinition source2 = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.5");
    insertionCount = database.query(ctx -> configPersistence.insertConfigRecord(
        ctx,
        timestamp,
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        Jsons.jsonNode(source2),
        ConfigSchema.STANDARD_SOURCE_DEFINITION.getIdFieldName()));
    assertEquals(0, insertionCount);
    assertRecordCount(2);
    assertHasSource(source1);
    assertHasSource(SOURCE_GITHUB);
  }

  @Test
  public void testUpdateConfigRecord() throws Exception {
    final OffsetDateTime timestamp = OffsetDateTime.now();
    final UUID definitionId = UUID.randomUUID();
    final String connectorRepository = "airbyte/test-connector";

    final StandardSourceDefinition oldSource = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.3.5");
    writeSource(configPersistence, oldSource);
    // write an irrelevant source to make sure that it is not changed
    writeSource(configPersistence, SOURCE_GITHUB);
    assertRecordCount(2);
    assertHasSource(oldSource);
    assertHasSource(SOURCE_GITHUB);

    final StandardSourceDefinition newSource = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.3.5");
    database.query(ctx -> configPersistence.updateConfigRecord(
        ctx,
        timestamp,
        ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        Jsons.jsonNode(newSource),
        definitionId.toString()));
    assertRecordCount(2);
    assertHasSource(newSource);
    assertHasSource(SOURCE_GITHUB);
  }

  @Test
  public void testHasNewVersion() {
    assertTrue(DeprecatedDatabaseConfigPersistence.hasNewVersion("0.1.99", "0.2.0"));
    assertFalse(DeprecatedDatabaseConfigPersistence.hasNewVersion("invalid_version", "0.2.0"));
  }

  @Test
  public void testGetNewFields() {
    final JsonNode o1 = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode o2 = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3 }");
    assertEquals(Collections.emptySet(), DeprecatedDatabaseConfigPersistence.getNewFields(o1, o1));
    assertEquals(Collections.singleton("field3"), DeprecatedDatabaseConfigPersistence.getNewFields(o1, o2));
    assertEquals(Collections.singleton("field2"), DeprecatedDatabaseConfigPersistence.getNewFields(o2, o1));
  }

  @Test
  public void testGetDefinitionWithNewFields() {
    final JsonNode current = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode latest = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3, \"field4\": 4 }");
    final Set<String> newFields = Set.of("field3");

    assertEquals(current, DeprecatedDatabaseConfigPersistence.getDefinitionWithNewFields(current, latest, Collections.emptySet()));

    final JsonNode currentWithNewFields = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2, \"field3\": 3 }");
    assertEquals(currentWithNewFields, DeprecatedDatabaseConfigPersistence.getDefinitionWithNewFields(current, latest, newFields));
  }

}
