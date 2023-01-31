/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.AUTHENTICATED_USER;
import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;
import static io.airbyte.commons.auth.AuthRoleConstants.READER;

import io.airbyte.api.generated.OperationApi;
import io.airbyte.api.model.generated.CheckOperationRead;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.OperationCreate;
import io.airbyte.api.model.generated.OperationIdRequestBody;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperationReadList;
import io.airbyte.api.model.generated.OperationUpdate;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.commons.server.handlers.OperationsHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
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
  @Secured({AUTHENTICATED_USER})
  @Override
  public CheckOperationRead checkOperation(@Body final OperatorConfiguration operatorConfiguration) {
    return ApiHelper.execute(() -> operationsHandler.checkOperation(operatorConfiguration));
  }

  @Post("/create")
  @Override
  @Secured({EDITOR})
  public OperationRead createOperation(@Body final OperationCreate operationCreate) {
    return ApiHelper.execute(() -> operationsHandler.createOperation(operationCreate));
  }

  @Post("/delete")
  @Secured({EDITOR})
  @Override
  @Status(HttpStatus.NO_CONTENT)
  public void deleteOperation(@Body final OperationIdRequestBody operationIdRequestBody) {
    ApiHelper.execute(() -> {
      operationsHandler.deleteOperation(operationIdRequestBody);
      return null;
    });
  }

  @Post("/get")
  @Secured({READER})
  @Override
  public OperationRead getOperation(@Body final OperationIdRequestBody operationIdRequestBody) {
    return ApiHelper.execute(() -> operationsHandler.getOperation(operationIdRequestBody));
  }

  @Post("/list")
  @Secured({READER})
  @Override
  public OperationReadList listOperationsForConnection(@Body final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> operationsHandler.listOperationsForConnection(connectionIdRequestBody));
  }

  @Post("/update")
  @Secured({EDITOR})
  @Override
  public OperationRead updateOperation(@Body final OperationUpdate operationUpdate) {
    return ApiHelper.execute(() -> operationsHandler.updateOperation(operationUpdate));
  }

}
