/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.discover.catalog;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.nio.file.Path;

public class DiscoverCatalogActivityImpl implements DiscoverCatalogActivity {

  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final AirbyteApiClient airbyteApiClient;
  private final String airbyteVersion;

  public DiscoverCatalogActivityImpl(final WorkerConfigs workerConfigs,
                                     final ProcessFactory processFactory,
                                     final SecretsHydrator secretsHydrator,
                                     final Path workspaceRoot,
                                     final WorkerEnvironment workerEnvironment,
                                     final LogConfigs logConfigs,
                                     final AirbyteApiClient airbyteApiClient,
                                     final String airbyteVersion) {
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.airbyteApiClient = airbyteApiClient;
    this.airbyteVersion = airbyteVersion;
  }

  @Override
  public ConnectorJobOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig launcherConfig,
                                final StandardDiscoverCatalogInput config) {
    final JsonNode fullConfig = secretsHydrator.hydrate(config.getConnectionConfiguration());

    final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput()
        .withConnectionConfiguration(fullConfig);

    final ActivityExecutionContext context = Activity.getExecutionContext();

    final TemporalAttemptExecution<StandardDiscoverCatalogInput, ConnectorJobOutput> temporalAttemptExecution =
        new TemporalAttemptExecution<>(
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            jobRunConfig,
            getWorkerFactory(launcherConfig),
            () -> input,
            new CancellationHandler.TemporalCancellationHandler(context),
            airbyteApiClient,
            airbyteVersion,
            () -> context);

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<StandardDiscoverCatalogInput, ConnectorJobOutput>, Exception> getWorkerFactory(final IntegrationLauncherConfig launcherConfig) {
    return () -> {
      final IntegrationLauncher integrationLauncher =
          new AirbyteIntegrationLauncher(launcherConfig.getJobId(), launcherConfig.getAttemptId().intValue(), launcherConfig.getDockerImage(),
              processFactory, workerConfigs.getResourceRequirements());
      final AirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();
      return new DefaultDiscoverCatalogWorker(workerConfigs, integrationLauncher, streamFactory);
    };
  }

}
