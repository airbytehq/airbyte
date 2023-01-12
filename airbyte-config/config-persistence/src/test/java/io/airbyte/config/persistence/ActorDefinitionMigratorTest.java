/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.config.ConfigSchema.STANDARD_DESTINATION_DEFINITION;
import static io.airbyte.config.ConfigSchema.STANDARD_SOURCE_DEFINITION;
import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.ReleaseStage;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.persistence.ActorDefinitionMigrator.ConnectorInfo;
import io.airbyte.db.ExceptionWrappingDatabase;
import java.sql.SQLException;
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ActorDefinitionMigratorTest extends BaseConfigDatabaseTest {

  public static final String DEFAULT_PROTOCOL_VERSION = "0.2.0";
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
      .withDockerRepository("airbyte/custom")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withSourceType(SourceType.DATABASE)
      .withCustom(true)
      .withReleaseStage(ReleaseStage.CUSTOM)
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
      .withDockerRepository("airbyte/custom")
      .withDockerImageTag("0.3.11")
      .withDocumentationUrl("https://docs.airbyte.io/integrations/sources/postgres")
      .withIcon("postgresql.svg")
      .withCustom(true)
      .withReleaseStage(StandardDestinationDefinition.ReleaseStage.CUSTOM)
      .withTombstone(false);

  private ActorDefinitionMigrator migrator;
  private ConfigRepository configRepository;

  @BeforeEach
  void setup() throws SQLException {
    truncateAllTables();

    migrator = new ActorDefinitionMigrator(new ExceptionWrappingDatabase(database));
    configRepository = new ConfigRepository(database, migrator, null);
  }

  private void writeSource(final StandardSourceDefinition source) throws Exception {
    configRepository.writeStandardSourceDefinition(source);
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
    writeSource(source1);
    writeSource(source2);
    final Map<String, ConnectorInfo> result = database.query(ctx -> migrator.getConnectorRepositoryToInfoMap(ctx));
    // when there are duplicated connector definitions, the one with the latest version should be
    // retrieved
    assertEquals(newVersion, result.get(connectorRepository).dockerImageTag);
  }

  @Test
  void testHasNewVersion() {
    assertTrue(ActorDefinitionMigrator.hasNewVersion("0.1.99", DEFAULT_PROTOCOL_VERSION));
    assertFalse(ActorDefinitionMigrator.hasNewVersion("invalid_version", "0.1.2"));
  }

  @Test
  void testHasNewPatchVersion() {
    assertFalse(ActorDefinitionMigrator.hasNewPatchVersion("0.1.99", DEFAULT_PROTOCOL_VERSION));
    assertFalse(ActorDefinitionMigrator.hasNewPatchVersion("invalid_version", "0.3.1"));
    assertTrue(ActorDefinitionMigrator.hasNewPatchVersion("0.1.0", "0.1.3"));
  }

  @Test
  void testGetNewFields() {
    final JsonNode o1 = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode o2 = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3 }");
    assertEquals(Collections.emptySet(), ActorDefinitionMigrator.getNewFields(o1, o1));
    assertEquals(Collections.singleton("field3"), ActorDefinitionMigrator.getNewFields(o1, o2));
    assertEquals(Collections.singleton("field2"), ActorDefinitionMigrator.getNewFields(o2, o1));
  }

  @Test
  void testGetDefinitionWithNewFields() {
    final JsonNode current = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2 }");
    final JsonNode latest = Jsons.deserialize("{ \"field1\": 1, \"field3\": 3, \"field4\": 4 }");
    final Set<String> newFields = Set.of("field3");

    assertEquals(current, ActorDefinitionMigrator.getDefinitionWithNewFields(current, latest, Collections.emptySet()));

    final JsonNode currentWithNewFields = Jsons.deserialize("{ \"field1\": 1, \"field2\": 2, \"field3\": 3 }");
    assertEquals(currentWithNewFields, ActorDefinitionMigrator.getDefinitionWithNewFields(current, latest, newFields));
  }

  @Test
  void testActorDefinitionReleaseDate() throws Exception {
    final UUID definitionId = UUID.randomUUID();
    final String connectorRepository = "airbyte/test-connector";

    // when the record does not exist, it is inserted
    final StandardSourceDefinition sourceDef = new StandardSourceDefinition()
        .withSourceDefinitionId(definitionId)
        .withDockerRepository(connectorRepository)
        .withDockerImageTag("0.1.2")
        .withName("random-name")
        .withProtocolVersion(DEFAULT_PROTOCOL_VERSION)
        .withTombstone(false);
    writeSource(sourceDef);
    assertEquals(sourceDef, configRepository.getStandardSourceDefinition(sourceDef.getSourceDefinitionId()));
  }

  @Test
  void filterCustomSource() {
    final Map<String, ConnectorInfo> sourceMap = new HashMap<>();
    final String nonCustomKey = "non-custom";
    final String customKey = "custom";
    sourceMap.put(nonCustomKey, new ConnectorInfo("id", Jsons.jsonNode(SOURCE_POSTGRES)));
    sourceMap.put(customKey, new ConnectorInfo("id", Jsons.jsonNode(SOURCE_CUSTOM)));

    final Map<String, ConnectorInfo> filteredSrcMap = migrator.filterCustomConnector(sourceMap, STANDARD_SOURCE_DEFINITION);

    assertThat(filteredSrcMap).containsOnlyKeys(nonCustomKey);
  }

  @Test
  void filterCustomDestination() {
    final Map<String, ConnectorInfo> sourceMap = new HashMap<>();
    final String nonCustomKey = "non-custom";
    final String customKey = "custom";
    sourceMap.put(nonCustomKey, new ConnectorInfo("id", Jsons.jsonNode(DESTINATION_S3)));
    sourceMap.put(customKey, new ConnectorInfo("id", Jsons.jsonNode(DESTINATION_CUSTOM)));

    final Map<String, ConnectorInfo> filteredDestMap = migrator.filterCustomConnector(sourceMap, STANDARD_DESTINATION_DEFINITION);

    assertThat(filteredDestMap).containsOnlyKeys(nonCustomKey);
  }

}
