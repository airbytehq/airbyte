/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteProtocolVersionedMigratorFactory;
import io.airbyte.commons.temporal.CancellationHandler;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultCheckConnectionWorker;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.internal.VersionedAirbyteStreamFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;

@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
public class CheckConnectionActivityImpl implements CheckConnectionActivity {

  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final AirbyteApiClient airbyteApiClient;
  private final String airbyteVersion;
  private final AirbyteMessageSerDeProvider serDeProvider;
  private final AirbyteProtocolVersionedMigratorFactory migratorFactory;
  private final FeatureFlags featureFlags;

  public CheckConnectionActivityImpl(@Named("checkWorkerConfigs") final WorkerConfigs workerConfigs,
                                     @Named("checkProcessFactory") final ProcessFactory processFactory,
                                     final SecretsHydrator secretsHydrator,
                                     @Named("workspaceRoot") final Path workspaceRoot,
                                     final WorkerEnvironment workerEnvironment,
                                     final LogConfigs logConfigs,
                                     final AirbyteApiClient airbyteApiClient,
                                     @Value("${airbyte.version}") final String airbyteVersion,
                                     final AirbyteMessageSerDeProvider serDeProvider,
                                     final AirbyteProtocolVersionedMigratorFactory migratorFactory,
                                     final FeatureFlags featureFlags) {
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.airbyteApiClient = airbyteApiClient;
    this.secretsHydrator = secretsHydrator;
    this.airbyteVersion = airbyteVersion;
    this.serDeProvider = serDeProvider;
    this.migratorFactory = migratorFactory;
    this.featureFlags = featureFlags;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public ConnectorJobOutput runWithJobOutput(final CheckConnectionInput args) {
    ApmTraceUtils
        .addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, args.getJobRunConfig().getAttemptId(), JOB_ID_KEY, args.getJobRunConfig().getJobId(),
            DOCKER_IMAGE_KEY, args.getLauncherConfig().getDockerImage()));
    final StandardCheckConnectionInput rawInput = args.getConnectionConfiguration();
    final JsonNode fullConfig = secretsHydrator.hydrate(rawInput.getConnectionConfiguration());

    final StandardCheckConnectionInput input = new StandardCheckConnectionInput()
        .withActorId(rawInput.getActorId())
        .withActorType(rawInput.getActorType())
        .withConnectionConfiguration(fullConfig);

    final ActivityExecutionContext context = Activity.getExecutionContext();

    final TemporalAttemptExecution<StandardCheckConnectionInput, ConnectorJobOutput> temporalAttemptExecution =
        new TemporalAttemptExecution<>(
            workspaceRoot, workerEnvironment, logConfigs,
            args.getJobRunConfig(),
            getWorkerFactory(args.getLauncherConfig()),
            () -> input,
            new CancellationHandler.TemporalCancellationHandler(context),
            airbyteApiClient,
            airbyteVersion,
            () -> context);

    return temporalAttemptExecution.get();
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public StandardCheckConnectionOutput run(final CheckConnectionInput args) {
    ApmTraceUtils
        .addTagsToTrace(Map.of(JOB_ID_KEY, args.getJobRunConfig().getJobId(), DOCKER_IMAGE_KEY, args.getLauncherConfig().getDockerImage()));
    final ConnectorJobOutput output = runWithJobOutput(args);
    if (output.getFailureReason() != null) {
      return new StandardCheckConnectionOutput().withStatus(Status.FAILED).withMessage("Error checking connection");
    }

    return output.getCheckConnection();
  }

  private CheckedSupplier<Worker<StandardCheckConnectionInput, ConnectorJobOutput>, Exception> getWorkerFactory(
                                                                                                                final IntegrationLauncherConfig launcherConfig) {
    return () -> {
      final IntegrationLauncher integrationLauncher = new AirbyteIntegrationLauncher(
          launcherConfig.getJobId(),
          Math.toIntExact(launcherConfig.getAttemptId()),
          launcherConfig.getDockerImage(),
          processFactory,
          workerConfigs.getResourceRequirements(),
          launcherConfig.getAllowedHosts(),
          launcherConfig.getIsCustomConnector(),
          featureFlags);

      final ConnectorConfigUpdater connectorConfigUpdater = new ConnectorConfigUpdater(
          airbyteApiClient.getSourceApi(),
          airbyteApiClient.getDestinationApi());

      final AirbyteStreamFactory streamFactory = launcherConfig.getProtocolVersion() != null
          ? new VersionedAirbyteStreamFactory<>(serDeProvider, migratorFactory, launcherConfig.getProtocolVersion(), Optional.empty(),
              Optional.empty())
          : new DefaultAirbyteStreamFactory();

      return new DefaultCheckConnectionWorker(integrationLauncher, connectorConfigUpdater, streamFactory);
    };
  }

}
