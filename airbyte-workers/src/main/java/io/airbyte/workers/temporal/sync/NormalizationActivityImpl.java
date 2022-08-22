/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultNormalizationWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

public class NormalizationActivityImpl implements NormalizationActivity {

  private final WorkerConfigs workerConfigs;
  private final ProcessFactory jobProcessFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final AirbyteConfigValidator validator;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final JobPersistence jobPersistence;
  private final String airbyteVersion;
  private final Optional<WorkerApp.ContainerOrchestratorConfig> containerOrchestratorConfig;

  public NormalizationActivityImpl(final Optional<WorkerApp.ContainerOrchestratorConfig> containerOrchestratorConfig,
                                   final WorkerConfigs workerConfigs,
                                   final ProcessFactory jobProcessFactory,
                                   final SecretsHydrator secretsHydrator,
                                   final Path workspaceRoot,
                                   final WorkerEnvironment workerEnvironment,
                                   final LogConfigs logConfigs,
                                   final JobPersistence jobPersistence,
                                   final String airbyteVersion) {
    this.containerOrchestratorConfig = containerOrchestratorConfig;
    this.workerConfigs = workerConfigs;
    this.jobProcessFactory = jobProcessFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.validator = new AirbyteConfigValidator();
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.jobPersistence = jobPersistence;
    this.airbyteVersion = airbyteVersion;
  }

  @Override
  public NormalizationSummary normalize(final JobRunConfig jobRunConfig,
                                        final IntegrationLauncherConfig destinationLauncherConfig,
                                        final NormalizationInput input) {
    final ActivityExecutionContext context = Activity.getExecutionContext();
    return TemporalUtils.withBackgroundHeartbeat(() -> {
      final var fullDestinationConfig = secretsHydrator.hydrate(input.getDestinationConfiguration());
      final var fullInput = Jsons.clone(input).withDestinationConfiguration(fullDestinationConfig);

      final Supplier<NormalizationInput> inputSupplier = () -> {
        validator.ensureAsRuntime(ConfigSchema.NORMALIZATION_INPUT, Jsons.jsonNode(fullInput));
        return fullInput;
      };

      final CheckedSupplier<Worker<NormalizationInput, NormalizationSummary>, Exception> workerFactory;

      if (containerOrchestratorConfig.isPresent()) {
        workerFactory = getContainerLauncherWorkerFactory(workerConfigs, destinationLauncherConfig, jobRunConfig,
            () -> context);
      } else {
        workerFactory = getLegacyWorkerFactory(workerConfigs, destinationLauncherConfig, jobRunConfig);
      }

      final TemporalAttemptExecution<NormalizationInput, NormalizationSummary> temporalAttemptExecution = new TemporalAttemptExecution<>(
          workspaceRoot, workerEnvironment, logConfigs,
          jobRunConfig,
          workerFactory,
          inputSupplier,
          new CancellationHandler.TemporalCancellationHandler(context),
          jobPersistence,
          airbyteVersion,
          () -> context);

      return temporalAttemptExecution.get();
    },
        () -> context);
  }

  private CheckedSupplier<Worker<NormalizationInput, NormalizationSummary>, Exception> getLegacyWorkerFactory(
                                                                                                              final WorkerConfigs workerConfigs,
                                                                                                              final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                              final JobRunConfig jobRunConfig) {
    return () -> new DefaultNormalizationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        NormalizationRunnerFactory.create(
            workerConfigs,
            destinationLauncherConfig.getDockerImage(),
            jobProcessFactory,
            NormalizationRunnerFactory.NORMALIZATION_VERSION),
        workerEnvironment);
  }

  private CheckedSupplier<Worker<NormalizationInput, NormalizationSummary>, Exception> getContainerLauncherWorkerFactory(
                                                                                                                         final WorkerConfigs workerConfigs,
                                                                                                                         final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                                         final JobRunConfig jobRunConfig,
                                                                                                                         final Supplier<ActivityExecutionContext> activityContext)
      throws IOException {
    final var jobScope = jobPersistence.getJob(Long.parseLong(jobRunConfig.getJobId())).getScope();
    final var connectionId = UUID.fromString(jobScope);
    return () -> new NormalizationLauncherWorker(
        connectionId,
        destinationLauncherConfig,
        jobRunConfig,
        workerConfigs,
        containerOrchestratorConfig.get(),
        activityContext);
  }

}
