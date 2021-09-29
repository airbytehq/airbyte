/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

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
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;
import java.nio.file.Path;
import java.time.Duration;
import java.util.function.Supplier;

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
    public AirbyteCatalog run(JobRunConfig jobRunConfig,
                              IntegrationLauncherConfig launcherConfig,
                              StandardDiscoverCatalogInput config) {
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

    public DiscoverCatalogActivityImpl(ProcessFactory processFactory, SecretsHydrator secretsHydrator, Path workspaceRoot) {
      this.processFactory = processFactory;
      this.secretsHydrator = secretsHydrator;
      this.workspaceRoot = workspaceRoot;
    }

    public AirbyteCatalog run(JobRunConfig jobRunConfig,
                              IntegrationLauncherConfig launcherConfig,
                              StandardDiscoverCatalogInput config) {

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

    private CheckedSupplier<Worker<StandardDiscoverCatalogInput, AirbyteCatalog>, Exception> getWorkerFactory(IntegrationLauncherConfig launcherConfig) {
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
