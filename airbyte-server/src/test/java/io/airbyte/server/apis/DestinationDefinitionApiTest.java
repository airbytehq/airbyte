/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import javax.ws.rs.NotFoundException;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class DestinationDefinitionApiTest extends BaseControllerTest {

  @Test
  void testCheckConnectionToDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.createCustomDestinationDefinition(Mockito.any()))
        .thenReturn(new DestinationDefinitionRead())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/create_custom";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new CustomDestinationDefinitionCreate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new CustomDestinationDefinitionCreate())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testDeleteDestinationDefinition() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doNothing()
        .doThrow(new NotFoundException())
        .when(destinationDefinitionsHandler).deleteDestinationDefinition(Mockito.any());
    final String path = "/api/v1/destination_definitions/delete";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdRequestBody())),
        HttpStatus.NO_CONTENT);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetDestinationDefinition() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.getDestinationDefinition(Mockito.any()))
        .thenReturn(new DestinationDefinitionRead())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetDestinationDefinitionForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.getDestinationDefinitionForWorkspace(Mockito.any()))
        .thenReturn(new DestinationDefinitionRead())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/get_for_workspace";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGrantDestinationDefinitionToWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.grantDestinationDefinitionToWorkspace(Mockito.any()))
        .thenReturn(new PrivateDestinationDefinitionRead())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/grant_definition";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdWithWorkspaceId())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdWithWorkspaceId())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListDestinationDefinitions() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.listDestinationDefinitions())
        .thenReturn(new DestinationDefinitionReadList())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/list";
    testEndpointStatus(
        HttpRequest.POST(path, ""),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, ""),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListDestinationDefinitionsForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.listDestinationDefinitionsForWorkspace(Mockito.any()))
        .thenReturn(new DestinationDefinitionReadList())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/list_for_workspace";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListLatestDestinationDefinitions() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.listLatestDestinationDefinitions())
        .thenReturn(new DestinationDefinitionReadList())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/list_latest";
    testEndpointStatus(
        HttpRequest.POST(path, ""),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, ""),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListPrivateDestinationDefinitions() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.listPrivateDestinationDefinitions(Mockito.any()))
        .thenReturn(new PrivateDestinationDefinitionReadList())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/list_private";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testRevokeDestinationDefinitionFromWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doNothing()
        .doThrow(new NotFoundException())
        .when(destinationDefinitionsHandler).revokeDestinationDefinitionFromWorkspace(Mockito.any());
    final String path = "/api/v1/destination_definitions/revoke_definition";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdWithWorkspaceId())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionIdWithWorkspaceId())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testUpdateDestinationDefinition() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationDefinitionsHandler.updateDestinationDefinition(Mockito.any()))
        .thenReturn(new DestinationDefinitionRead())
        .thenThrow(new NotFoundException());
    final String path = "/api/v1/destination_definitions/update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionUpdate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationDefinitionUpdate())),
        HttpStatus.NOT_FOUND);
  }

}
