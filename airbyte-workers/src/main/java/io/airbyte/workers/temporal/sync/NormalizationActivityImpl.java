/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DESTINATION_DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import com.google.common.annotations.VisibleForTesting;
import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.model.generated.JobIdRequestBody;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.migrations.v1.CatalogMigrationV1Helper;
import io.airbyte.commons.temporal.CancellationHandler;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.version.Version;
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
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.ContainerOrchestratorConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultNormalizationWorker;
import io.airbyte.workers.normalization.DefaultNormalizationRunner;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.sync.NormalizationLauncherWorker;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.micronaut.context.annotation.Value;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;

@Singleton
public class NormalizationActivityImpl implements NormalizationActivity {

  private final Optional<ContainerOrchestratorConfig> containerOrchestratorConfig;
  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final String airbyteVersion;
  private final Integer serverPort;
  private final AirbyteConfigValidator airbyteConfigValidator;
  private final TemporalUtils temporalUtils;
  private final ResourceRequirements normalizationResourceRequirements;
  private final AirbyteApiClient airbyteApiClient;

  private final static Version MINIMAL_VERSION_FOR_DATATYPES_V1 = new Version("0.3.0");

  public NormalizationActivityImpl(@Named("containerOrchestratorConfig") final Optional<ContainerOrchestratorConfig> containerOrchestratorConfig,
                                   @Named("defaultWorkerConfigs") final WorkerConfigs workerConfigs,
                                   @Named("defaultProcessFactory") final ProcessFactory processFactory,
                                   final SecretsHydrator secretsHydrator,
                                   @Named("workspaceRoot") final Path workspaceRoot,
                                   final WorkerEnvironment workerEnvironment,
                                   final LogConfigs logConfigs,
                                   @Value("${airbyte.version}") final String airbyteVersion,
                                   @Value("${micronaut.server.port}") final Integer serverPort,
                                   final AirbyteConfigValidator airbyteConfigValidator,
                                   final TemporalUtils temporalUtils,
                                   @Named("normalizationResourceRequirements") final ResourceRequirements normalizationResourceRequirements,
                                   final AirbyteApiClient airbyteApiClient) {
    this.containerOrchestratorConfig = containerOrchestratorConfig;
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.airbyteVersion = airbyteVersion;
    this.serverPort = serverPort;
    this.airbyteConfigValidator = airbyteConfigValidator;
    this.temporalUtils = temporalUtils;
    this.normalizationResourceRequirements = normalizationResourceRequirements;
    this.airbyteApiClient = airbyteApiClient;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public NormalizationSummary normalize(final JobRunConfig jobRunConfig,
                                        final IntegrationLauncherConfig destinationLauncherConfig,
                                        final NormalizationInput input) {
    ApmTraceUtils.addTagsToTrace(
        Map.of(ATTEMPT_NUMBER_KEY, jobRunConfig.getAttemptId(), JOB_ID_KEY, jobRunConfig.getJobId(), DESTINATION_DOCKER_IMAGE_KEY,
            destinationLauncherConfig.getDockerImage()));
    final ActivityExecutionContext context = Activity.getExecutionContext();
    return temporalUtils.withBackgroundHeartbeat(() -> {
      final var fullDestinationConfig = secretsHydrator.hydrate(input.getDestinationConfiguration());
      final var fullInput = Jsons.clone(input).withDestinationConfiguration(fullDestinationConfig);

      // Check the version of normalization
      // We require at least version 0.3.0 to support data types v1. Using an older version would lead to
      // all columns being typed as JSONB. We should fail before coercing the types into an unexpected
      // form.
      if (!normalizationSupportsV1DataTypes(destinationLauncherConfig)) {
        throw new IllegalStateException("Normalization is too old, a version >=\"0.3.0\" is required but got \""
            + destinationLauncherConfig.getNormalizationDockerImage() + "\" instead");
      }

      // This should only be useful for syncs that started before the release that contained v1 migration.
      // However, we lack the effective way to detect those syncs so this code should remain until we
      // phase v0 out.
      // Performance impact should be low considering the nature of the check compared to the time to run
      // normalization.
      CatalogMigrationV1Helper.upgradeSchemaIfNeeded(fullInput.getCatalog());

      final Supplier<NormalizationInput> inputSupplier = () -> {
        airbyteConfigValidator.ensureAsRuntime(ConfigSchema.NORMALIZATION_INPUT, Jsons.jsonNode(fullInput));
        return fullInput;
      };

      final CheckedSupplier<Worker<NormalizationInput, NormalizationSummary>, Exception> workerFactory;

      if (containerOrchestratorConfig.isPresent()) {
        workerFactory = getContainerLauncherWorkerFactory(workerConfigs, destinationLauncherConfig, jobRunConfig,
            () -> context);
      } else {
        workerFactory = getLegacyWorkerFactory(destinationLauncherConfig, jobRunConfig);
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

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public NormalizationInput generateNormalizationInput(final StandardSyncInput syncInput, final StandardSyncOutput syncOutput) {
    return new NormalizationInput()
        .withDestinationConfiguration(syncInput.getDestinationConfiguration())
        .withCatalog(syncOutput.getOutputCatalog())
        .withResourceRequirements(normalizationResourceRequirements);
  }

  @VisibleForTesting
  static boolean normalizationSupportsV1DataTypes(final IntegrationLauncherConfig destinationLauncherConfig) {
    try {
      final String[] normalizationImage = destinationLauncherConfig.getNormalizationDockerImage().split(":", 2);
      final Version normalizationVersion = new Version(normalizationImage[1]);
      return normalizationVersion.greaterThanOrEqualTo(MINIMAL_VERSION_FOR_DATATYPES_V1);
    } catch (final IllegalArgumentException e) {
      // IllegalArgument here means that the version isn't in a semver format.
      // The current behavior is to assume it supports v1 data types for dev purposes.
      return true;
    }
  }

  private CheckedSupplier<Worker<NormalizationInput, NormalizationSummary>, Exception> getLegacyWorkerFactory(
                                                                                                              final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                              final JobRunConfig jobRunConfig) {
    return () -> new DefaultNormalizationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        new DefaultNormalizationRunner(
            processFactory,
            destinationLauncherConfig.getNormalizationDockerImage(),
            destinationLauncherConfig.getNormalizationIntegrationType()),
        workerEnvironment);
  }

  private CheckedSupplier<Worker<NormalizationInput, NormalizationSummary>, Exception> getContainerLauncherWorkerFactory(
                                                                                                                         final WorkerConfigs workerConfigs,
                                                                                                                         final IntegrationLauncherConfig destinationLauncherConfig,
                                                                                                                         final JobRunConfig jobRunConfig,
                                                                                                                         final Supplier<ActivityExecutionContext> activityContext) {
    final JobIdRequestBody id = new JobIdRequestBody();
    id.setId(Long.valueOf(jobRunConfig.getJobId()));
    final var jobScope = AirbyteApiClient.retryWithJitter(
        () -> airbyteApiClient.getJobsApi().getJobInfo(id).getJob().getConfigId(),
        "get job scope");
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
