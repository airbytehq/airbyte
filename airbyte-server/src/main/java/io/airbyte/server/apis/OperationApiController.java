/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.OperationApi;
import io.airbyte.api.model.generated.CheckOperationRead;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.OperationCreate;
import io.airbyte.api.model.generated.OperationIdRequestBody;
import io.airbyte.api.model.generated.OperationRead;
import io.airbyte.api.model.generated.OperationReadList;
import io.airbyte.api.model.generated.OperationUpdate;
import io.airbyte.api.model.generated.OperatorConfiguration;
import io.airbyte.server.handlers.OperationsHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/operations")
@AllArgsConstructor
public class OperationApiController implements OperationApi {

  private final OperationsHandler operationsHandler;

  @Override
  public CheckOperationRead checkOperation(final OperatorConfiguration operatorConfiguration) {
    return ApiHelper.execute(() -> operationsHandler.checkOperation(operatorConfiguration));
  }

  @Override
  public OperationRead createOperation(final OperationCreate operationCreate) {
    return ApiHelper.execute(() -> operationsHandler.createOperation(operationCreate));
  }

  @Override
  public void deleteOperation(final OperationIdRequestBody operationIdRequestBody) {
    ApiHelper.execute(() -> {
      operationsHandler.deleteOperation(operationIdRequestBody);
      return null;
    });
  }

  @Override
  public OperationRead getOperation(final OperationIdRequestBody operationIdRequestBody) {
    return ApiHelper.execute(() -> operationsHandler.getOperation(operationIdRequestBody));
  }

  @Override
  public OperationReadList listOperationsForConnection(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> operationsHandler.listOperationsForConnection(connectionIdRequestBody));
  }

  @Override
  public OperationRead updateOperation(final OperationUpdate operationUpdate) {
    return ApiHelper.execute(() -> operationsHandler.updateOperation(operationUpdate));
  }

}
