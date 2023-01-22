/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.Geography;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.ReleaseStage;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;

@SuppressWarnings({"PMD.LongVariable", "PMD.AvoidInstantiatingObjectsInLoops"})
class WorkspacePersistenceTest extends BaseConfigDatabaseTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID = UUID.randomUUID();
  private static final UUID SOURCE_ID = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_ID = UUID.randomUUID();
  private static final JsonNode CONFIG = Jsons.jsonNode(ImmutableMap.of("key-a", "value-a"));

  private ConfigRepository configRepository;

  @BeforeEach
  void setup() {
    configRepository = spy(new ConfigRepository(
        database,
        new ActorDefinitionMigrator(new ExceptionWrappingDatabase(database)),
        null));
  }

  @Test
  void testGetWorkspace() throws ConfigNotFoundException, IOException, JsonValidationException {
    configRepository.writeStandardWorkspaceNoSecrets(createBaseStandardWorkspace().withWorkspaceId(UUID.randomUUID()));
    assertReturnsWorkspace(createBaseStandardWorkspace());
  }

  @Test
  void testWorkspaceWithNullTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(createBaseStandardWorkspace());
  }

  @Test
  void testWorkspaceWithFalseTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(createBaseStandardWorkspace().withTombstone(false));
  }

  @Test
  void testWorkspaceWithTrueTombstone() throws ConfigNotFoundException, IOException, JsonValidationException {
    assertReturnsWorkspace(createBaseStandardWorkspace().withTombstone(true));
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

  private static SourceConnection createBaseSource() {
    return new SourceConnection()
        .withSourceId(SOURCE_ID)
        .withSourceDefinitionId(SOURCE_DEFINITION_ID)
        .withName("source-a")
        .withTombstone(false)
        .withConfiguration(CONFIG)
        .withWorkspaceId(WORKSPACE_ID);
  }

  private static DestinationConnection createBaseDestination() {
    return new DestinationConnection()
        .withDestinationId(DESTINATION_ID)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID)
        .withName("destination-a")
        .withTombstone(false)
        .withConfiguration(CONFIG)
        .withWorkspaceId(WORKSPACE_ID);
  }

  private static StandardSourceDefinition createSourceDefinition(final ReleaseStage releaseStage) {
    return new StandardSourceDefinition()
        .withSourceDefinitionId(SOURCE_DEFINITION_ID)
        .withTombstone(false)
        .withName("source-definition-a")
        .withDockerRepository("dockerhub")
        .withDockerImageTag("some-tag")
        .withReleaseStage(releaseStage);
  }

  private static StandardDestinationDefinition createDestinationDefinition(final StandardDestinationDefinition.ReleaseStage releaseStage) {
    return new StandardDestinationDefinition()
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID)
        .withTombstone(false)
        .withName("destination-definition-a")
        .withDockerRepository("dockerhub")
        .withDockerImageTag("some-tag")
        .withReleaseStage(releaseStage);
  }

  private void persistConnectorsWithReleaseStages(
                                                  final ReleaseStage sourceReleaseStage,
                                                  final StandardDestinationDefinition.ReleaseStage destinationReleaseStage)
      throws JsonValidationException, IOException {

    configRepository.writeStandardSourceDefinition(createSourceDefinition(sourceReleaseStage));
    configRepository.writeStandardDestinationDefinition(createDestinationDefinition(destinationReleaseStage));
    configRepository.writeSourceConnectionNoSecrets(createBaseSource());
    configRepository.writeDestinationConnectionNoSecrets(createBaseDestination());
  }

  void assertReturnsWorkspace(final StandardWorkspace workspace) throws ConfigNotFoundException, IOException, JsonValidationException {
    configRepository.writeStandardWorkspaceNoSecrets(workspace);

    final StandardWorkspace expectedWorkspace = Jsons.clone(workspace);
    /*
     * tombstone defaults to false in the db, so if the passed in workspace does not have it set, we
     * expected the workspace returned from the db to have it set to false.
     */
    if (workspace.getTombstone() == null) {
      expectedWorkspace.withTombstone(false);
    }

    assertEquals(workspace, configRepository.getStandardWorkspaceNoSecrets(WORKSPACE_ID, true));
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  void testWorkspaceByConnectionId(final boolean isTombstone) throws ConfigNotFoundException, IOException, JsonValidationException {
    final UUID connectionId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final StandardSync mSync = new StandardSync()
        .withSourceId(sourceId);
    final SourceConnection mSourceConnection = new SourceConnection()
        .withWorkspaceId(WORKSPACE_ID);
    final StandardWorkspace mWorkflow = new StandardWorkspace()
        .withWorkspaceId(WORKSPACE_ID);

    doReturn(mSync)
        .when(configRepository)
        .getStandardSync(connectionId);
    doReturn(mSourceConnection)
        .when(configRepository)
        .getSourceConnection(sourceId);
    doReturn(mWorkflow)
        .when(configRepository)
        .getStandardWorkspaceNoSecrets(WORKSPACE_ID, isTombstone);

    configRepository.getStandardWorkspaceFromConnection(connectionId, isTombstone);

    verify(configRepository).getStandardWorkspaceNoSecrets(WORKSPACE_ID, isTombstone);
  }

  @Test
  void testUpdateFeedback() throws JsonValidationException, ConfigNotFoundException, IOException {
    final StandardWorkspace workspace = createBaseStandardWorkspace();

    configRepository.writeStandardWorkspaceNoSecrets(workspace);

    assertFalse(MoreBooleans.isTruthy(configRepository.getStandardWorkspaceNoSecrets(workspace.getWorkspaceId(), false).getFeedbackDone()));
    configRepository.setFeedback(workspace.getWorkspaceId());
    assertTrue(configRepository.getStandardWorkspaceNoSecrets(workspace.getWorkspaceId(), false).getFeedbackDone());
  }

  @Test
  void testWorkspaceHasAlphaOrBetaConnector() throws JsonValidationException, IOException {
    final StandardWorkspace workspace = createBaseStandardWorkspace();

    configRepository.writeStandardWorkspaceNoSecrets(workspace);

    persistConnectorsWithReleaseStages(ReleaseStage.GENERALLY_AVAILABLE, StandardDestinationDefinition.ReleaseStage.GENERALLY_AVAILABLE);
    assertFalse(configRepository.getWorkspaceHasAlphaOrBetaConnector(WORKSPACE_ID));

    persistConnectorsWithReleaseStages(ReleaseStage.ALPHA, StandardDestinationDefinition.ReleaseStage.GENERALLY_AVAILABLE);
    assertTrue(configRepository.getWorkspaceHasAlphaOrBetaConnector(WORKSPACE_ID));

    persistConnectorsWithReleaseStages(ReleaseStage.GENERALLY_AVAILABLE, StandardDestinationDefinition.ReleaseStage.BETA);
    assertTrue(configRepository.getWorkspaceHasAlphaOrBetaConnector(WORKSPACE_ID));

    persistConnectorsWithReleaseStages(ReleaseStage.CUSTOM, StandardDestinationDefinition.ReleaseStage.CUSTOM);
    assertFalse(configRepository.getWorkspaceHasAlphaOrBetaConnector(WORKSPACE_ID));
  }

}
