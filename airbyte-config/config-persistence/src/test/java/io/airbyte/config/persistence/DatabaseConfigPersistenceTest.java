/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.ConfigSchema.STANDARD_DESTINATION_DEFINITION;
import static io.airbyte.config.ConfigSchema.STANDARD_SOURCE_DEFINITION;
import static io.airbyte.db.instance.configs.jooq.generated.Tables.ACTOR_DEFINITION;
import static org.assertj.core.api.Assertions.assertThat;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.count;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.spy;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.Geography;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.ReleaseStage;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.DatabaseConfigPersistence.ConnectorInfo;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.Record1;
import org.jooq.Result;
import org.jooq.Table;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * See {@link DatabaseConfigPersistenceUpdateConnectorDefinitionsTest} for testing of specific
 * methods.
 */
@SuppressWarnings({"PMD.SignatureDeclareThrowsException", "PMD.ShortVariable", "PMD.JUnitTestsShouldIncludeAssert"})
class DatabaseConfigPersistenceTest extends BaseConfigDatabaseTest {

  public static final String DEFAULT_PROTOCOL_VERSION = "0.2.0";
  protected static final StandardSourceDefinition SOURCE_GITHUB = new StandardSourceDefinition()
      .withName("GitHub")
      .withSourceDefinitionId(UUID.fromString("ef69ef6e-aa7f-4af1-a01d-ef775033524e"))
      .withDockerRepository("airbyte/source-github")
      .withDockerImageTag("0.2.3")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/github")
      .withIcon("github.svg")
      .withSourceType(SourceType.API)
      .withProtocolVersion(DEFAULT_PROTOCOL_VERSION)
      .withTombstone(false);
  protected static final StandardSourceDefinition SOURCE_POSTGRES = new StandardSourceDefinition()
      .withName("Postgres")
      .withSourceDefinitionId(UUID.fromString("decd338e-5647-4c0b-adf4-da0e75f5a750"))
      .withDockerRepository("airbyte/source-postgres")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withSourceType(SourceType.DATABASE)
      .withTombstone(false);
  protected static final StandardSourceDefinition SOURCE_CUSTOM = new StandardSourceDefinition()
      .withName("Custom")
      .withSourceDefinitionId(UUID.fromString("baba338e-5647-4c0b-adf4-da0e75f5a750"))
      .withDockerRepository("airbyte/cusom")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withSourceType(SourceType.DATABASE)
      .withCustom(true)
      .withReleaseStage(ReleaseStage.CUSTOM)
      .withTombstone(false);
  protected static final StandardDestinationDefinition DESTINATION_SNOWFLAKE = new StandardDestinationDefinition()
      .withName("Snowflake")
      .withDestinationDefinitionId(UUID.fromString("424892c4-daac-4491-b35d-c6688ba547ba"))
      .withDockerRepository("airbyte/destination-snowflake")
      .withDockerImageTag("0.3.16")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/destinations/snowflake")
      .withProtocolVersion(DEFAULT_PROTOCOL_VERSION)
      .withTombstone(false);
  protected static final StandardDestinationDefinition DESTINATION_S3 = new StandardDestinationDefinition()
      .withName("S3")
      .withDestinationDefinitionId(UUID.fromString("4816b78f-1489-44c1-9060-4b19d5fa9362"))
      .withDockerRepository("airbyte/destination-s3")
      .withDockerImageTag("0.1.12")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/destinations/s3")
      .withProtocolVersion(DEFAULT_PROTOCOL_VERSION)
      .withTombstone(false);
  protected static final StandardDestinationDefinition DESTINATION_CUSTOM = new StandardDestinationDefinition()
      .withName("Custom")
      .withDestinationDefinitionId(UUID.fromString("baba338e-5647-4c0b-adf4-da0e75f5a750"))
      .withDockerRepository("airbyte/cusom")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withCustom(true)
      .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM)
      .withTombstone(false);
  private static final String CANNOT_BE_NULL = "can not be null";

  private DatabaseConfigPersistence configPersistence;

  @BeforeEach
  public void setup() throws Exception {
    configPersistence = spy(new DatabaseConfigPersistence(database));
    truncateAllTables();
  }

  @Test
  void testMultiWriteAndGetConfig() throws Exception {
    writeDestinations(configPersistence, Lists.newArrayList(DESTINATION_S3, DESTINATION_SNOWFLAKE));
    assertRecordCount(2, ACTOR_DEFINITION);
    assertHasDestination(DESTINATION_S3);
    assertHasDestination(DESTINATION_SNOWFLAKE);
    assertThat(configPersistence
        .listConfigs(STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class))
            .hasSameElementsAs(List.of(DESTINATION_SNOWFLAKE, DESTINATION_S3));
  }

  @Test
  void testWriteAndGetConfig() throws Exception {
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
  void testGetConfigWithMetadata() throws Exception {
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
  void testListConfigWithMetadata() throws Exception {
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
  void testDeleteConfig() throws Exception {
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
  void testGetConnectorRepositoryToInfoMap() throws Exception {
    final String connectorRepository = "airbyte/duplicated-connector";
    final String oldVersion = "0.1.10";
    final String newVersion = DEFAULT_PROTOCOL_VERSION;
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
  void testInsertConfigRecord() throws Exception {
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
  void testHasNewVersion() {
    assertTrue(DatabaseConfigPersistence.hasNewVersion("0.1.99", DEFAULT_PROTOCOL_VERSION));
    assertFalse(DatabaseConfigPersistence.hasNewVersion("invalid_version", "0.1.2"));
  }

  @Test
  void testHasNewPatchVersion() {
    assertFalse(DatabaseConfigPersistence.hasNewPatchVersion("0.1.99", DEFAULT_PROTOCOL_VERSION));
    assertFalse(DatabaseConfigPersistence.hasNewPatchVersion("invalid_version", "0.3.1"));
    assertTrue(DatabaseConfigPersistence.hasNewPatchVersion("0.1.0", "0.1.3"));
  }

  @Test
  void testGetNewFields() {
    final JsonNode o1 = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode o2 = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3 }");
    assertEquals(Collections.emptySet(), DatabaseConfigPersistence.getNewFields(o1, o1));
    assertEquals(Collections.singleton("field3"), DatabaseConfigPersistence.getNewFields(o1, o2));
    assertEquals(Collections.singleton("field2"), DatabaseConfigPersistence.getNewFields(o2, o1));
  }

  @Test
  void testGetDefinitionWithNewFields() {
    final JsonNode current = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode latest = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3, \"field4\": 4 }");
    final Set<String> newFields = Set.of("field3");

    assertEquals(current, DatabaseConfigPersistence.getDefinitionWithNewFields(current, latest, Collections.emptySet()));

    final JsonNode currentWithNewFields = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2, \"field3\": 3 }");
    assertEquals(currentWithNewFields, DatabaseConfigPersistence.getDefinitionWithNewFields(current, latest, newFields));
  }

  @Test
  void testActorDefinitionReleaseDate() throws Exception {
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
  void filterCustomSource() {
    final Map<String, ConnectorInfo> sourceMap = new HashMap<>();
    final String nonCustomKey = "non-custom";
    final String customKey = "custom";
    sourceMap.put(nonCustomKey, new ConnectorInfo("id", Jsons.jsonNode(SOURCE_POSTGRES)));
    sourceMap.put(customKey, new ConnectorInfo("id", Jsons.jsonNode(SOURCE_CUSTOM)));

    final Map<String, ConnectorInfo> filteredSourceMap = configPersistence.filterCustomConnector(sourceMap, STANDARD_SOURCE_DEFINITION);

    assertThat(filteredSourceMap).containsOnlyKeys(nonCustomKey);
  }

  @Test
  void filterCustomDestination() {
    final Map<String, ConnectorInfo> sourceMap = new HashMap<>();
    final String nonCustomKey = "non-custom";
    final String customKey = "custom";
    sourceMap.put(nonCustomKey, new ConnectorInfo("id", Jsons.jsonNode(DESTINATION_S3)));
    sourceMap.put(customKey, new ConnectorInfo("id", Jsons.jsonNode(DESTINATION_CUSTOM)));

    final Map<String, ConnectorInfo> filteredSourceMap = configPersistence.filterCustomConnector(sourceMap,
        STANDARD_DESTINATION_DEFINITION);

    assertThat(filteredSourceMap).containsOnlyKeys(nonCustomKey);
  }

  void writeSource(final ConfigPersistence configPersistence, final StandardSourceDefinition source) throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(), source);
  }

  void writeSourceWithSourceConnection(final ConfigPersistence configPersistence, final StandardSourceDefinition source)
      throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(), source);
    final UUID connectionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withName(CANNOT_BE_NULL)
        .withSlug(CANNOT_BE_NULL)
        .withInitialSetupComplete(true)
        .withDefaultGeography(Geography.AUTO);
    configPersistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString(), workspace);

    final SourceConnection sourceConnection = new SourceConnection()
        .withSourceId(connectionId)
        .withWorkspaceId(workspaceId)
        .withName(CANNOT_BE_NULL)
        .withSourceDefinitionId(source.getSourceDefinitionId());
    configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, connectionId.toString(), sourceConnection);
  }

  void writeDestination(final ConfigPersistence configPersistence, final StandardDestinationDefinition destination)
      throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(), destination);
  }

  void writeDestinationWithDestinationConnection(final ConfigPersistence configPersistence,
                                                 final StandardDestinationDefinition destination)
      throws Exception {
    configPersistence.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(), destination);
    final UUID connectionId = UUID.randomUUID();
    final UUID workspaceId = UUID.randomUUID();
    final StandardWorkspace workspace = new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withName(CANNOT_BE_NULL)
        .withSlug(CANNOT_BE_NULL)
        .withInitialSetupComplete(true)
        .withDefaultGeography(Geography.AUTO);
    configPersistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString(), workspace);

    final DestinationConnection destinationConnection = new DestinationConnection()
        .withDestinationId(connectionId)
        .withWorkspaceId(workspaceId)
        .withName(CANNOT_BE_NULL)
        .withDestinationDefinitionId(destination.getDestinationDefinitionId());
    configPersistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, connectionId.toString(), destinationConnection);
  }

  void writeDestinations(final ConfigPersistence configPersistence, final List<StandardDestinationDefinition> destinations)
      throws Exception {
    final Map<String, StandardDestinationDefinition> destinationsByID = destinations.stream()
        .collect(Collectors.toMap(destinationDefinition -> destinationDefinition.getDestinationDefinitionId().toString(), Function.identity()));
    configPersistence.writeConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destinationsByID);
  }

  void deleteDestination(final ConfigPersistence configPersistence, final StandardDestinationDefinition destination)
      throws Exception {
    configPersistence.deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString());
  }

  protected Map<String, Set<JsonNode>> getMapWithSet(final Map<String, Stream<JsonNode>> input) {
    return input.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        e -> e.getValue().collect(Collectors.toSet())));
  }

  // assertEquals cannot correctly check the equality of two maps with stream values,
  // so streams are converted to sets before being compared.
  protected void assertSameConfigDump(final Map<String, Stream<JsonNode>> expected, final Map<String, Stream<JsonNode>> actual) {
    assertEquals(getMapWithSet(expected), getMapWithSet(actual));
  }

  protected void assertRecordCount(final int expectedCount, final Table table) throws Exception {
    final Result<Record1<Integer>> recordCount = database.query(ctx -> ctx.select(count(asterisk())).from(table).fetch());
    assertEquals(expectedCount, recordCount.get(0).value1());
  }

  protected void assertHasSource(final StandardSourceDefinition source) throws Exception {
    assertEquals(source, configPersistence
        .getConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, source.getSourceDefinitionId().toString(),
            StandardSourceDefinition.class));
  }

  protected void assertHasDestination(final StandardDestinationDefinition destination) throws Exception {
    assertEquals(destination, configPersistence
        .getConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destination.getDestinationDefinitionId().toString(),
            StandardDestinationDefinition.class));
  }

}
