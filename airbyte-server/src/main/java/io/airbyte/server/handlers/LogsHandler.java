/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.config.Configs;
import io.airbyte.config.helpers.LogClientSingleton;
import java.io.File;
import lombok.AllArgsConstructor;

/**
 * This handler is only responsible for server and scheduler logs. Jobs logs paths are determined by
 * the submitJob function in the JobSubmitter class in the airbyte-server module.
 */
@AllArgsConstructor
public class LogsHandler {

  private final Configs configs;

  public File getLogs(final LogsRequestBody logsRequestBody) {
    switch (logsRequestBody.getLogType()) {
      case SERVER -> {
        return LogClientSingleton.getInstance().getServerLogFile(configs.getWorkspaceRoot(), configs.getWorkerEnvironment(), configs.getLogConfigs());
      }
      case SCHEDULER -> {
        return LogClientSingleton.getInstance().getSchedulerLogFile(configs.getWorkspaceRoot(), configs.getWorkerEnvironment(),
            configs.getLogConfigs());
      }
      default -> throw new IllegalStateException("Unexpected value: " + logsRequestBody.getLogType());
    }
  }

}
