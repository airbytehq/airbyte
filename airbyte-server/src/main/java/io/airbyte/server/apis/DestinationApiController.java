/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.EDITOR;
import static io.airbyte.commons.auth.AuthRoleConstants.READER;

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
import io.airbyte.commons.server.handlers.DestinationHandler;
import io.airbyte.commons.server.handlers.SchedulerHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.annotation.Body;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.http.annotation.Status;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/destinations")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class DestinationApiController implements DestinationApi {

  private final DestinationHandler destinationHandler;
  private final SchedulerHandler schedulerHandler;

  public DestinationApiController(final DestinationHandler destinationHandler, final SchedulerHandler schedulerHandler) {
    this.destinationHandler = destinationHandler;
    this.schedulerHandler = schedulerHandler;
  }

  @Post(uri = "/check_connection")
  @Secured({EDITOR})
  @Override
  public CheckConnectionRead checkConnectionToDestination(@Body final DestinationIdRequestBody destinationIdRequestBody) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationId(destinationIdRequestBody));
  }

  @Post(uri = "/check_connection_for_update")
  @Secured({EDITOR})
  @Override
  public CheckConnectionRead checkConnectionToDestinationForUpdate(@Body final DestinationUpdate destinationUpdate) {
    return ApiHelper.execute(() -> schedulerHandler.checkDestinationConnectionFromDestinationIdForUpdate(destinationUpdate));
  }

  @Post(uri = "/clone")
  @Override
  public DestinationRead cloneDestination(@Body final DestinationCloneRequestBody destinationCloneRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.cloneDestination(destinationCloneRequestBody));
  }

  @Post(uri = "/create")
  @Secured({EDITOR})
  @Override
  public DestinationRead createDestination(@Body final DestinationCreate destinationCreate) {
    return ApiHelper.execute(() -> destinationHandler.createDestination(destinationCreate));
  }

  @Post(uri = "/delete")
  @Secured({EDITOR})
  @Override
  @Status(HttpStatus.NO_CONTENT)
  public void deleteDestination(@Body final DestinationIdRequestBody destinationIdRequestBody) {
    ApiHelper.execute(() -> {
      destinationHandler.deleteDestination(destinationIdRequestBody);
      return null;
    });
  }

  @Post(uri = "/get")
  @Secured({READER})
  @Override
  public DestinationRead getDestination(@Body final DestinationIdRequestBody destinationIdRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.getDestination(destinationIdRequestBody));
  }

  @Post(uri = "/list")
  @Secured({READER})
  @Override
  public DestinationReadList listDestinationsForWorkspace(@Body final WorkspaceIdRequestBody workspaceIdRequestBody) {
    return ApiHelper.execute(() -> destinationHandler.listDestinationsForWorkspace(workspaceIdRequestBody));
  }

  @Post(uri = "/search")
  @Override
  public DestinationReadList searchDestinations(@Body final DestinationSearch destinationSearch) {
    return ApiHelper.execute(() -> destinationHandler.searchDestinations(destinationSearch));
  }

  @Post(uri = "/update")
  @Secured({EDITOR})
  @Override
  public DestinationRead updateDestination(@Body final DestinationUpdate destinationUpdate) {
    return ApiHelper.execute(() -> destinationHandler.updateDestination(destinationUpdate));
  }

}
