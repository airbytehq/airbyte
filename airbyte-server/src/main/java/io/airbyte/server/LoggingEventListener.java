/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;
import jakarta.inject.Inject;
import jakarta.inject.Singleton;
import java.nio.file.Path;
import java.util.Optional;

/**
 * Initializes the logging client on startup
 */
@Singleton
public class LoggingEventListener implements ApplicationEventListener<ServiceReadyEvent> {

  @Inject
  private Optional<LogConfigs> logConfigs;
  @Inject
  private WorkerEnvironment workerEnvironment;
  @Value("${airbyte.workspace.root}")
  private String workspaceRoot;

  @Override
  public void onApplicationEvent(final ServiceReadyEvent event) {
    // Configure logging client
    LogClientSingleton.getInstance().setWorkspaceMdc(workerEnvironment, logConfigs.orElseThrow(),
        LogClientSingleton.getInstance().getServerLogsRoot(Path.of(workspaceRoot)));
  }

}
