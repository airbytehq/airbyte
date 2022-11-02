/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class ActorDefinitionPersistenceTest extends BaseConfigDatabaseTest {

  private static final UUID SOURCE_DEFINITION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID = UUID.randomUUID();

  private ConfigRepository configRepository;
  private StandardSyncPersistence standardSyncPersistence;

  @BeforeEach
  void setup() throws SQLException {
    truncateAllTables();

    standardSyncPersistence = mock(StandardSyncPersistence.class);
    configRepository = spy(new ConfigRepository(
        database,
        new ActorDefinitionMigrator(new ExceptionWrappingDatabase(database)),
        standardSyncPersistence));
  }

  @Test
  void testSourceDefinitionWithNullTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsSrcDef(createBaseSourceDef());
  }

  @Test
  void testSourceDefinitionWithTrueTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsSrcDef(createBaseSourceDef().withTombstone(true));
  }

  @Test
  void testSourceDefinitionWithFalseTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsSrcDef(createBaseSourceDef().withTombstone(false));
  }

  void assertReturnsSrcDef(final StandardSourceDefinition srcDef) throws ConfigNotFoundException, IOException, JsonValidationException {
    configRepository.writeStandardSourceDefinition(srcDef);
    assertEquals(srcDef, configRepository.getStandardSourceDefinition(srcDef.getSourceDefinitionId()));
  }

  @SuppressWarnings("SameParameterValue")
  private static SourceConnection createSource(final UUID sourceDefId) {
    return new SourceConnection()
        .withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceDefId);
  }

  @Test
  void testSourceDefinitionFromSource() throws JsonValidationException, ConfigNotFoundException, IOException {
    final SourceConnection source = createSource(SOURCE_DEFINITION_ID);

    doReturn(source)
        .when(configRepository)
        .getSourceConnection(source.getSourceId());

    configRepository.getSourceDefinitionFromSource(source.getSourceId());
    verify(configRepository).getStandardSourceDefinition(SOURCE_DEFINITION_ID);
  }

  @Test
  void testSourceDefinitionsFromConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID connectionId = UUID.randomUUID();

    final StandardSourceDefinition sourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID);

    final SourceConnection source = createSource(SOURCE_DEFINITION_ID);

    final StandardSync connection = new StandardSync()
        .withSourceId(source.getSourceId())
        .withConnectionId(connectionId);

    doReturn(sourceDefinition)
        .when(configRepository)
        .getStandardSourceDefinition(SOURCE_DEFINITION_ID);
    doReturn(source)
        .when(configRepository)
        .getSourceConnection(source.getSourceId());
    doReturn(connection)
        .when(configRepository)
        .getStandardSync(connectionId);

    configRepository.getSourceDefinitionFromSource(source.getSourceId());

    verify(configRepository).getStandardSourceDefinition(SOURCE_DEFINITION_ID);
  }

  @ParameterizedTest
  @ValueSource(ints = {0, 1, 2, 10})
  void testListStandardSourceDefsHandlesTombstoneSourceDefs(final int numSrcDefs) throws JsonValidationException, IOException {
    final List<StandardSourceDefinition> allSourceDefinitions = new ArrayList<>();
    final List<StandardSourceDefinition> notTombstoneSourceDefinitions = new ArrayList<>();
    for (int i = 0; i < numSrcDefs; i++) {
      final boolean isTombstone = i % 2 == 0; // every other is tombstone
      final StandardSourceDefinition sourceDefinition = createBaseSourceDef().withTombstone(isTombstone);
      allSourceDefinitions.add(sourceDefinition);
      if (!isTombstone) {
        notTombstoneSourceDefinitions.add(sourceDefinition);
      }
      configRepository.writeStandardSourceDefinition(sourceDefinition);
    }

    final List<StandardSourceDefinition> returnedSrcDefsWithoutTombstone = configRepository.listStandardSourceDefinitions(false);
    assertEquals(notTombstoneSourceDefinitions, returnedSrcDefsWithoutTombstone);

    final List<StandardSourceDefinition> returnedSrcDefsWithTombstone = configRepository.listStandardSourceDefinitions(true);
    assertEquals(allSourceDefinitions, returnedSrcDefsWithTombstone);
  }

  private static StandardSourceDefinition createBaseSourceDef() {
    final UUID id = UUID.randomUUID();

    return new StandardSourceDefinition()
        .withName("source-def-" + id)
        .withDockerRepository("source-image-" + id)
        .withDockerImageTag("0.0.1")
        .withSourceDefinitionId(id)
        .withProtocolVersion("0.2.0")
        .withTombstone(false);
  }

  private static StandardDestinationDefinition createBaseDestDef() {
    final UUID id = UUID.randomUUID();

    return new StandardDestinationDefinition()
        .withName("source-def-" + id)
        .withDockerRepository("source-image-" + id)
        .withDockerImageTag("0.0.1")
        .withDestinationDefinitionId(id)
        .withProtocolVersion("0.2.0")
        .withTombstone(false);
  }

  // todo add test for protocol version behavior
  @Test
  void testListDestinationDefinitionsWithVersion() throws JsonValidationException, IOException {
    final List<StandardDestinationDefinition> allDestDefs = List.of(
        createBaseDestDef().withProtocolVersion(null),
        createBaseDestDef().withProtocolVersion(null).withSpec(new ConnectorSpecification().withProtocolVersion("0.3.1")),
        // We expect the protocol version to be in the ConnectorSpec, so we'll override regardless.
        createBaseDestDef().withProtocolVersion("0.4.0").withSpec(new ConnectorSpecification().withProtocolVersion("0.4.1")),
        createBaseDestDef().withProtocolVersion("0.5.0").withSpec(new ConnectorSpecification()));

    for (final StandardDestinationDefinition destDef : allDestDefs) {
      configRepository.writeStandardDestinationDefinition(destDef);
    }

    final List<StandardDestinationDefinition> destinationDefinitions = configRepository.listStandardDestinationDefinitions(false);
    final List<String> protocolVersions = destinationDefinitions.stream().map(StandardDestinationDefinition::getProtocolVersion).toList();
    assertEquals(
        List.of(
            AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION.serialize(),
            "0.3.1",
            "0.4.1",
            AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION.serialize()),
        protocolVersions);
  }

  @Test
  void testListSourceDefinitionsWithVersion() throws JsonValidationException, IOException {
    final List<StandardSourceDefinition> allSrcDefs = List.of(
        createBaseSourceDef().withProtocolVersion(null),
        createBaseSourceDef().withProtocolVersion(null).withSpec(new ConnectorSpecification().withProtocolVersion("0.6.0")),
        // We expect the protocol version to be in the ConnectorSpec, so we'll override regardless.
        createBaseSourceDef().withProtocolVersion("0.7.0").withSpec(new ConnectorSpecification().withProtocolVersion("0.7.1")),
        createBaseSourceDef().withProtocolVersion("0.8.0").withSpec(new ConnectorSpecification()));

    for (final StandardSourceDefinition srcDef : allSrcDefs) {
      configRepository.writeStandardSourceDefinition(srcDef);
    }

    final List<StandardSourceDefinition> sourceDefinitions = configRepository.listStandardSourceDefinitions(false);
    final List<String> protocolVersions = sourceDefinitions.stream().map(StandardSourceDefinition::getProtocolVersion).toList();
    assertEquals(
        List.of(
            AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION.serialize(),
            "0.6.0",
            "0.7.1",
            AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION.serialize()),
        protocolVersions);
  }

  @Test
  void testDestinationDefinitionWithNullTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsDestDef(createBaseDestDef());
  }

  @Test
  void testDestinationDefinitionWithTrueTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsDestDef(createBaseDestDef().withTombstone(true));
  }

  @Test
  void testDestinationDefinitionWithFalseTombstone() throws JsonValidationException, ConfigNotFoundException, IOException {
    assertReturnsDestDef(createBaseDestDef().withTombstone(false));
  }

  void assertReturnsDestDef(final StandardDestinationDefinition destDef) throws ConfigNotFoundException, IOException, JsonValidationException {
    configRepository.writeStandardDestinationDefinition(destDef);
    assertEquals(destDef, configRepository.getStandardDestinationDefinition(destDef.getDestinationDefinitionId()));
  }

  @SuppressWarnings("SameParameterValue")
  private static DestinationConnection createDest(final UUID destDefId) {
    return new DestinationConnection()
        .withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destDefId);
  }

  @Test
  void testDestinationDefinitionFromDestination() throws JsonValidationException, ConfigNotFoundException, IOException {

    final DestinationConnection destination = createDest(DESTINATION_DEFINITION_ID);

    doReturn(destination)
        .when(configRepository)
        .getDestinationConnection(destination.getDestinationId());

    configRepository.getDestinationDefinitionFromDestination(destination.getDestinationId());
    verify(configRepository).getStandardDestinationDefinition(DESTINATION_DEFINITION_ID);
  }

  @Test
  void testDestinationDefinitionsFromConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final UUID connectionId = UUID.randomUUID();

    final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID);

    final DestinationConnection destination = createDest(DESTINATION_DEFINITION_ID);

    final StandardSync connection = new StandardSync()
        .withDestinationId(destination.getDestinationId())
        .withConnectionId(connectionId);

    doReturn(destinationDefinition)
        .when(configRepository)
        .getStandardDestinationDefinition(DESTINATION_DEFINITION_ID);
    doReturn(destination)
        .when(configRepository)
        .getDestinationConnection(destination.getDestinationId());
    doReturn(connection)
        .when(configRepository)
        .getStandardSync(connectionId);

    configRepository.getDestinationDefinitionFromDestination(destination.getDestinationId());

    verify(configRepository).getStandardDestinationDefinition(DESTINATION_DEFINITION_ID);
  }

  @ParameterizedTest
  @ValueSource(ints = {0, 1, 2, 10})
  void testListStandardDestDefsHandlesTombstoneDestDefs(final int numDestinationDefinitions) throws JsonValidationException, IOException {
    final List<StandardDestinationDefinition> allDestinationDefinitions = new ArrayList<>();
    final List<StandardDestinationDefinition> notTombstoneDestinationDefinitions = new ArrayList<>();
    for (int i = 0; i < numDestinationDefinitions; i++) {
      final boolean isTombstone = i % 2 == 0; // every other is tombstone
      final StandardDestinationDefinition destinationDefinition = createBaseDestDef().withTombstone(isTombstone);
      allDestinationDefinitions.add(destinationDefinition);
      if (!isTombstone) {
        notTombstoneDestinationDefinitions.add(destinationDefinition);
      }
      configRepository.writeStandardDestinationDefinition(destinationDefinition);
    }

    final List<StandardDestinationDefinition> returnedDestDefsWithoutTombstone = configRepository.listStandardDestinationDefinitions(false);
    assertEquals(notTombstoneDestinationDefinitions, returnedDestDefsWithoutTombstone);

    final List<StandardDestinationDefinition> returnedDestDefsWithTombstone = configRepository.listStandardDestinationDefinitions(true);
    assertEquals(allDestinationDefinitions, returnedDestDefsWithTombstone);
  }

}
