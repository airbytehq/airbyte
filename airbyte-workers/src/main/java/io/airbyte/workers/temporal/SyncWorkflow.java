/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DbtTransformationRunner;
import io.airbyte.workers.DbtTransformationWorker;
import io.airbyte.workers.DefaultNormalizationWorker;
import io.airbyte.workers.DefaultReplicationWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.airbyte.EmptyAirbyteSource;
import io.airbyte.workers.protocols.airbyte.NamespacingMapper;
import io.temporal.activity.ActivityCancellationType;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.nio.file.Path;
import java.time.Duration;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@WorkflowInterface
public interface SyncWorkflow {

  @WorkflowMethod
  StandardSyncOutput run(JobRunConfig jobRunConfig,
                         IntegrationLauncherConfig sourceLauncherConfig,
                         IntegrationLauncherConfig destinationLauncherConfig,
                         StandardSyncInput syncInput);

  class WorkflowImpl implements SyncWorkflow {

    private static final Logger LOGGER = LoggerFactory.getLogger(WorkflowImpl.class);

    private static final int MAX_SYNC_TIMEOUT_DAYS = new EnvConfigs().getMaxSyncTimeoutDays();

    private static final ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofDays(MAX_SYNC_TIMEOUT_DAYS))
        .setCancellationType(ActivityCancellationType.WAIT_CANCELLATION_COMPLETED)
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .build();

    private final ReplicationActivity replicationActivity = Workflow.newActivityStub(ReplicationActivity.class, options);
    private final NormalizationActivity normalizationActivity = Workflow.newActivityStub(NormalizationActivity.class, options);
    private final DbtTransformationActivity dbtTransformationActivity = Workflow.newActivityStub(DbtTransformationActivity.class, options);

    @Override
    public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                  final IntegrationLauncherConfig sourceLauncherConfig,
                                  final IntegrationLauncherConfig destinationLauncherConfig,
                                  final StandardSyncInput syncInput) {
      final StandardSyncOutput run = replicationActivity.replicate(jobRunConfig, sourceLauncherConfig, destinationLauncherConfig, syncInput);

      if (syncInput.getOperationSequence() != null && !syncInput.getOperationSequence().isEmpty()) {
        for (final StandardSyncOperation standardSyncOperation : syncInput.getOperationSequence()) {
          if (standardSyncOperation.getOperatorType() == OperatorType.NORMALIZATION) {
            final NormalizationInput normalizationInput = new NormalizationInput()
                .withDestinationConfiguration(syncInput.getDestinationConfiguration())
                .withCatalog(run.getOutputCatalog())
                .withResourceRequirements(syncInput.getResourceRequirements());

            normalizationActivity.normalize(jobRunConfig, destinationLauncherConfig, normalizationInput);
          } else if (standardSyncOperation.getOperatorType() == OperatorType.DBT) {
            final OperatorDbtInput operatorDbtInput = new OperatorDbtInput()
                .withDestinationConfiguration(syncInput.getDestinationConfiguration())
                .withOperatorDbt(standardSyncOperation.getOperatorDbt());

            dbtTransformationActivity.run(jobRunConfig, destinationLauncherConfig, syncInput.getResourceRequirements(), operatorDbtInput);
          } else {
            final String message = String.format("Unsupported operation type: %s", standardSyncOperation.getOperatorType());
            LOGGER.error(message);
            throw new IllegalArgumentException(message);
          }
        }
      }

      return run;
    }

  }

  @ActivityInterface
  interface ReplicationActivity {

    @ActivityMethod
    StandardSyncOutput replicate(JobRunConfig jobRunConfig,
                                 IntegrationLauncherConfig sourceLauncherConfig,
                                 IntegrationLauncherConfig destinationLauncherConfig,
                                 StandardSyncInput syncInput);

  }

  class ReplicationActivityImpl implements ReplicationActivity {

    private static final Logger LOGGER = LoggerFactory.getLogger(ReplicationActivityImpl.class);

    private final ProcessFactory processFactory;
    private final SecretsHydrator secretsHydrator;
    private final Path workspaceRoot;
    private final AirbyteConfigValidator validator;

    public ReplicationActivityImpl(final ProcessFactory processFactory, final SecretsHydrator secretsHydrator, final Path workspaceRoot) {
      this(processFactory, secretsHydrator, workspaceRoot, new AirbyteConfigValidator());
    }

    @VisibleForTesting
    ReplicationActivityImpl(final ProcessFactory processFactory,
                            final SecretsHydrator secretsHydrator,
                            final Path workspaceRoot,
                            final AirbyteConfigValidator validator) {
      this.processFactory = processFactory;
      this.secretsHydrator = secretsHydrator;
      this.workspaceRoot = workspaceRoot;
      this.validator = validator;
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
          workspaceRoot,
          jobRunConfig,
          getWorkerFactory(sourceLauncherConfig, destinationLauncherConfig, jobRunConfig, syncInput),
          inputSupplier,
          new CancellationHandler.TemporalCancellationHandler());

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

  @ActivityInterface
  interface NormalizationActivity {

    @ActivityMethod
    Void normalize(JobRunConfig jobRunConfig,
                   IntegrationLauncherConfig destinationLauncherConfig,
                   NormalizationInput input);

  }

  class NormalizationActivityImpl implements NormalizationActivity {

    private static final Logger LOGGER = LoggerFactory.getLogger(NormalizationActivityImpl.class);

    private final ProcessFactory processFactory;
    private final SecretsHydrator secretsHydrator;
    private final Path workspaceRoot;
    private final AirbyteConfigValidator validator;
    private final WorkerEnvironment workerEnvironment;
    private final String airbyteVersion;

    public NormalizationActivityImpl(final ProcessFactory processFactory,
                                     final SecretsHydrator secretsHydrator,
                                     final Path workspaceRoot,
                                     final WorkerEnvironment workerEnvironment,
                                     final String airbyteVersion) {
      this(processFactory, secretsHydrator, workspaceRoot, new AirbyteConfigValidator(), workerEnvironment, airbyteVersion);
    }

    @VisibleForTesting
    NormalizationActivityImpl(final ProcessFactory processFactory,
                              final SecretsHydrator secretsHydrator,
                              final Path workspaceRoot,
                              final AirbyteConfigValidator validator,
                              final WorkerEnvironment workerEnvironment,
                              final String airbyteVersion) {
      this.processFactory = processFactory;
      this.secretsHydrator = secretsHydrator;
      this.workspaceRoot = workspaceRoot;
      this.validator = validator;
      this.workerEnvironment = workerEnvironment;
      this.airbyteVersion = airbyteVersion;
    }

    @Override
    public Void normalize(final JobRunConfig jobRunConfig,
                          final IntegrationLauncherConfig destinationLauncherConfig,
                          final NormalizationInput input) {

      final var fullDestinationConfig = secretsHydrator.hydrate(input.getDestinationConfiguration());
      final var fullInput = Jsons.clone(input).withDestinationConfiguration(fullDestinationConfig);

      final Supplier<NormalizationInput> inputSupplier = () -> {
        validator.ensureAsRuntime(ConfigSchema.NORMALIZATION_INPUT, Jsons.jsonNode(fullInput));
        return fullInput;
      };

      final TemporalAttemptExecution<NormalizationInput, Void> temporalAttemptExecution = new TemporalAttemptExecution<>(
          workspaceRoot,
          jobRunConfig,
          getWorkerFactory(destinationLauncherConfig, jobRunConfig),
          inputSupplier,
          new CancellationHandler.TemporalCancellationHandler());

      return temporalAttemptExecution.get();
    }

    private CheckedSupplier<Worker<NormalizationInput, Void>, Exception> getWorkerFactory(final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                          final JobRunConfig jobRunConfig) {
      return () -> new DefaultNormalizationWorker(
          jobRunConfig.getJobId(),
          Math.toIntExact(jobRunConfig.getAttemptId()),
          NormalizationRunnerFactory.create(
              destinationLauncherConfig.getDockerImage(),
              processFactory),
          workerEnvironment);
    }

  }

  @ActivityInterface
  interface DbtTransformationActivity {

    @ActivityMethod
    Void run(JobRunConfig jobRunConfig,
             IntegrationLauncherConfig destinationLauncherConfig,
             ResourceRequirements resourceRequirements,
             OperatorDbtInput input);

  }

  class DbtTransformationActivityImpl implements DbtTransformationActivity {

    private static final Logger LOGGER = LoggerFactory.getLogger(DbtTransformationActivityImpl.class);

    private final ProcessFactory processFactory;
    private final SecretsHydrator secretsHydrator;
    private final Path workspaceRoot;
    private final AirbyteConfigValidator validator;
    private final String airbyteVersion;

    public DbtTransformationActivityImpl(
                                         final ProcessFactory processFactory,
                                         final SecretsHydrator secretsHydrator,
                                         final Path workspaceRoot,
                                         final String airbyteVersion) {
      this(processFactory, secretsHydrator, workspaceRoot, new AirbyteConfigValidator(), airbyteVersion);
    }

    @VisibleForTesting
    DbtTransformationActivityImpl(final ProcessFactory processFactory,
                                  final SecretsHydrator secretsHydrator,
                                  final Path workspaceRoot,
                                  final AirbyteConfigValidator validator,
                                  final String airbyteVersion) {
      this.processFactory = processFactory;
      this.secretsHydrator = secretsHydrator;
      this.workspaceRoot = workspaceRoot;
      this.validator = validator;
      this.airbyteVersion = airbyteVersion;
    }

    @Override
    public Void run(final JobRunConfig jobRunConfig,
                    final IntegrationLauncherConfig destinationLauncherConfig,
                    final ResourceRequirements resourceRequirements,
                    final OperatorDbtInput input) {

      final var fullDestinationConfig = secretsHydrator.hydrate(input.getDestinationConfiguration());
      final var fullInput = Jsons.clone(input).withDestinationConfiguration(fullDestinationConfig);

      final Supplier<OperatorDbtInput> inputSupplier = () -> {
        validator.ensureAsRuntime(ConfigSchema.OPERATOR_DBT_INPUT, Jsons.jsonNode(fullInput));
        return fullInput;
      };

      final TemporalAttemptExecution<OperatorDbtInput, Void> temporalAttemptExecution = new TemporalAttemptExecution<>(
          workspaceRoot,
          jobRunConfig,
          getWorkerFactory(destinationLauncherConfig, jobRunConfig, resourceRequirements),
          inputSupplier,
          new CancellationHandler.TemporalCancellationHandler());

      return temporalAttemptExecution.get();
    }

    private CheckedSupplier<Worker<OperatorDbtInput, Void>, Exception> getWorkerFactory(final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                        final JobRunConfig jobRunConfig,
                                                                                        final ResourceRequirements resourceRequirements) {
      return () -> new DbtTransformationWorker(
          jobRunConfig.getJobId(),
          Math.toIntExact(jobRunConfig.getAttemptId()),
          resourceRequirements,
          new DbtTransformationRunner(
              processFactory, NormalizationRunnerFactory.create(
                  destinationLauncherConfig.getDockerImage(),
                  processFactory)));
    }

  }

}
