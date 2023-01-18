/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.OperationApi;
import io.airbyte.api.model.generated.*;
import io.airbyte.server.handlers.OperationsHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/operations")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class OperationApiController implements OperationApi {

  private final OperationsHandler operationsHandler;

  public OperationApiController(final OperationsHandler operationsHandler) {
    this.operationsHandler = operationsHandler;
  }

  @Post("/check")
  @Override
  public CheckOperationRead checkOperation(@Body final OperatorConfiguration operatorConfiguration) {
    return ApiHelper.execute(() -> operationsHandler.checkOperation(operatorConfiguration));
  }

  @Post("/create")
  @Override
  public OperationRead createOperation(@Body final OperationCreate operationCreate) {
    return ApiHelper.execute(() -> operationsHandler.createOperation(operationCreate));
  }

  @Post("/delete")
  @Override
  public void deleteOperation(@Body final OperationIdRequestBody operationIdRequestBody) {
    ApiHelper.execute(() -> {
      operationsHandler.deleteOperation(operationIdRequestBody);
      return null;
    });
  }

  @Post("/get")
  @Override
  public OperationRead getOperation(@Body final OperationIdRequestBody operationIdRequestBody) {
    return ApiHelper.execute(() -> operationsHandler.getOperation(operationIdRequestBody));
  }

  @Post("/list")
  @Override
  public OperationReadList listOperationsForConnection(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> operationsHandler.listOperationsForConnection(connectionIdRequestBody));
  }

  @Post("/update")
  @Override
  public OperationRead updateOperation(@Body final OperationUpdate operationUpdate) {
    return ApiHelper.execute(() -> operationsHandler.updateOperation(operationUpdate));
  }

}
