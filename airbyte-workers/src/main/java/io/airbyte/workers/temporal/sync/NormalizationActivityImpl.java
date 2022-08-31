/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.ContainerOrchestratorConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultNormalizationWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.airbyte.workers.temporal.TemporalUtils;
import io.micronaut.context.annotation.Value;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;

@Singleton
public class NormalizationActivityImpl implements NormalizationActivity {

  @Inject
  @Named("containerOrchestratorConfig")
  private Optional<ContainerOrchestratorConfig> containerOrchestratorConfig;
  @Inject
  @Named("defaultWorkerConfigs")
  private WorkerConfigs workerConfigs;
  @Inject
  @Named("defaultProcessFactory")
  private ProcessFactory processFactory;
  @Inject
  private SecretsHydrator secretsHydrator;
  @Inject
  @Named("workspaceRoot")
  private Path workspaceRoot;
  @Inject
  private WorkerEnvironment workerEnvironment;
  @Inject
  private LogConfigs logConfigs;
  @Inject
  private JobPersistence jobPersistence;
  @Value("${airbyte.version}")
  private String airbyteVersion;
  @Value("${micronaut.server.port}")
  private Integer serverPort;
  @Inject
  private AirbyteConfigValidator airbyteConfigValidator;
  @Inject
  private TemporalUtils temporalUtils;
  @Inject
  @Named("normalizationResourceRequirements")
  private ResourceRequirements normalizationResourceRequirements;
  @Inject
  private AirbyteApiClient airbyteApiClient;

  @Override
  public NormalizationSummary normalize(final JobRunConfig jobRunConfig,
                                        final IntegrationLauncherConfig destinationLauncherConfig,
                                        final NormalizationInput input) {
    final ActivityExecutionContext context = Activity.getExecutionContext();
    return temporalUtils.withBackgroundHeartbeat(() -> {
      final var fullDestinationConfig = secretsHydrator.hydrate(input.getDestinationConfiguration());
      final var fullInput = Jsons.clone(input).withDestinationConfiguration(fullDestinationConfig);

      final Supplier<NormalizationInput> inputSupplier = () -> {
        airbyteConfigValidator.ensureAsRuntime(ConfigSchema.NORMALIZATION_INPUT, Jsons.jsonNode(fullInput));
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
          airbyteApiClient,
          airbyteVersion,
          () -> context);

      return temporalAttemptExecution.get();
    },
        () -> context);
  }

  @Override
  public NormalizationInput generateNormalizationInput(final StandardSyncInput syncInput, final StandardSyncOutput syncOutput) {
    return new NormalizationInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withCatalog(syncOutput.getOutputCatalog())
        .withResourceRequirements(normalizationResourceRequirements);
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
            processFactory,
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
        activityContext,
        serverPort,
        temporalUtils);
  }

}
