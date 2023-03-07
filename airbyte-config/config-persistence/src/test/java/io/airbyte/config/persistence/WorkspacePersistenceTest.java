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

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.MoreBooleans;
import io.airbyte.config.Geography;
import io.airbyte.config.SourceConnection;
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

@SuppressWarnings({"PMD.LongVariable", "PMD.AvoidInstantiatingObjectsInLoops"})
class WorkspacePersistenceTest extends BaseConfigDatabaseTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();

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

}
