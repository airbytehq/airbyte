/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerApp.ContainerOrchestratorConfig;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerMetricReporter;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.general.DefaultReplicationWorker;
import io.airbyte.workers.internal.AirbyteMessageTracker;
import io.airbyte.workers.internal.AirbyteSource;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.internal.EmptyAirbyteSource;
import io.airbyte.workers.internal.NamespacingMapper;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ReplicationActivityImpl implements ReplicationActivity {

  private static final Logger LOGGER = LoggerFactory.getLogger(ReplicationActivityImpl.class);

  private final Optional<WorkerApp.ContainerOrchestratorConfig> containerOrchestratorConfig;
  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final AirbyteConfigValidator validator;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;

  private final AirbyteApiClient airbyteApiClient;
  private final String airbyteVersion;
  private final boolean useStreamCapableState;

  public ReplicationActivityImpl(final Optional<WorkerApp.ContainerOrchestratorConfig> containerOrchestratorConfig,
                                 final WorkerConfigs workerConfigs,
                                 final ProcessFactory processFactory,
                                 final SecretsHydrator secretsHydrator,
                                 final Path workspaceRoot,
                                 final WorkerEnvironment workerEnvironment,
                                 final LogConfigs logConfigs,
                                 final AirbyteApiClient airbyteApiClient,
                                 final String airbyteVersion,
                                 final boolean useStreamCapableState) {
    this(containerOrchestratorConfig, workerConfigs, processFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs,
        new AirbyteConfigValidator(), airbyteApiClient, airbyteVersion, useStreamCapableState);
  }

  @VisibleForTesting
  ReplicationActivityImpl(final Optional<WorkerApp.ContainerOrchestratorConfig> containerOrchestratorConfig,
                          final WorkerConfigs workerConfigs,
                          final ProcessFactory processFactory,
                          final SecretsHydrator secretsHydrator,
                          final Path workspaceRoot,
                          final WorkerEnvironment workerEnvironment,
                          final LogConfigs logConfigs,
                          final AirbyteConfigValidator validator,
                          final AirbyteApiClient airbyteApiClient,
                          final String airbyteVersion,
                          final boolean useStreamCapableState) {
    this.containerOrchestratorConfig = containerOrchestratorConfig;
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.validator = validator;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.airbyteApiClient = airbyteApiClient;
    this.airbyteVersion = airbyteVersion;
    this.useStreamCapableState = useStreamCapableState;
  }

  @Override
  public StandardSyncOutput replicate(final JobRunConfig jobRunConfig,
                                      final IntegrationLauncherConfig sourceLauncherConfig,
                                      final IntegrationLauncherConfig destinationLauncherConfig,
                                      final StandardSyncInput syncInput) {
    final ActivityExecutionContext context = Activity.getExecutionContext();
    return TemporalUtils.withBackgroundHeartbeat(
        () -> {

          final var fullSourceConfig = secretsHydrator.hydrate(syncInput.getSourceConfiguration());
          final var fullDestinationConfig = secretsHydrator.hydrate(syncInput.getDestinationConfiguration());

          final var fullSyncInput = Jsons.clone(syncInput)
              .withSourceConfiguration(fullSourceConfig)
              .withDestinationConfiguration(fullDestinationConfig);

          final Supplier<StandardSyncInput> inputSupplier = () -> {
            validator.ensureAsRuntime(ConfigSchema.STANDARD_SYNC_INPUT, Jsons.jsonNode(fullSyncInput));
            return fullSyncInput;
          };

          final CheckedSupplier<Worker<StandardSyncInput, ReplicationOutput>, Exception> workerFactory;

          if (containerOrchestratorConfig.isPresent()) {
            workerFactory = getContainerLauncherWorkerFactory(
                containerOrchestratorConfig.get(),
                sourceLauncherConfig,
                destinationLauncherConfig,
                jobRunConfig,
                syncInput.getResourceRequirements(),
                () -> context);
          } else {
            workerFactory =
                getLegacyWorkerFactory(sourceLauncherConfig, destinationLauncherConfig, jobRunConfig, syncInput);
          }

          final TemporalAttemptExecution<StandardSyncInput, ReplicationOutput> temporalAttempt =
              new TemporalAttemptExecution<>(
                  workspaceRoot,
                  workerEnvironment,
                  logConfigs,
                  jobRunConfig,
                  workerFactory,
                  inputSupplier,
                  new CancellationHandler.TemporalCancellationHandler(context),
                  airbyteApiClient,
                  airbyteVersion,
                  () -> context);

          final ReplicationOutput attemptOutput = temporalAttempt.get();
          final StandardSyncOutput standardSyncOutput = reduceReplicationOutput(attemptOutput);

          LOGGER.info("sync summary: {}", standardSyncOutput);

          return standardSyncOutput;
        },
        () -> context);
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
    syncSummary.setTotalStats(output.getReplicationAttemptSummary().getTotalStats());
    syncSummary.setStreamStats(output.getReplicationAttemptSummary().getStreamStats());

    final StandardSyncOutput standardSyncOutput = new StandardSyncOutput();
    standardSyncOutput.setState(output.getState());
    standardSyncOutput.setOutputCatalog(output.getOutputCatalog());
    standardSyncOutput.setStandardSyncSummary(syncSummary);
    standardSyncOutput.setFailures(output.getFailures());

    return standardSyncOutput;
  }

  private CheckedSupplier<Worker<StandardSyncInput, ReplicationOutput>, Exception> getLegacyWorkerFactory(final IntegrationLauncherConfig sourceLauncherConfig,
                                                                                                          final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                          final JobRunConfig jobRunConfig,
                                                                                                          final StandardSyncInput syncInput) {
    return () -> {
      final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(
          sourceLauncherConfig.getJobId(),
          Math.toIntExact(sourceLauncherConfig.getAttemptId()),
          sourceLauncherConfig.getDockerImage(),
          processFactory,
          syncInput.getSourceResourceRequirements());
      final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(
          destinationLauncherConfig.getJobId(),
          Math.toIntExact(destinationLauncherConfig.getAttemptId()),
          destinationLauncherConfig.getDockerImage(),
          processFactory,
          syncInput.getDestinationResourceRequirements());

      // reset jobs use an empty source to induce resetting all data in destination.
      final AirbyteSource airbyteSource =
          WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB.equals(sourceLauncherConfig.getDockerImage())
              ? new EmptyAirbyteSource(useStreamCapableState)
              : new DefaultAirbyteSource(workerConfigs, sourceLauncher);
      MetricClientFactory.initialize(MetricEmittingApps.WORKER);
      final MetricClient metricClient = MetricClientFactory.getMetricClient();
      final WorkerMetricReporter metricReporter = new WorkerMetricReporter(metricClient, sourceLauncherConfig.getDockerImage());

      return new DefaultReplicationWorker(
          jobRunConfig.getJobId(),
          Math.toIntExact(jobRunConfig.getAttemptId()),
          airbyteSource,
          new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
          new DefaultAirbyteDestination(workerConfigs, destinationLauncher),
          new AirbyteMessageTracker(),
          new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput)),
          metricReporter);
    };
  }

  private CheckedSupplier<Worker<StandardSyncInput, ReplicationOutput>, Exception> getContainerLauncherWorkerFactory(final ContainerOrchestratorConfig containerOrchestratorConfig,
                                                                                                                     final IntegrationLauncherConfig sourceLauncherConfig,
                                                                                                                     final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                                     final JobRunConfig jobRunConfig,
                                                                                                                     final ResourceRequirements resourceRequirements,
                                                                                                                     final Supplier<ActivityExecutionContext> activityContext)
      throws ApiException {
    final JobIdRequestBody id = new JobIdRequestBody();
    id.setId(Long.valueOf(jobRunConfig.getJobId()));

    final var jobScope = airbyteApiClient.getJobsApi().getJobInfo(id).getJob().getConfigId();
    final var connectionId = UUID.fromString(jobScope);

    return () -> new ReplicationLauncherWorker(
        connectionId,
        containerOrchestratorConfig,
        sourceLauncherConfig,
        destinationLauncherConfig,
        jobRunConfig,
        resourceRequirements,
        activityContext);
  }

}
