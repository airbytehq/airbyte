/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.config.*;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.*;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;
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

  private static final MdcScope.Builder LOG_MDC_BUILDER = new MdcScope.Builder()
      .setLogPrefix("runner") // todo: uniquely identify runner since we'll eventually have multiple runners
      .setPrefixColor(LoggingHelper.Color.YELLOW);

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
                                      final StandardSyncInput syncInput,
                                      final UUID connectionId) {

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
        getWorkerFactory(sourceLauncherConfig, destinationLauncherConfig, jobRunConfig, syncInput, connectionId),
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
                                                                                                    final StandardSyncInput syncInput,
                                                                                                    final UUID connectionId) {
    return () -> new Worker<>() {

      final AtomicBoolean cancelled = new AtomicBoolean(false);
      Process process;

      @Override
      public ReplicationOutput run(StandardSyncInput standardSyncInput, Path jobRoot) throws WorkerException {
        try {
          // todo: do we need to wrapp all of this in a worker with anew TemporalAttemptExecution<>()

          final Path jobPath = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());

          // todo: don't use magic strings
          final Map<String, String> fileMap = Map.of(
              "application.txt", "replication",
              "jobRunConfig.json", Jsons.serialize(jobRunConfig),
              "sourceLauncherConfig.json", Jsons.serialize(sourceLauncherConfig),
              "destinationLauncherConfig.json", Jsons.serialize(destinationLauncherConfig),
              "syncInput.json", Jsons.serialize(syncInput),
              "connectionId.json", Jsons.serialize(connectionId),
              "envMap.json", Jsons.serialize(System.getenv()));

          // for now keep same failure behavior where this is heartbeating and depends on the parent worker to
          // exist
          process = processFactory.create(
              "runner-" + UUID.randomUUID().toString().substring(0, 10),
              0,
              jobPath,
              "airbyte/runner:" + airbyteVersion,
              false,
              fileMap,
              null,
              null, // todo: allow resource requirements for this pod to be configurable
              Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_RUNNER));

          final AtomicReference<ReplicationOutput> output = new AtomicReference<>();

          LineGobbler.gobble(process.getInputStream(), line -> {
            final var maybeOutput = Jsons.tryDeserialize(line, ReplicationOutput.class);

            if (maybeOutput.isPresent()) {
              output.set(maybeOutput.get());
            } else {
              try (final var mdcScope = LOG_MDC_BUILDER.build()) {
                LOGGER.info(line);
              }
            }
          });

          LineGobbler.gobble(process.getInputStream(), LOGGER::info, LOG_MDC_BUILDER);
          LineGobbler.gobble(process.getErrorStream(), LOGGER::error, LOG_MDC_BUILDER);

          WorkerUtils.wait(process);

          if (process.exitValue() != 0) {
            throw new WorkerException("Non-zero exit code!"); // todo: handle better
          }

          if (output.get() != null) {
            return output.get();
          } else {
            throw new WorkerException("Running the sync attempt resulted in no readable output!");
          }
        } catch (Exception e) {
          if (cancelled.get()) {
            throw new WorkerException("Sync was cancelled.", e);
          } else {
            throw new WorkerException("Running the sync attempt failed", e);
          }
        }
      }

      @Override
      public void cancel() {
        cancelled.set(true);

        if (process == null) {
          return;
        }

        LOGGER.debug("Closing sync runner process");
        WorkerUtils.gentleClose(process, 1, TimeUnit.MINUTES);
        if (process.isAlive() || process.exitValue() != 0) {
          LOGGER.error("Sync runner process wasn't successful");
        }
      }

    };
  }

}
