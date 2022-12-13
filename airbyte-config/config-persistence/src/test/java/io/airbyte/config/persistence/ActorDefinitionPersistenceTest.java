/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;

import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.Geography;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardWorkspace;
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

  private static final UUID WORKSPACE_ID = UUID.randomUUID();

  private ConfigRepository configRepository;

  @BeforeEach
  void setup() throws SQLException {
    truncateAllTables();

    configRepository = spy(new ConfigRepository(
        database,
        new ActorDefinitionMigrator(new ExceptionWrappingDatabase(database)),
        mock(StandardSyncPersistence.class)));
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

  private void assertReturnsSrcDef(final StandardSourceDefinition srcDef) throws ConfigNotFoundException, IOException, JsonValidationException {
    configRepository.writeStandardSourceDefinition(srcDef);
    assertEquals(srcDef, configRepository.getStandardSourceDefinition(srcDef.getSourceDefinitionId()));
  }

  @Test
  void testSourceDefinitionFromSource() throws JsonValidationException, IOException {
    final StandardWorkspace workspace = createBaseStandardWorkspace();
    final StandardSourceDefinition srcDef = createBaseSourceDef().withTombstone(false);
    final SourceConnection source = createSource(srcDef.getSourceDefinitionId(), workspace.getWorkspaceId());
    configRepository.writeStandardWorkspaceNoSecrets(workspace);
    configRepository.writeStandardSourceDefinition(srcDef);
    configRepository.writeSourceConnectionNoSecrets(source);

    assertEquals(srcDef, configRepository.getSourceDefinitionFromSource(source.getSourceId()));
  }

  @Test
  void testSourceDefinitionsFromConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = createBaseStandardWorkspace();
    final StandardSourceDefinition srcDef = createBaseSourceDef().withTombstone(false);
    final SourceConnection source = createSource(srcDef.getSourceDefinitionId(), workspace.getWorkspaceId());
    configRepository.writeStandardWorkspaceNoSecrets(workspace);
    configRepository.writeStandardSourceDefinition(srcDef);
    configRepository.writeSourceConnectionNoSecrets(source);

    final UUID connectionId = UUID.randomUUID();
    final StandardSync connection = new StandardSync()
        .withSourceId(source.getSourceId())
        .withConnectionId(connectionId);

    // todo (cgardens) - remove this mock and replace with record in db
    doReturn(connection)
        .when(configRepository)
        .getStandardSync(connectionId);

    assertEquals(srcDef, configRepository.getSourceDefinitionFromConnection(connectionId));
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

  // todo add test for protocol version behavior
  @Test
  void testListDestinationDefinitionsWithVersion() throws JsonValidationException, IOException {
    final List<StandardDestinationDefinition> allDestDefs = List.of(
        createBaseDestDef().withProtocolVersion(null),
        createBaseDestDef().withProtocolVersion(null).withSpec(new ConnectorSpecification().withProtocolVersion("0.3.1")),
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
            AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION.serialize(),
            "0.4.0",
            "0.5.0"),
        protocolVersions);
  }

  @Test
  void testListSourceDefinitionsWithVersion() throws JsonValidationException, IOException {
    final List<StandardSourceDefinition> allSrcDefs = List.of(
        createBaseSourceDef().withProtocolVersion(null),
        createBaseSourceDef().withProtocolVersion(null).withSpec(new ConnectorSpecification().withProtocolVersion("0.6.0")),
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
            AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION.serialize(),
            "0.7.0",
            "0.8.0"),
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

  @Test
  void testDestinationDefinitionFromDestination() throws JsonValidationException, IOException {
    final StandardWorkspace workspace = createBaseStandardWorkspace();
    final StandardDestinationDefinition destDef = createBaseDestDef().withTombstone(false);
    final DestinationConnection dest = createDest(destDef.getDestinationDefinitionId(), workspace.getWorkspaceId());
    configRepository.writeStandardWorkspaceNoSecrets(workspace);
    configRepository.writeStandardDestinationDefinition(destDef);
    configRepository.writeDestinationConnectionNoSecrets(dest);

    assertEquals(destDef, configRepository.getDestinationDefinitionFromDestination(dest.getDestinationId()));
  }

  @Test
  void testDestinationDefinitionsFromConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = createBaseStandardWorkspace();
    final StandardDestinationDefinition destDef = createBaseDestDef().withTombstone(false);
    final DestinationConnection dest = createDest(destDef.getDestinationDefinitionId(), workspace.getWorkspaceId());
    configRepository.writeStandardWorkspaceNoSecrets(workspace);
    configRepository.writeStandardDestinationDefinition(destDef);
    configRepository.writeDestinationConnectionNoSecrets(dest);

    final UUID connectionId = UUID.randomUUID();
    final StandardSync connection = new StandardSync()
        .withDestinationId(dest.getDestinationId())
        .withConnectionId(connectionId);

    // todo (cgardens) - remove this mock and replace with record in db
    doReturn(connection)
        .when(configRepository)
        .getStandardSync(connectionId);

    assertEquals(destDef, configRepository.getDestinationDefinitionFromConnection(connectionId));
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

  @SuppressWarnings("SameParameterValue")
  private static SourceConnection createSource(final UUID sourceDefId, final UUID workspaceId) {
    return new SourceConnection()
        .withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceDefId)
        .withWorkspaceId(workspaceId)
        .withName("source");
  }

  @SuppressWarnings("SameParameterValue")
  private static DestinationConnection createDest(final UUID destDefId, final UUID workspaceId) {
    return new DestinationConnection()
        .withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destDefId)
        .withWorkspaceId(workspaceId)
        .withName("dest");
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

  private static StandardWorkspace createBaseStandardWorkspace() {
    return new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID)
        .withName("workspace-a")
        .withSlug("workspace-a-slug")
        .withInitialSetupComplete(false)
        .withTombstone(false)
        .withDefaultGeography(Geography.AUTO);
  }

}
