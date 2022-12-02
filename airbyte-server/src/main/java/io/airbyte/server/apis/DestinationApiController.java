/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.DestinationApi;
import io.airbyte.api.model.generated.CheckConnectionRead;
import io.airbyte.api.model.generated.DestinationCloneRequestBody;
import io.airbyte.api.model.generated.DestinationCreate;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.DestinationReadList;
import io.airbyte.api.model.generated.DestinationSearch;
import io.airbyte.api.model.generated.DestinationUpdate;
import io.airbyte.api.model.generated.WorkspaceIdRequestBody;
import io.airbyte.server.handlers.DestinationHandler;
import io.airbyte.server.handlers.SchedulerHandler;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/destinations")
@AllArgsConstructor
public class DestinationApiController implements DestinationApi {

  private final DestinationHandler destinationHandler;
  private final SchedulerHandler schedulerHandler;

  @Override
  public CheckConnectionRead checkConnectionToDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationId(destinationIdRequestBody));
  }

  @Override
  public CheckConnectionRead checkConnectionToDestinationForUpdate(final DestinationUpdate destinationUpdate) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(destinationUpdate));
  }

  @Override
  public DestinationRead cloneDestination(final DestinationCloneRequestBody destinationCloneRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.cloneDestination(destinationCloneRequestBody));
  }

  @Override
  public DestinationRead createDestination(final DestinationCreate destinationCreate) {
    return ApiHelper.execute(() -> destinationHandler.createDestination(destinationCreate));
  }

  @Override
  public void deleteDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    ApiHelper.execute(() -> {
      destinationHandler.deleteDestination(destinationIdRequestBody);
      return null;
    });
  }

  @Override
  public DestinationRead getDestination(final DestinationIdRequestBody destinationIdRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.getDestination(destinationIdRequestBody));
  }

  @Override
  public DestinationReadList listDestinationsForWorkspace(final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody));
  }

  @Override
  public DestinationReadList searchDestinations(final DestinationSearch destinationSearch) {
    return ApiHelper.execute(() -> destinationHandler.searchDestinations(destinationSearch));
  }

  @Override
  public DestinationRead updateDestination(final DestinationUpdate destinationUpdate) {
    return ApiHelper.execute(() -> destinationHandler.updateDestination(destinationUpdate));
  }

}
