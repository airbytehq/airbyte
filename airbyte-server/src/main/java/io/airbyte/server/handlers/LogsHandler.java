/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.LogsRequestBody;
import io.airbyte.config.Configs;
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

<<<<<<< HEAD
  public File getLogs(Path workspaceRoot, WorkerEnvironment workerEnvironment, LogConfigs logConfigs, LogsRequestBody logsRequestBody) {
=======
  public File getLogs(final Configs configs, final LogsRequestBody logsRequestBody) {
>>>>>>> master
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
