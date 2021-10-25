/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.discover.catalog;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultDiscoverCatalogWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteStreamFactory;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteStreamFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.function.Supplier;

public class DiscoverCatalogActivityImpl implements DiscoverCatalogActivity {

  private final ProcessFactory processFactory;
  private final SecretsHydrator secretsHydrator;
  private final Path workspaceRoot;

  public DiscoverCatalogActivityImpl(final ProcessFactory processFactory, final SecretsHydrator secretsHydrator, final Path workspaceRoot) {
    this.processFactory = processFactory;
    this.secretsHydrator = secretsHydrator;
    this.workspaceRoot = workspaceRoot;
  }

  public AirbyteCatalog run(final JobRunConfig jobRunConfig,
                            final IntegrationLauncherConfig launcherConfig,
                            final StandardDiscoverCatalogInput config) {

    final JsonNode fullConfig = secretsHydrator.hydrate(config.getConnectionConfiguration());

    final StandardDiscoverCatalogInput input = new StandardDiscoverCatalogInput()
        .withConnectionConfiguration(fullConfig);

    final Supplier<StandardDiscoverCatalogInput> inputSupplier = () -> input;

    final TemporalAttemptExecution<StandardDiscoverCatalogInput, AirbyteCatalog> temporalAttemptExecution = new TemporalAttemptExecution<>(
        workspaceRoot,
        jobRunConfig,
        getWorkerFactory(launcherConfig),
        inputSupplier,
        new CancellationHandler.TemporalCancellationHandler());

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<StandardDiscoverCatalogInput, AirbyteCatalog>, Exception> getWorkerFactory(final IntegrationLauncherConfig launcherConfig) {
    return () -> {
      final IntegrationLauncher integrationLauncher =
          new AirbyteIntegrationLauncher(launcherConfig.getJobId(), launcherConfig.getAttemptId().intValue(), launcherConfig.getDockerImage(),
              processFactory, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);
      final AirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();
      return new DefaultDiscoverCatalogWorker(integrationLauncher, streamFactory);
    };
  }

}
