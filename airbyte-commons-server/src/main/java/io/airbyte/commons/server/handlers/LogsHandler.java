/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import io.airbyte.api.model.generated.LogsRequestBody;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.File;
import java.nio.file.Path;

/**
 * This handler is only responsible for server and scheduler logs. Jobs logs paths are determined by
 * the submitJob function in the JobSubmitter class in the airbyte-server module.
 */
@Singleton
public class LogsHandler {

  private final Path workspaceRoot;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;

  @Deprecated(forRemoval = true)
  public LogsHandler(final Configs configs) {
    this(configs.getWorkspaceRoot(), configs.getWorkerEnvironment(), configs.getLogConfigs());
  }

  @Inject
  public LogsHandler(@Named("workspaceRoot") final Path workspaceRoot,
                     final WorkerEnvironment workerEnvironment,
                     final LogConfigs logConfigs) {
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
  }

  public File getLogs(final LogsRequestBody logsRequestBody) {
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
