/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.atMostOnce;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.api.model.generated.ConnectorBuilderProjectDetails;
import io.airbyte.api.model.generated.ConnectorBuilderProjectIdWithWorkspaceId;
import io.airbyte.api.model.generated.ConnectorBuilderProjectWithWorkspaceId;
import io.airbyte.api.model.generated.ExistingConnectorBuilderProjectWithWorkspaceId;
import io.airbyte.config.ConnectorBuilderProject;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class ConnectorBuilderProjectsHandlerTest {

  private ConfigRepository configRepository;
  private ConnectorBuilderProjectsHandler connectorBuilderProjectsHandler;
  private WorkspaceHelper workspaceHelper;
  private Supplier<UUID> uuidSupplier;
  private UUID workspaceId;

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setUp() throws JsonProcessingException {
    configRepository = mock(ConfigRepository.class);
    uuidSupplier = mock(Supplier.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    workspaceId = UUID.randomUUID();

    connectorBuilderProjectsHandler = new ConnectorBuilderProjectsHandler(configRepository, workspaceHelper, uuidSupplier);
  }

  private ConnectorBuilderProject generateBuilderProject() throws JsonProcessingException {
    final UUID projectId = UUID.randomUUID();
    return new ConnectorBuilderProject().withBuilderProjectId(projectId).withWorkspaceId(workspaceId).withName("Test project")
        .withManifestDraft(new ObjectMapper().readTree("{\"test\": 123}"));
  }

  @Test
  @DisplayName("createConnectorBuilderProject should create a new project and return the id")
  void testCreateConnectorBuilderProject() throws IOException {
    final ConnectorBuilderProject project = generateBuilderProject();

    when(uuidSupplier.get()).thenReturn(project.getBuilderProjectId());

    final ConnectorBuilderProjectWithWorkspaceId create = new ConnectorBuilderProjectWithWorkspaceId()
        .builderProject(new ConnectorBuilderProjectDetails().name(project.getName())
            .draftManifest(new ObjectMapper().convertValue(project.getManifestDraft(), new TypeReference<Map<String, Object>>() {})))
        .workspaceId(workspaceId);

    final ConnectorBuilderProjectIdWithWorkspaceId response = connectorBuilderProjectsHandler.createConnectorBuilderProject(create);
    assertEquals(response.getBuilderProjectId(), project.getBuilderProjectId());
    assertEquals(response.getWorkspaceId(), project.getWorkspaceId());

    verify(configRepository, times(1))
        .writeBuilderProject(
            project);
  }

  @Test
  @DisplayName("updateConnectorBuilderProject should update an existing project and return the id")
  void testUpdateConnectorBuilderProject() throws IOException, JsonValidationException, ConfigNotFoundException {
    final ConnectorBuilderProject project = generateBuilderProject();

    when(workspaceHelper.getWorkspaceForConnectorBuilderProject(project.getBuilderProjectId())).thenReturn(workspaceId);

    final ExistingConnectorBuilderProjectWithWorkspaceId update = new ExistingConnectorBuilderProjectWithWorkspaceId()
        .builderProject(new ConnectorBuilderProjectDetails().name(project.getName())
            .draftManifest(new ObjectMapper().convertValue(project.getManifestDraft(), new TypeReference<Map<String, Object>>() {})))
        .workspaceId(workspaceId).builderProjectId(project.getBuilderProjectId());

    connectorBuilderProjectsHandler.updateConnectorBuilderProject(update);

    verify(uuidSupplier, never()).get();
    verify(configRepository, atMostOnce())
        .writeBuilderProject(
            project);
  }

  @Test
  @DisplayName("updateConnectorBuilderProject should validate whether the workspace does not match")
  void testUpdateConnectorBuilderProjectValidateWorkspace() throws IOException, JsonValidationException, ConfigNotFoundException {
    final ConnectorBuilderProject project = generateBuilderProject();
    final UUID wrongWorkspace = UUID.randomUUID();
    when(workspaceHelper.getWorkspaceForConnectorBuilderProject(project.getBuilderProjectId())).thenReturn(wrongWorkspace);

    final ExistingConnectorBuilderProjectWithWorkspaceId update = new ExistingConnectorBuilderProjectWithWorkspaceId()
        .builderProject(new ConnectorBuilderProjectDetails().name(project.getName())
            .draftManifest(new ObjectMapper().convertValue(project.getManifestDraft(), new TypeReference<Map<String, Object>>() {})))
        .workspaceId(workspaceId).builderProjectId(project.getBuilderProjectId());

    assertThrows(ConfigNotFoundException.class, () -> connectorBuilderProjectsHandler.updateConnectorBuilderProject(update));

    verify(configRepository, never()).writeBuilderProject(any(ConnectorBuilderProject.class));
  }

  @Test
  @DisplayName("deleteConnectorBuilderProject should validate whether the workspace does not match")
  void testDeleteConnectorBuilderProjectValidateWorkspace() throws IOException, JsonValidationException, ConfigNotFoundException {
    final ConnectorBuilderProject project = generateBuilderProject();
    final UUID wrongWorkspace = UUID.randomUUID();
    when(workspaceHelper.getWorkspaceForConnectorBuilderProject(project.getBuilderProjectId())).thenReturn(wrongWorkspace);

    assertThrows(ConfigNotFoundException.class, () -> connectorBuilderProjectsHandler.deleteConnectorBuilderProject(
        new ConnectorBuilderProjectIdWithWorkspaceId().builderProjectId(project.getBuilderProjectId()).workspaceId(workspaceId)));

    verify(configRepository, never()).deleteBuilderProject(any(UUID.class));
  }

  @Test
  @DisplayName("deleteConnectorBuilderProject should delete an existing project")
  void testDeleteConnectorBuilderProject() throws IOException, JsonValidationException, ConfigNotFoundException {
    final ConnectorBuilderProject project = generateBuilderProject();

    when(workspaceHelper.getWorkspaceForConnectorBuilderProject(project.getBuilderProjectId())).thenReturn(workspaceId);

    connectorBuilderProjectsHandler.deleteConnectorBuilderProject(
        new ConnectorBuilderProjectIdWithWorkspaceId().builderProjectId(project.getBuilderProjectId()).workspaceId(workspaceId));

    verify(uuidSupplier, never()).get();
    verify(configRepository, times(1))
        .deleteBuilderProject(
            project.getBuilderProjectId());
  }

}
