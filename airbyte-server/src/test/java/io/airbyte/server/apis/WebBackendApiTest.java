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
class WebBackendApiTest extends BaseControllerTest {

  @Test
  void testGetStateType() throws IOException {
    Mockito.when(webBackendConnectionsHandler.getStateType(Mockito.any()))
        .thenReturn(ConnectionStateType.STREAM);
    final String path = "/api/v1/web_backend/state/get_type";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testWebBackendCheckUpdates() {
    Mockito.when(webBackendCheckUpdatesHandler.checkUpdates())
        .thenReturn(new WebBackendCheckUpdatesRead());
    final String path = "/api/v1/web_backend/check_updates";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testWebBackendCreateConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(webBackendConnectionsHandler.webBackendCreateConnection(Mockito.any()))
        .thenReturn(new WebBackendConnectionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/web_backend/connections/create";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testWebBackendGetConnection() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(webBackendConnectionsHandler.webBackendGetConnection(Mockito.any()))
        .thenReturn(new WebBackendConnectionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/web_backend/connections/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testWebBackendGetWorkspaceState() throws IOException {
    Mockito.when(webBackendConnectionsHandler.getWorkspaceState(Mockito.any()))
        .thenReturn(new WebBackendWorkspaceStateResult());
    final String path = "/api/v1/web_backend/workspace/state";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testWebBackendListConnectionsForWorkspace() throws IOException {
    Mockito.when(webBackendConnectionsHandler.webBackendListConnectionsForWorkspace(Mockito.any()))
        .thenReturn(new WebBackendConnectionReadList());
    final String path = "/api/v1/web_backend/connections/list";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testWebBackendListGeographies() {
    Mockito.when(webBackendGeographiesHandler.listGeographiesOSS())
        .thenReturn(new WebBackendGeographiesListResult());
    final String path = "/api/v1/web_backend/geographies/list";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
  }

  @Test
  void testWebBackendUpdateConnection() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(webBackendConnectionsHandler.webBackendUpdateConnection(Mockito.any()))
        .thenReturn(new WebBackendConnectionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/web_backend/connections/update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new SourceDefinitionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

}
