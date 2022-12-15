/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.LogsApi;
import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.server.handlers.LogsHandler;
import io.micronaut.context.annotation.Context;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Post;
import java.io.File;
import javax.transaction.Transactional;

@Controller("/api/v1/logs")
@Context
@Transactional
public class LogsApiController implements LogsApi {

  private final LogsHandler logsHandler;

  public LogsApiController(final LogsHandler logsHandler) {
    this.logsHandler = logsHandler;
  }

  @Post("/get")
  @Override
  @Transactional
  public File getLogs(final LogsRequestBody logsRequestBody) {
    return ApiHelper.execute(() -> logsHandler.getLogs(logsRequestBody));
  }

}
