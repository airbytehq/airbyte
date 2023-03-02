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
class DestinationApiTest extends BaseControllerTest {

  @Test
  void testCheckConnectionToDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(schedulerHandler.checkDestinationConnectionFromDestinationId(Mockito.any()))
        .thenReturn(new CheckConnectionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destinations/check_connection";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testCheckConnectionToDestinationForUpdate() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(Mockito.any()))
        .thenReturn(new CheckConnectionRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destinations/check_connection_for_update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationUpdate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationUpdate())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testCloneDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationHandler.cloneDestination(Mockito.any()))
        .thenReturn(new DestinationRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destinations/clone";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationCloneRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationCloneRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testCreateDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationHandler.createDestination(Mockito.any()))
        .thenReturn(new DestinationRead())
        .thenThrow(new ConstraintViolationException(new HashSet<>()));
    final String path = "/api/v1/destinations/create";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationCreate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationCreate())),
        HttpStatus.BAD_REQUEST);
  }

  @Test
  void testDeleteDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.doNothing()
        .doThrow(new ConfigNotFoundException("", ""))
        .when(destinationHandler).deleteDestination(Mockito.any(DestinationIdRequestBody.class));

    final String path = "/api/v1/destinations/delete";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationIdRequestBody())),
        HttpStatus.NO_CONTENT);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testGetDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationHandler.getDestination(Mockito.any()))
        .thenReturn(new DestinationRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destinations/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationHandler.listDestinationsForWorkspace(Mockito.any()))
        .thenReturn(new DestinationReadList())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destinations/list";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new WorkspaceIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testSearchDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationHandler.searchDestinations(Mockito.any()))
        .thenReturn(new DestinationReadList())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destinations/search";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationSearch())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationSearch())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testUpdateDestination() throws JsonValidationException, ConfigNotFoundException, IOException {
    Mockito.when(destinationHandler.updateDestination(Mockito.any()))
        .thenReturn(new DestinationRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/destinations/update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationUpdate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new DestinationUpdate())),
        HttpStatus.NOT_FOUND);
  }

}
