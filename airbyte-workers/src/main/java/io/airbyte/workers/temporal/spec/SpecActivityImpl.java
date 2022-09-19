/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.spec;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DefaultGetSpecWorker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.CancellationHandler;
import io.airbyte.workers.temporal.TemporalAttemptExecution;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.temporal.activity.Activity;
import io.temporal.activity.ActivityExecutionContext;
import java.nio.file.Path;
import java.util.function.Supplier;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;

@Singleton
@Requires(property = "airbyte.worker.plane",
          pattern = "(?i)^(?!data_plane).*")
public class SpecActivityImpl implements SpecActivity {

  @Inject
  @Named("specWorkerConfigs")
  private WorkerConfigs workerConfigs;
  @Inject
  @Named("specProcessFactory")
  private ProcessFactory processFactory;
  @Inject
  @Named("workspaceRoot")
  private Path workspaceRoot;
  @Inject
  private WorkerEnvironment workerEnvironment;
  @Inject
  private LogConfigs logConfigs;
  @Inject
  private AirbyteApiClient airbyteApiClient;
  @Value("${airbyte.version}")
  private String airbyteVersion;

  @Override
  public ConnectorJobOutput run(final JobRunConfig jobRunConfig, final IntegrationLauncherConfig launcherConfig) {
    final Supplier<JobGetSpecConfig> inputSupplier = () -> new JobGetSpecConfig().withDockerImage(launcherConfig.getDockerImage());

    final ActivityExecutionContext context = Activity.getExecutionContext();

    final TemporalAttemptExecution<JobGetSpecConfig, ConnectorJobOutput> temporalAttemptExecution = new TemporalAttemptExecution<>(
        workspaceRoot,
        workerEnvironment,
        logConfigs,
        jobRunConfig,
        getWorkerFactory(launcherConfig),
        inputSupplier,
        new CancellationHandler.TemporalCancellationHandler(context),
        airbyteApiClient,
        airbyteVersion,
        () -> context);

    return temporalAttemptExecution.get();
  }

  private CheckedSupplier<Worker<JobGetSpecConfig, ConnectorJobOutput>, Exception> getWorkerFactory(
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
