/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultReplicationWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.airbyte.EmptyAirbyteSource;
import io.airbyte.workers.protocols.airbyte.NamespacingMapper;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ReplicationActivityImpl implements ReplicationActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(ReplicationActivityImpl.class);

  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final AirbyteConfigValidator validator;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;

  private final String databaseUser;
  private final String databasePassword;
  private final String databaseUrl;
  private final String airbyteVersion;

  public ReplicationActivityImpl(
                                 final ProcessFactory processFactory,
                                 final SecretsHydrator secretsHydrator,
                                 final Path workspaceRoot,
                                 final WorkerEnvironment workerEnvironment,
                                 final LogConfigs logConfigs,
                                 final String databaseUser,
                                 final String databasePassword,
                                 final String databaseUrl,
                                 final String airbyteVersion) {
    this(processFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs, new AirbyteConfigValidator(), databaseUser,
        databasePassword, databaseUrl, airbyteVersion);
  }

  @VisibleForTesting
  ReplicationActivityImpl(final ProcessFactory processFactory,
                          final SecretsHydrator secretsHydrator,
                          final Path workspaceRoot,
                          final WorkerEnvironment workerEnvironment,
                          final LogConfigs logConfigs,
                          final AirbyteConfigValidator validator,
                          final String databaseUser,
                          final String databasePassword,
                          final String databaseUrl,
                          final String airbyteVersion) {
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.validator = validator;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.databaseUser = databaseUser;
    this.databasePassword = databasePassword;
    this.databaseUrl = databaseUrl;
    this.airbyteVersion = airbyteVersion;
  }

  @Override
  public StandardSyncOutput replicate(final JobRunConfig jobRunConfig,
                                      final IntegrationLauncherConfig sourceLauncherConfig,
                                      final IntegrationLauncherConfig destinationLauncherConfig,
                                      final StandardSyncInput syncInput) {

    final var fullSourceConfig = secretsHydrator.hydrate(syncInput.getSourceConfiguration());
    final var fullDestinationConfig = secretsHydrator.hydrate(syncInput.getDestinationConfiguration());

    final var fullSyncInput = Jsons.clone(syncInput)
        .withSourceConfiguration(fullSourceConfig)
        .withDestinationConfiguration(fullDestinationConfig);

    final Supplier<StandardSyncInput> inputSupplier = () -> {
      validator.ensureAsRuntime(ConfigSchema.STANDARD_SYNC_INPUT, Jsons.jsonNode(fullSyncInput));
      return fullSyncInput;
    };

    final TemporalAttemptExecution<StandardSyncInput, ReplicationOutput> temporalAttempt = new TemporalAttemptExecution<>(
        workspaceRoot, workerEnvironment, logConfigs,
        jobRunConfig,
        getWorkerFactory(sourceLauncherConfig, destinationLauncherConfig, jobRunConfig, syncInput),
        inputSupplier,
        new CancellationHandler.TemporalCancellationHandler(), databaseUser, databasePassword, databaseUrl, airbyteVersion);

    final ReplicationOutput attemptOutput = temporalAttempt.get();
    final StandardSyncOutput standardSyncOutput = reduceReplicationOutput(attemptOutput);

    LOGGER.info("sync summary: {}", standardSyncOutput);

    return standardSyncOutput;
  }

  private static StandardSyncOutput reduceReplicationOutput(final ReplicationOutput output) {
    final long totalBytesReplicated = output.getReplicationAttemptSummary().getBytesSynced();
    final long totalRecordsReplicated = output.getReplicationAttemptSummary().getRecordsSynced();

    final StandardSyncSummary syncSummary = new StandardSyncSummary();
    syncSummary.setBytesSynced(totalBytesReplicated);
    syncSummary.setRecordsSynced(totalRecordsReplicated);
    syncSummary.setStartTime(output.getReplicationAttemptSummary().getStartTime());
    syncSummary.setEndTime(output.getReplicationAttemptSummary().getEndTime());
    syncSummary.setStatus(output.getReplicationAttemptSummary().getStatus());

    final StandardSyncOutput standardSyncOutput = new StandardSyncOutput();
    standardSyncOutput.setState(output.getState());
    standardSyncOutput.setOutputCatalog(output.getOutputCatalog());
    standardSyncOutput.setStandardSyncSummary(syncSummary);

    return standardSyncOutput;
  }

  private CheckedSupplier<Worker<StandardSyncInput, ReplicationOutput>, Exception> getWorkerFactory(
                                                                                                    final IntegrationLauncherConfig sourceLauncherConfig,
                                                                                                    final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                    final JobRunConfig jobRunConfig,
                                                                                                    final StandardSyncInput syncInput) {
    return () -> {
      final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(
          sourceLauncherConfig.getJobId(),
          Math.toIntExact(sourceLauncherConfig.getAttemptId()),
          sourceLauncherConfig.getDockerImage(),
          processFactory,
          syncInput.getResourceRequirements());
      final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(
          destinationLauncherConfig.getJobId(),
          Math.toIntExact(destinationLauncherConfig.getAttemptId()),
          destinationLauncherConfig.getDockerImage(),
          processFactory,
          syncInput.getResourceRequirements());

      // reset jobs use an empty source to induce resetting all data in destination.
      final AirbyteSource airbyteSource =
          sourceLauncherConfig.getDockerImage().equals(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB) ? new EmptyAirbyteSource()
              : new DefaultAirbyteSource(sourceLauncher);

      return new DefaultReplicationWorker(
          jobRunConfig.getJobId(),
          Math.toIntExact(jobRunConfig.getAttemptId()),
          airbyteSource,
          new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
          new DefaultAirbyteDestination(destinationLauncher),
          new AirbyteMessageTracker(),
          new AirbyteMessageTracker());
    };
  }

}
