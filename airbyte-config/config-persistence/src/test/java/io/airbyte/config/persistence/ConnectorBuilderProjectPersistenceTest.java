/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.config.ConnectorBuilderProject;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConnectorBuilderProjectPersistenceTest extends BaseConfigDatabaseTest {

  private ConfigRepository configRepository;
  private UUID mainWorkspace;

  private ConnectorBuilderProject project1;

  private ConnectorBuilderProject project2;

  @BeforeEach
  void beforeEach() throws Exception {
    truncateAllTables();
    configRepository = new ConfigRepository(database);
  }

  @Test
  void testRead() throws IOException {
    createBaseObjects();
    assertEquals(project1, configRepository.getConnectorBuilderProject(project1.getBuilderProjectId(), mainWorkspace).get());
  }

  @Test
  void testReadNotExists() throws IOException {
    final Optional<ConnectorBuilderProject> projectOptional = configRepository.getConnectorBuilderProject(UUID.randomUUID(), mainWorkspace);
    assertFalse(projectOptional.isPresent());
  }

  @Test
  void testList() throws IOException {
    createBaseObjects();

    // set draft to null because it won't be returned as part of listing call
    project1.setManifestDraft(null);
    project2.setManifestDraft(null);

    assertEquals(new ArrayList<>(
        Arrays.asList(project1, project2)), configRepository.getConnectorBuilderProjectsByWorkspace(mainWorkspace).toList());
  }

  @Test
  void testUpdate() throws IOException {
    createBaseObjects();
    project1.setName("Updated name");
    project1.setManifestDraft(new ObjectMapper().readTree("{}"));
    configRepository.writeBuilderProject(project1);
    assertEquals(project1, configRepository.getConnectorBuilderProject(project1.getBuilderProjectId(), mainWorkspace).get());
  }

  @Test
  void testDelete() throws IOException {
    createBaseObjects();

    final boolean deleted = configRepository.deleteBuilderProject(project1.getBuilderProjectId(), mainWorkspace);
    assertTrue(deleted);
    assertFalse(configRepository.getConnectorBuilderProject(project1.getBuilderProjectId(), mainWorkspace).isPresent());
    assertTrue(configRepository.getConnectorBuilderProject(project2.getBuilderProjectId(), mainWorkspace).isPresent());
  }

  private void createBaseObjects() throws IOException {
    mainWorkspace = UUID.randomUUID();
    final UUID workspaceId2 = UUID.randomUUID();

    project1 = createConnectorBuilderProject(mainWorkspace);
    project2 = createConnectorBuilderProject(mainWorkspace);

    // unreachable project, should not show up in listing
    createConnectorBuilderProject(workspaceId2);
  }

  private ConnectorBuilderProject createConnectorBuilderProject(final UUID workspace)
      throws IOException {
    final UUID projectId = UUID.randomUUID();
    final ConnectorBuilderProject project = new ConnectorBuilderProject()
        .withBuilderProjectId(projectId)
        .withName("project " + projectId)
        .withManifestDraft(new ObjectMapper().readTree("{\"the_id\": \"" + projectId + "\"}"))
        .withWorkspaceId(workspace);
    configRepository.writeBuilderProject(project);
    return project;
  }

}
