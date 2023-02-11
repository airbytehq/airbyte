/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.connector;

import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteProtocolVersionedMigratorFactory;
import io.airbyte.commons.temporal.CancellationHandler;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.commons.version.Version;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultConnectorBuilderReadWorker;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.VersionedAirbyteStreamFactory;
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
import lombok.extern.slf4j.Slf4j;

@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
@Slf4j
public class ConnectorBuilderReadActivityImpl implements ConnectorBuilderReadActivity {

  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final AirbyteApiClient airbyteApiClient;
  private final String airbyteVersion;
  private final ConfigRepository configRepository;
  private final AirbyteMessageSerDeProvider serDeProvider;
  private final AirbyteProtocolVersionedMigratorFactory migratorFactory;
  private final FeatureFlags featureFlags;

  public ConnectorBuilderReadActivityImpl(@Named("discoverWorkerConfigs") final WorkerConfigs workerConfigs,
                                          @Named("discoverProcessFactory") final ProcessFactory processFactory,
                                          final ConfigRepository configRepository,
                                          final SecretsHydrator secretsHydrator,
                                          @Named("workspaceRoot") final Path workspaceRoot,
                                          final WorkerEnvironment workerEnvironment,
                                          final LogConfigs logConfigs,
                                          final AirbyteApiClient airbyteApiClient,
                                          @Value("${airbyte.version}") final String airbyteVersion,
                                          final AirbyteMessageSerDeProvider serDeProvider,
                                          final AirbyteProtocolVersionedMigratorFactory migratorFactory,
                                          final FeatureFlags featureFlags) {
    this.configRepository = configRepository;
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.airbyteApiClient = airbyteApiClient;
    this.airbyteVersion = airbyteVersion;
    this.serDeProvider = serDeProvider;
    this.migratorFactory = migratorFactory;
    this.featureFlags = featureFlags;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public StandardConnectorBuilderReadOutput run(final JobRunConfig jobRunConfig,
                                                final StandardConnectorBuilderReadInput config) {
    ApmTraceUtils.addTagsToTrace(
        Map.of(ATTEMPT_NUMBER_KEY, jobRunConfig.getAttemptId(), JOB_ID_KEY, jobRunConfig.getJobId(), DOCKER_IMAGE_KEY, "docker_image_activity")); // FIXME

    final ActivityExecutionContext context = Activity.getExecutionContext();

    final TemporalAttemptExecution<StandardConnectorBuilderReadInput, StandardConnectorBuilderReadOutput> temporalAttemptExecution =
        new TemporalAttemptExecution<>(
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            jobRunConfig,
            getWorkerFactory(jobRunConfig.getJobId()),
            () -> config,
            new CancellationHandler.TemporalCancellationHandler(context),
            airbyteApiClient,
            airbyteVersion,
            () -> context);

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<StandardConnectorBuilderReadInput, StandardConnectorBuilderReadOutput>, Exception> getWorkerFactory(String jobId) {
    return () -> {
      final AirbyteStreamFactory streamFactory =
          new VersionedAirbyteStreamFactory<>(serDeProvider, migratorFactory, new Version("1.0.0"), Optional.empty(), // FIXME
              Optional.empty());
      final ConnectorConfigUpdater connectorConfigUpdater =
          new ConnectorConfigUpdater(airbyteApiClient.getSourceApi(), airbyteApiClient.getDestinationApi());
      return new DefaultConnectorBuilderReadWorker(airbyteApiClient, processFactory, connectorConfigUpdater, streamFactory, jobId);
    };
  }

}
