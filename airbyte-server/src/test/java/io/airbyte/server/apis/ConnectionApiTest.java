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
import java.util.HashSet;
import javax.validation.ConstraintViolationException;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

@MicronautTest
@Requires(property = "mockito.test.enabled",
          defaultValue = StringUtils.TRUE,
          value = StringUtils.TRUE)
@Requires(env = {Environment.TEST})
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class ConnectionApiTest extends BaseControllerTest {

  @Test
  void testCreateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(connectionsHandler.createConnection(Mockito.any()))
        .thenReturn(new ConnectionRead())
        .thenThrow(new ConstraintViolationException(new HashSet<>()));
    final String path = "/api/v1/connections/create";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionCreate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionCreate())),
        HttpStatus.BAD_REQUEST);
  }

  @Test
  void testUpdateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(connectionsHandler.updateConnection(Mockito.any()))
        .thenReturn(new ConnectionRead())
        .thenThrow(new ConstraintViolationException(new HashSet<>()))
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/connections/update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionUpdate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionUpdate())),
        HttpStatus.BAD_REQUEST);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionUpdate())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListConnectionsForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(connectionsHandler.listConnectionsForWorkspace(Mockito.any()))
        .thenReturn(new ConnectionReadList())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/connections/list";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListAllConnectionsForWorkspace() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(connectionsHandler.listAllConnectionsForWorkspace(Mockito.any()))
        .thenReturn(new ConnectionReadList())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/connections/list_all";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testSearchConnections() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(connectionsHandler.searchConnections(Mockito.any()))
        .thenReturn(new ConnectionReadList())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/connections/search";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionSearch())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionSearch())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(connectionsHandler.getConnection(Mockito.any()))
        .thenReturn(new ConnectionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/connections/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testDeleteConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doNothing()
        .doThrow(new ConfigNotFoundException("", ""))
        .when(connectionsHandler).deleteConnection(Mockito.any());

    final String path = "/api/v1/connections/delete";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.NO_CONTENT);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testSyncConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(schedulerHandler.syncConnection(Mockito.any()))
        .thenReturn(new JobInfoRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/connections/sync";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testResetConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(schedulerHandler.resetConnection(Mockito.any()))
        .thenReturn(new JobInfoRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/connections/reset";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

}
