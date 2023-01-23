/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.commons.auth.AuthRoleConstants.ADMIN;

import io.airbyte.api.generated.LogsApi;
import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.commons.server.handlers.LogsHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;
import java.io.File;

@Controller("/api/v1/logs")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Context
@Secured(SecurityRule.IS_AUTHENTICATED)
public class LogsApiController implements LogsApi {

  private final LogsHandler logsHandler;

  public LogsApiController(final LogsHandler logsHandler) {
    this.logsHandler = logsHandler;
  }

  @Post("/get")
  @Secured({ADMIN})
  @Override
  public File getLogs(final LogsRequestBody logsRequestBody) {
    return ApiHelper.execute(() -> logsHandler.getLogs(logsRequestBody));
  }

}
