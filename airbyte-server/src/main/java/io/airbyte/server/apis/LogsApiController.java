/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.api.generated.LogsApi;
import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.server.handlers.LogsHandler;
import java.io.File;
import javax.ws.rs.Path;
import lombok.AllArgsConstructor;

@Path("/v1/logs/get")
@AllArgsConstructor
public class LogsApiController implements LogsApi {

  private final LogsHandler logsHandler;

  @Override
  public File getLogs(final LogsRequestBody logsRequestBody) {
    return ApiHelper.execute(() -> logsHandler.getLogs(logsRequestBody));
  }

}
