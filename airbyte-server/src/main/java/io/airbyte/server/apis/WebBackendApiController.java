/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.WebBackendApi;
import io.airbyte.api.model.generated.*;
import io.airbyte.server.handlers.WebBackendCheckUpdatesHandler;
import io.airbyte.server.handlers.WebBackendConnectionsHandler;
import io.airbyte.server.handlers.WebBackendGeographiesHandler;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

@Controller("/api/v1/web_backend")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_AUTHENTICATED)
public class WebBackendApiController implements WebBackendApi {

  private final WebBackendConnectionsHandler webBackendConnectionsHandler;
  private final WebBackendGeographiesHandler webBackendGeographiesHandler;
  private final WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler;

  public WebBackendApiController(final WebBackendConnectionsHandler webBackendConnectionsHandler,
                                 final WebBackendGeographiesHandler webBackendGeographiesHandler,
                                 final WebBackendCheckUpdatesHandler webBackendCheckUpdatesHandler) {
    this.webBackendConnectionsHandler = webBackendConnectionsHandler;
    this.webBackendGeographiesHandler = webBackendGeographiesHandler;
    this.webBackendCheckUpdatesHandler = webBackendCheckUpdatesHandler;
  }

  @Post("/state/get_type")
  @Override
  public ConnectionStateType getStateType(final ConnectionIdRequestBody connectionIdRequestBody) {
    return ApiHelper.execute(() -> webBackendConnectionsHandler.getStateType(connectionIdRequestBody));
  }

  @Post("/check_updates")
  @Override
  public WebBackendCheckUpdatesRead webBackendCheckUpdates() {
    return ApiHelper.execute(webBackendCheckUpdatesHandler::checkUpdates);
  }

  @Post("/connections/create")
  @Override
  public WebBackendConnectionRead webBackendCreateConnection(final WebBackendConnectionCreate webBackendConnectionCreate) {
    return ApiHelper.execute(() -> webBackendConnectionsHandler.webBackendCreateConnection(webBackendConnectionCreate));
  }

  @Post("/connections/get")
  @Override
  public WebBackendConnectionRead webBackendGetConnection(final WebBackendConnectionRequestBody webBackendConnectionRequestBody) {
    return ApiHelper.execute(() -> webBackendConnectionsHandler.webBackendGetConnection(webBackendConnectionRequestBody));
  }

  @Post("/workspace/state")
  @Override
  public WebBackendWorkspaceStateResult webBackendGetWorkspaceState(final WebBackendWorkspaceState webBackendWorkspaceState) {
    return ApiHelper.execute(() -> webBackendConnectionsHandler.getWorkspaceState(webBackendWorkspaceState));
  }

  @Post("/connections/list")
  @Override
  public WebBackendConnectionReadList webBackendListConnectionsForWorkspace(final WebBackendConnectionListRequestBody webBackendConnectionListRequestBody) {
    return ApiHelper.execute(() -> webBackendConnectionsHandler.webBackendListConnectionsForWorkspace(webBackendConnectionListRequestBody));
  }

  @Post("/geographies/list")
  @Override
  public WebBackendGeographiesListResult webBackendListGeographies() {
    return ApiHelper.execute(webBackendGeographiesHandler::listGeographiesOSS);
  }

  @Post("/connections/update")
  @Override
  public WebBackendConnectionRead webBackendUpdateConnection(final WebBackendConnectionUpdate webBackendConnectionUpdate) {
    return ApiHelper.execute(() -> webBackendConnectionsHandler.webBackendUpdateConnection(webBackendConnectionUpdate));
  }

}
