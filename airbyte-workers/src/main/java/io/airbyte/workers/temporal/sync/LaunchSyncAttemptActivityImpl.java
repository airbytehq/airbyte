/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.*;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.*;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.protocols.airbyte.*;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.UUID;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class LaunchSyncAttemptActivityImpl implements LaunchSyncAttemptActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(LaunchSyncAttemptActivityImpl.class);

  private final ProcessFactory processFactory;
  private final Path workspaceRoot;
  private final Configs.WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final String databaseUser;
  private final String databasePassword;
  private final String databaseUrl;
  private final String airbyteVersion;

  public LaunchSyncAttemptActivityImpl(
                                       final ProcessFactory processFactory,
                                       final Path workspaceRoot,
                                       final Configs.WorkerEnvironment workerEnvironment,
                                       final LogConfigs logConfigs,
                                       final String databaseUser,
                                       final String databasePassword,
                                       final String databaseUrl,
                                       final String airbyteVersion) {
    this.processFactory = processFactory;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.databaseUser = databaseUser;
    this.databasePassword = databasePassword;
    this.databaseUrl = databaseUrl;
    this.airbyteVersion = airbyteVersion;
  }

  @Override
  public StandardSyncOutput launch(JobRunConfig jobRunConfig,
                                   IntegrationLauncherConfig sourceLauncherConfig,
                                   IntegrationLauncherConfig destinationLauncherConfig,
                                   StandardSyncInput partialSyncInput,
                                   UUID connectionId) {

    final Supplier<StandardSyncInput> inputSupplier = () -> partialSyncInput;

    final TemporalAttemptExecution<StandardSyncInput, StandardSyncOutput> temporalAttempt = new TemporalAttemptExecution<>(
        workspaceRoot,
        workerEnvironment,
        logConfigs,
        jobRunConfig,
        getWorkerFactory(sourceLauncherConfig, destinationLauncherConfig, jobRunConfig, partialSyncInput, connectionId),
        inputSupplier,
        new CancellationHandler.TemporalCancellationHandler(),
        databaseUser,
        databasePassword,
        databaseUrl,
        airbyteVersion);

    final StandardSyncOutput attemptOutput = temporalAttempt.get();

    LOGGER.info("sync summary: {}", attemptOutput);

    return attemptOutput;
  }

  private CheckedSupplier<Worker<StandardSyncInput, StandardSyncOutput>, Exception> getWorkerFactory(
                                                                                                     final IntegrationLauncherConfig sourceLauncherConfig,
                                                                                                     final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                     final JobRunConfig jobRunConfig,
                                                                                                     final StandardSyncInput syncInput,
                                                                                                     final UUID connectionId) {
    return () -> new LaunchSyncAttemptWorker(
        sourceLauncherConfig,
        destinationLauncherConfig,
        jobRunConfig,
        syncInput,
        processFactory,
        workspaceRoot,
        airbyteVersion,
        connectionId);
  }

}
