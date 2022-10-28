package io.airbyte.server.apis;

import io.airbyte.api.generated.LogsApi;
import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.server.handlers.LogsHandler;
import java.io.File;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class LogsApiController implements LogsApi {

  private final LogsHandler logsHandler;

  @Override public File getLogs(final LogsRequestBody logsRequestBody) {
    return ConfigurationApi.execute(() -> logsHandler.getLogs(logsRequestBody));
  }
}
