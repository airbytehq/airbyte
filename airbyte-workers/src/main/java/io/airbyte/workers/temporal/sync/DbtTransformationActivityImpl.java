/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.ContainerOrchestratorConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DbtTransformationRunner;
import io.airbyte.workers.general.DbtTransformationWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.airbyte.workers.temporal.TemporalUtils;
import io.micronaut.context.annotation.Value;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;

@Singleton
public class DbtTransformationActivityImpl implements DbtTransformationActivity {

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
  @Value("${airbyte.version}")
  private String airbyteVersion;
  @Value("${micronaut.server.port}")
  private Integer serverPort;
  @Inject
  private AirbyteConfigValidator airbyteConfigValidator;
  @Inject
  private TemporalUtils temporalUtils;
  @Inject
  private AirbyteApiClient airbyteApiClient;

  @Override
  public Void run(final JobRunConfig jobRunConfig,
                  final IntegrationLauncherConfig destinationLauncherConfig,
                  final ResourceRequirements resourceRequirements,
                  final OperatorDbtInput input) {
    final ActivityExecutionContext context = Activity.getExecutionContext();
    return temporalUtils.withBackgroundHeartbeat(
        () -> {
          final var fullDestinationConfig = secretsHydrator.hydrate(input.getDestinationConfiguration());
          final var fullInput = Jsons.clone(input).withDestinationConfiguration(fullDestinationConfig);

          final Supplier<OperatorDbtInput> inputSupplier = () -> {
            airbyteConfigValidator.ensureAsRuntime(ConfigSchema.OPERATOR_DBT_INPUT, Jsons.jsonNode(fullInput));
            return fullInput;
          };

          final CheckedSupplier<Worker<OperatorDbtInput, Void>, Exception> workerFactory;

          if (containerOrchestratorConfig.isPresent()) {
            workerFactory =
                getContainerLauncherWorkerFactory(workerConfigs, destinationLauncherConfig, jobRunConfig,
                    () -> context);
          } else {
            workerFactory = getLegacyWorkerFactory(destinationLauncherConfig, jobRunConfig, resourceRequirements);
          }

          final TemporalAttemptExecution<OperatorDbtInput, Void> temporalAttemptExecution =
              new TemporalAttemptExecution<>(
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

  private CheckedSupplier<Worker<OperatorDbtInput, Void>, Exception> getLegacyWorkerFactory(final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                            final JobRunConfig jobRunConfig,
                                                                                            final ResourceRequirements resourceRequirements) {
    return () -> new DbtTransformationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        resourceRequirements,
        new DbtTransformationRunner(
            workerConfigs,
            processFactory, NormalizationRunnerFactory.create(
                workerConfigs,
                destinationLauncherConfig.getDockerImage(),
                processFactory,
                NormalizationRunnerFactory.NORMALIZATION_VERSION)));
  }

  private CheckedSupplier<Worker<OperatorDbtInput, Void>, Exception> getContainerLauncherWorkerFactory(
                                                                                                       final WorkerConfigs workerConfigs,
                                                                                                       final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                       final JobRunConfig jobRunConfig,
                                                                                                       final Supplier<ActivityExecutionContext> activityContext)
      throws ApiException {
    final JobIdRequestBody id = new JobIdRequestBody();
    id.setId(Long.valueOf(jobRunConfig.getJobId()));
    final var jobScope =  airbyteApiClient.getJobsApi().getJobInfo(id).getJob().getConfigId();
    final var connectionId = UUID.fromString(jobScope);

    return () -> new DbtLauncherWorker(
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
