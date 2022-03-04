/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.spec;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import java.nio.file.Path;
import java.util.function.Supplier;

public class SpecActivityImpl implements SpecActivity {

  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final Path workspaceRoot;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final JobPersistence jobPersistence;
  private final String airbyteVersion;

  public SpecActivityImpl(final WorkerConfigs workerConfigs,
                          final ProcessFactory processFactory,
                          final Path workspaceRoot,
                          final WorkerEnvironment workerEnvironment,
                          final LogConfigs logConfigs,
                          final JobPersistence jobPersistence,
                          final String airbyteVersion) {
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.workspaceRoot = workspaceRoot;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.jobPersistence = jobPersistence;
    this.airbyteVersion = airbyteVersion;
  }

  public ConnectorSpecification run(final JobRunConfig jobRunConfig, final IntegrationLauncherConfig launcherConfig) {
    final Supplier<JobGetSpecConfig> inputSupplier = () -> new JobGetSpecConfig().withDockerImage(launcherConfig.getDockerImage());

    final TemporalAttemptExecution<JobGetSpecConfig, ConnectorSpecification> temporalAttemptExecution = new TemporalAttemptExecution<>(
        workspaceRoot,
        workerEnvironment,
        logConfigs,
        jobRunConfig,
        getWorkerFactory(launcherConfig),
        inputSupplier,
        new CancellationHandler.TemporalCancellationHandler(),
        jobPersistence,
        airbyteVersion);

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<JobGetSpecConfig, ConnectorSpecification>, Exception> getWorkerFactory(
                                                                                                        final IntegrationLauncherConfig launcherConfig) {
    return () -> {
      final IntegrationLauncher integrationLauncher = new AirbyteIntegrationLauncher(
          launcherConfig.getJobId(),
          launcherConfig.getAttemptId().intValue(),
          launcherConfig.getDockerImage(),
          processFactory,
          workerConfigs.getResourceRequirements());

      return new DefaultGetSpecWorker(workerConfigs, integrationLauncher);
    };
  }

}
