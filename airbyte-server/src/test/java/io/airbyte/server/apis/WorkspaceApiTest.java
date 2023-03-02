/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.SourceDefinitionIdRequestBody;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.WorkspaceRead;
import io.airbyte.api.model.generated.WorkspaceReadList;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.env.Environment;
import io.micronaut.core.util.StringUtils;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpStatus;
import io.micronaut.test.extensions.junit5.annotation.MicronautTest;
import java.io.IOException;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class WorkspaceApiTest extends BaseControllerTest {

  @Test
  void testCreateWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(workspacesHandler.createWorkspace(Mockito.any()))
        .thenReturn(new WorkspaceRead());
    final String path = "/api/v1/workspaces/create";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testDeleteWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doNothing()
        .doThrow(new ConfigNotFoundException("", ""))
        .when(workspacesHandler).deleteWorkspace(Mockito.any());
    final String path = "/api/v1/workspaces/delete";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.NO_CONTENT);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(workspacesHandler.getWorkspace(Mockito.any()))
        .thenReturn(new WorkspaceRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/workspaces/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetBySlugWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(workspacesHandler.getWorkspaceBySlug(Mockito.any()))
        .thenReturn(new WorkspaceRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/workspaces/get_by_slug";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(workspacesHandler.listWorkspaces())
        .thenReturn(new WorkspaceReadList());
    final String path = "/api/v1/workspaces/list";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testUpdateWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(workspacesHandler.updateWorkspace(Mockito.any()))
        .thenReturn(new WorkspaceRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/workspaces/update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testUpdateWorkspaceFeedback() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doNothing()
        .doThrow(new ConfigNotFoundException("", ""))
        .when(workspacesHandler).setFeedbackDone(Mockito.any());
    final String path = "/api/v1/workspaces/tag_feedback_status_as_done";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testUpdateWorkspaceName() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(workspacesHandler.updateWorkspaceName(Mockito.any()))
        .thenReturn(new WorkspaceRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/workspaces/update_name";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetWorkspaceByConnectionId() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(workspacesHandler.getWorkspaceByConnectionId(Mockito.any()))
        .thenReturn(new WorkspaceRead());
    final String path = "/api/v1/workspaces/get_by_connection_id";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

}
