/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import io.airbyte.api.model.LogsRequestBody;
import io.airbyte.config.Configs;
import io.airbyte.config.helpers.LogClientSingleton;
import java.io.File;

/**
 * This handler is only responsible for server and scheduler logs. Jobs logs paths are determined by
 * the submitJob function in the JobSubmitter class in the airbyte-server module.
 */
public class LogsHandler {

  public File getLogs(Configs configs, LogsRequestBody logsRequestBody) {
    switch (logsRequestBody.getLogType()) {
      case SERVER -> {
        return LogClientSingleton.getServerLogFile(configs);
      }
      case SCHEDULER -> {
        return LogClientSingleton.getSchedulerLogFile(configs);
      }
      default -> throw new IllegalStateException("Unexpected value: " + logsRequestBody.getLogType());
    }
  }

}
