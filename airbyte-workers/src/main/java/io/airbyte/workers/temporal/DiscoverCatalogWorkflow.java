/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.helpers.LogConfigs;
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
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.nio.file.Path;
import java.time.Duration;

@WorkflowInterface
public interface DiscoverCatalogWorkflow {

  @WorkflowMethod
  AirbyteCatalog run(JobRunConfig jobRunConfig,
                     IntegrationLauncherConfig launcherConfig,
                     StandardDiscoverCatalogInput config);

  class WorkflowImpl implements DiscoverCatalogWorkflow {

    final ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofHours(2))
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .build();
    private final DiscoverCatalogActivity activity = Workflow.newActivityStub(DiscoverCatalogActivity.class, options);

    @Override
    public AirbyteCatalog run(final JobRunConfig jobRunConfig,
                              final IntegrationLauncherConfig launcherConfig,
                              final StandardDiscoverCatalogInput config) {
      return activity.run(jobRunConfig, launcherConfig, config);
    }

  }

  @ActivityInterface
  interface DiscoverCatalogActivity {

    @ActivityMethod
    AirbyteCatalog run(JobRunConfig jobRunConfig,
                       IntegrationLauncherConfig launcherConfig,
                       StandardDiscoverCatalogInput config);

  }

  class DiscoverCatalogActivityImpl implements DiscoverCatalogActivity {

    private final ProcessFactory processFactory;
    private final SecretsHydrator secretsHydrator;
    private final Path workspaceRoot;
    private final WorkerEnvironment workerEnvironment;
    private final LogConfigs logConfigs;
    private final String databaseUser;
    private final String databasePassword;
    private final String databaseUrl;
    private final String airbyteVersion;

    public DiscoverCatalogActivityImpl(final ProcessFactory processFactory,
                                       final SecretsHydrator secretsHydrator,
                                       final Path workspaceRoot,
                                       final WorkerEnvironment workerEnvironment,
                                       final LogConfigs logConfigs,
                                       final String databaseUser,
                                       final String databasePassword,
                                       final String databaseUrl, final String airbyteVersion) {
      this.processFactory = processFactory;
      this.secretsHydrator = secretsHydrator;
      this.workspaceRoot = workspaceRoot;
      this.workerEnvironment = workerEnvironment;
      this.logConfigs = logConfigs;
      this.databaseUser = databaseUser;
      this.databasePassword = databasePassword;
      this.databaseUrl = databaseUrl;
      this.airbyteVersion = airbyteVersion;

    }

    public AirbyteCatalog run(final JobRunConfig jobRunConfig,
                              final IntegrationLauncherConfig launcherConfig,
                              final StandardDiscoverCatalogInput config) {

      final TemporalAttemptExecution<StandardDiscoverCatalogInput, AirbyteCatalog> temporalAttemptExecution =
          new TemporalAttemptExecution<>(
              workspaceRoot, workerEnvironment, logConfigs,
              jobRunConfig,
              getWorkerFactory(launcherConfig),
              () -> new StandardDiscoverCatalogInput().withConnectionConfiguration(secretsHydrator.hydrate(config.getConnectionConfiguration())),
              new CancellationHandler.TemporalCancellationHandler(), databaseUser, databasePassword, databaseUrl, airbyteVersion);

      return temporalAttemptExecution.get();
    }

    private CheckedSupplier<Worker<StandardDiscoverCatalogInput, AirbyteCatalog>, Exception> getWorkerFactory(
                                                                                                              final IntegrationLauncherConfig launcherConfig) {
      return () -> {
        final IntegrationLauncher integrationLauncher =
            new AirbyteIntegrationLauncher(launcherConfig.getJobId(), launcherConfig.getAttemptId().intValue(), launcherConfig.getDockerImage(),
                processFactory, WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);
        final AirbyteStreamFactory streamFactory = new DefaultAirbyteStreamFactory();
        return new DefaultDiscoverCatalogWorker(integrationLauncher, streamFactory);
      };
    }

  }

}
