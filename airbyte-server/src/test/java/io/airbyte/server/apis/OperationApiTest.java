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
class OperationApiTest extends BaseControllerTest {

  @Test
  void testCheckOperation() {
    Mockito.when(operationsHandler.checkOperation(Mockito.any()))
        .thenReturn(new CheckOperationRead());
    final String path = "/api/v1/operations/check";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new OperatorConfiguration())),
        HttpStatus.OK);
  }

  @Test
  void testCreateOperation() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(operationsHandler.createOperation(Mockito.any()))
        .thenReturn(new OperationRead());
    final String path = "/api/v1/operations/create";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new OperationCreate())),
        HttpStatus.OK);
  }

  @Test
  void testDeleteOperation() throws IOException {
    Mockito.doNothing()
        .when(operationsHandler).deleteOperation(Mockito.any());

    final String path = "/api/v1/operations/delete";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new OperationIdRequestBody())),
        HttpStatus.NO_CONTENT);
  }

  @Test
  void testGetOperation() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(operationsHandler.getOperation(Mockito.any()))
        .thenReturn(new OperationRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/operations/get";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new OperationIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new OperationIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testListOperationsForConnection() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(operationsHandler.listOperationsForConnection(Mockito.any()))
        .thenReturn(new OperationReadList())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/operations/list";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new ConnectionIdRequestBody())),
        HttpStatus.NOT_FOUND);
  }

  @Test
  void testUpdateOperation() throws IOException, JsonValidationException, ConfigNotFoundException {
    Mockito.when(operationsHandler.updateOperation(Mockito.any()))
        .thenReturn(new OperationRead())
        .thenThrow(new ConfigNotFoundException("", ""));
    final String path = "/api/v1/operations/update";
    testEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new OperationUpdate())),
        HttpStatus.OK);
    testErrorEndpointStatus(
        HttpRequest.POST(path, Jsons.serialize(new OperationUpdate())),
        HttpStatus.NOT_FOUND);
  }

}
