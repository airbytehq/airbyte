/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.ConfigSchema.STANDARD_DESTINATION_DEFINITION;
import static io.airbyte.config.ConfigSchema.STANDARD_SOURCE_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.Tables.ACTOR_DEFINITION;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.eq;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.ReleaseStage;
import io.airbyte.config.persistence.DatabaseConfigPersistence.ConnectorInfo;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.development.DevDatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import java.io.Closeable;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.assertj.core.api.Assertions;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * See {@link DatabaseConfigPersistenceLoadDataTest} and
 * {@link DatabaseConfigPersistenceUpdateConnectorDefinitionsTest} for testing of specific methods.
 */
public class DatabaseConfigPersistenceTest extends BaseDatabaseConfigPersistenceTest {

  @BeforeEach
  public void setup() throws Exception {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    database = new ConfigsDatabaseInstance(dslContext).getAndInitialize();
    flyway = FlywayFactory.create(dataSource, DatabaseConfigPersistenceLoadDataTest.class.getName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    database = new ConfigsDatabaseInstance(dslContext).getAndInitialize();
    configPersistence = spy(new DatabaseConfigPersistence(database, jsonSecretsProcessor));
    final ConfigsDatabaseMigrator configsDatabaseMigrator =
        new ConfigsDatabaseMigrator(database, flyway);
    final DevDatabaseMigrator devDatabaseMigrator = new DevDatabaseMigrator(configsDatabaseMigrator);
    MigrationDevHelper.runLastMigration(devDatabaseMigrator);
    truncateAllTables();
  }

  @AfterEach
  void tearDown() throws IOException {
    dslContext.close();
    if (dataSource instanceof Closeable closeable) {
      closeable.close();
    }
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
  public void testGetConfigWithMetadata() throws Exception {
    final Instant now = Instant.now().minus(Duration.ofSeconds(1));
    writeDestination(configPersistence, DESTINATION_S3);
    final ConfigWithMetadata<StandardDestinationDefinition> configWithMetadata = configPersistence.getConfigWithMetadata(
        STANDARD_DESTINATION_DEFINITION,
        DESTINATION_S3.getDestinationDefinitionId().toString(),
        StandardDestinationDefinition.class);
    assertEquals("STANDARD_DESTINATION_DEFINITION", configWithMetadata.getConfigType());
    assertTrue(configWithMetadata.getCreatedAt().isAfter(now));
    assertTrue(configWithMetadata.getUpdatedAt().isAfter(now));
    assertEquals(DESTINATION_S3.getDestinationDefinitionId().toString(), configWithMetadata.getConfigId());
    assertEquals(DESTINATION_S3, configWithMetadata.getConfig());
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
  public void testDumpConfigsWithoutSecret() throws Exception {
    final ConnectorSpecification mockedConnectorSpec = new ConnectorSpecification()
        .withConnectionSpecification(
            Jsons.emptyObject());
    doReturn(new StandardDestinationDefinition()
        .withSpec(mockedConnectorSpec)).when(configPersistence).getConfig(eq(ConfigSchema.STANDARD_DESTINATION_DEFINITION), any(), any());
    doReturn(new StandardSourceDefinition()
        .withSpec(mockedConnectorSpec)).when(configPersistence).getConfig(eq(ConfigSchema.STANDARD_SOURCE_DEFINITION), any(), any());

    writeSourceWithSourceConnection(configPersistence, SOURCE_GITHUB);
    writeSourceWithSourceConnection(configPersistence, SOURCE_POSTGRES);
    writeDestinationWithDestinationConnection(configPersistence, DESTINATION_S3);
    final Map<String, Stream<JsonNode>> result = configPersistence.dumpConfigs();
    result.values().forEach(stream -> {
      stream.collect(Collectors.toList());
    });
    verify(jsonSecretsProcessor, times(3)).prepareSecretsForOutput(any(), any());
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
        .withName("random-name")
        .withTombstone(false)
        .withReleaseDate(LocalDate.now().toString())
        .withReleaseStage(ReleaseStage.ALPHA);
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
        .withName("random-name-2")
        .withTombstone(false)
        .withReleaseDate(LocalDate.now().minusDays(1).toString())
        .withReleaseStage(ReleaseStage.BETA);
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

  @Test
  public void testActorDefinitionReleaseDate() throws Exception {
    final UUID definitionId = UUID.randomUUID();
    final String connectorRepository = "airbyte/test-connector";

    // when the record does not exist, it is inserted
    final StandardSourceDefinition source1 = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.2")
        .withName("random-name")
        .withTombstone(false);
    writeSource(configPersistence, source1);
  }

  @Test
  public void filterCustomSource() {
    final Map<String, ConnectorInfo> sourceMap = new HashMap<>();
    final String nonCustomKey = "non-custom";
    final String customKey = "custom";
    sourceMap.put(nonCustomKey, new ConnectorInfo("id", Jsons.jsonNode(SOURCE_POSTGRES)));
    sourceMap.put(customKey, new ConnectorInfo("id", Jsons.jsonNode(SOURCE_CUSTOM)));

    final Map<String, ConnectorInfo> filteredSourceMap = configPersistence.filterCustomConnector(sourceMap, ConfigSchema.STANDARD_SOURCE_DEFINITION);

    Assertions.assertThat(filteredSourceMap).containsOnlyKeys(nonCustomKey);
  }

  @Test
  public void filterCustomDestination() {
    final Map<String, ConnectorInfo> sourceMap = new HashMap<>();
    final String nonCustomKey = "non-custom";
    final String customKey = "custom";
    sourceMap.put(nonCustomKey, new ConnectorInfo("id", Jsons.jsonNode(DESTINATION_S3)));
    sourceMap.put(customKey, new ConnectorInfo("id", Jsons.jsonNode(DESTINATION_CUSTOM)));

    final Map<String, ConnectorInfo> filteredSourceMap = configPersistence.filterCustomConnector(sourceMap,
        ConfigSchema.STANDARD_DESTINATION_DEFINITION);

    Assertions.assertThat(filteredSourceMap).containsOnlyKeys(nonCustomKey);
  }

}
