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
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import javax.transaction.Transactional;
import lombok.AllArgsConstructor;

@Controller("/api/v1/destinations")
@AllArgsConstructor
@Transactional
public class DestinationApiController implements DestinationApi {

  private final DestinationHandler destinationHandler;
  private final SchedulerHandler schedulerHandler;

  @Post(uri = "/check_connection")
  @Override
  @Transactional
  public CheckConnectionRead checkConnectionToDestination(@Body final DestinationIdRequestBody destinationIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationId(destinationIdRequestBody));
  }

  @Post(uri = "/check_connection_for_update")
  @Override
  @Transactional
  public CheckConnectionRead checkConnectionToDestinationForUpdate(@Body final DestinationUpdate destinationUpdate) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(destinationUpdate));
  }

  @Post(uri = "/clone")
  @Override
  @Transactional
  public DestinationRead cloneDestination(@Body final DestinationCloneRequestBody destinationCloneRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.cloneDestination(destinationCloneRequestBody));
  }

  @Post(uri = "/create")
  @Override
  @Transactional
  public DestinationRead createDestination(@Body final DestinationCreate destinationCreate) {
    return ApiHelper.execute(() -> destinationHandler.createDestination(destinationCreate));
  }

  @Post(uri = "/delete")
  @Override
  @Transactional
  public void deleteDestination(@Body final DestinationIdRequestBody destinationIdRequestBody) {
    ApiHelper.execute(() -> {
      destinationHandler.deleteDestination(destinationIdRequestBody);
      return null;
    });
  }

  @Post(uri = "/get")
  @Override
  @Transactional
  public DestinationRead getDestination(@Body final DestinationIdRequestBody destinationIdRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.getDestination(destinationIdRequestBody));
  }

  @Post(uri = "/list")
  @Override
  @Transactional
  public DestinationReadList listDestinationsForWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody));
  }

  @Post(uri = "/search")
  @Override
  @Transactional
  public DestinationReadList searchDestinations(@Body final DestinationSearch destinationSearch) {
    return ApiHelper.execute(() -> destinationHandler.searchDestinations(destinationSearch));
  }

  @Post(uri = "/update")
  @Override
  @Transactional
  public DestinationRead updateDestination(@Body final DestinationUpdate destinationUpdate) {
    return ApiHelper.execute(() -> destinationHandler.updateDestination(destinationUpdate));
  }

}
