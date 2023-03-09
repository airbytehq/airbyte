/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.ADMIN;
import static io.airbyte.commons.auth.AuthRoleConstants.READER;

import io.airbyte.api.generated.StateApi;
import io.airbyte.api.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.model.generated.ConnectionState;
import io.airbyte.api.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.commons.server.handlers.StateHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/state")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class StateApiController implements StateApi {

  private final StateHandler stateHandler;

  public StateApiController(final StateHandler stateHandler) {
    this.stateHandler = stateHandler;
  }

  @Post("/create_or_update")
  @Secured({ADMIN})
  @Override
  public ConnectionState createOrUpdateState(final ConnectionStateCreateOrUpdate connectionStateCreateOrUpdate) {
    return ApiHelper.execute(() -> stateHandler.createOrUpdateState(connectionStateCreateOrUpdate));
  }

  @Post("/get")
  @Secured({READER})
  @Override
  public ConnectionState getState(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> stateHandler.getState(connectionIdRequestBody));
  }

}
