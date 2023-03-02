/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.model.generated.*;
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
class SourceDefinitionApiTest extends BaseControllerTest {

  @Test
  void testCreateCustomSourceDefinition() throws IOException {
    Mockito.when(sourceDefinitionsHandler.createCustomSourceDefinition(Mockito.any()))
        .thenReturn(new SourceDefinitionRead());
    final String path = "/api/v1/source_definitions/create_custom";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testDeleteSourceDefinition() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doNothing()
        .doThrow(new ConfigNotFoundException("", ""))
        .when(sourceDefinitionsHandler).deleteSourceDefinition(Mockito.any());

    final String path = "/api/v1/source_definitions/delete";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NO_CONTENT);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetSourceDefinition() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(sourceDefinitionsHandler.getSourceDefinition(Mockito.any()))
        .thenReturn(new SourceDefinitionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/source_definitions/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetSourceDefinitionForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(sourceDefinitionsHandler.getSourceDefinitionForWorkspace(Mockito.any()))
        .thenReturn(new SourceDefinitionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/source_definitions/get_for_workspace";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdWithWorkspaceId())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdWithWorkspaceId())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGrantSourceDefinitionToWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(sourceDefinitionsHandler.grantSourceDefinitionToWorkspace(Mockito.any()))
        .thenReturn(new PrivateSourceDefinitionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/source_definitions/grant_definition";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdWithWorkspaceId())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdWithWorkspaceId())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListLatestSourceDefinitions() {
    Mockito.when(sourceDefinitionsHandler.listLatestSourceDefinitions())
        .thenReturn(new SourceDefinitionReadList());
    final String path = "/api/v1/source_definitions/list_latest";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdWithWorkspaceId())),
        HttpStatus.OK);
  }

  @Test
  void testListPrivateSourceDefinitions() throws IOException {
    Mockito.when(sourceDefinitionsHandler.listPrivateSourceDefinitions(Mockito.any()))
        .thenReturn(new PrivateSourceDefinitionReadList());
    final String path = "/api/v1/source_definitions/list_private";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testListSourceDefinitions() throws JsonValidationException, IOException {
    Mockito.when(sourceDefinitionsHandler.listSourceDefinitions())
        .thenReturn(new SourceDefinitionReadList());
    final String path = "/api/v1/source_definitions/list";
    testEndpointStatus(
        HttpRequest.POST(path, ""),
        HttpStatus.OK);
  }

  @Test
  void testListSourceDefinitionsForWorkspace() throws IOException {
    Mockito.when(sourceDefinitionsHandler.listSourceDefinitionsForWorkspace(Mockito.any()))
        .thenReturn(new SourceDefinitionReadList());
    final String path = "/api/v1/source_definitions/list_for_workspace";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testRevokeSourceDefinitionFromWorkspace() throws IOException {
    Mockito.doNothing()
        .when(sourceDefinitionsHandler).revokeSourceDefinitionFromWorkspace(Mockito.any());

    final String path = "/api/v1/source_definitions/revoke_definition";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdWithWorkspaceId())),
        HttpStatus.NO_CONTENT);
  }

  @Test
  void testUpdateSourceDefinition() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(sourceDefinitionsHandler.updateSourceDefinition(Mockito.any()))
        .thenReturn(new SourceDefinitionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/source_definitions/update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionUpdate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionUpdate())),
        HttpStatus.NOT_FOUND);
  }

}
