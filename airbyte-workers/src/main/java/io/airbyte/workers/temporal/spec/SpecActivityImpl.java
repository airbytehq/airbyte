/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.spec;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.function.Supplier;

public class SpecActivityImpl implements SpecActivity {

  private final ProcessFactory processFactory;
  private final Path workspaceRoot;

  public SpecActivityImpl(final ProcessFactory processFactory, final Path workspaceRoot) {
    this.processFactory = processFactory;
    this.workspaceRoot = workspaceRoot;
  }

  public ConnectorSpecification run(final JobRunConfig jobRunConfig, final IntegrationLauncherConfig launcherConfig) {
    final Supplier<JobGetSpecConfig> inputSupplier = () -> new JobGetSpecConfig().withDockerImage(launcherConfig.getDockerImage());

    final TemporalAttemptExecution<JobGetSpecConfig, ConnectorSpecification> temporalAttemptExecution = new TemporalAttemptExecution<>(
        workspaceRoot,
        jobRunConfig,
        getWorkerFactory(launcherConfig),
        inputSupplier,
        new CancellationHandler.TemporalCancellationHandler());

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<JobGetSpecConfig, ConnectorSpecification>, Exception> getWorkerFactory(final IntegrationLauncherConfig launcherConfig) {
    return () -> {
      final IntegrationLauncher integrationLauncher = new AirbyteIntegrationLauncher(
          launcherConfig.getJobId(),
          launcherConfig.getAttemptId().intValue(),
          launcherConfig.getDockerImage(),
          processFactory,
          WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);

      return new DefaultGetSpecWorker(integrationLauncher);
    };
  }

}
