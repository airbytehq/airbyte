/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import java.io.File;
import java.nio.file.Path;

/**
 * This handler is only responsible for server and scheduler logs. Jobs logs paths are determined by
 * the submitJob function in the JobSubmitter class in the airbyte-server module.
 */
public class LogsHandler {

  public File getLogs(final Path workspaceRoot,
                      final WorkerEnvironment workerEnvironment,
                      final LogConfigs logConfigs,
                      final LogsRequestBody logsRequestBody) {
    switch (logsRequestBody.getLogType()) {
      case SERVER -> {
        return LogClientSingleton.getInstance().getServerLogFile(workspaceRoot, workerEnvironment, logConfigs);
      }
      case SCHEDULER -> {
        return LogClientSingleton.getInstance().getSchedulerLogFile(workspaceRoot, workerEnvironment, logConfigs);
      }
      default -> throw new IllegalStateException("Unexpected value: " + logsRequestBody.getLogType());
    }
  }

}
