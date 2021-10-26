/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultGetSpecWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
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
public interface SpecWorkflow {

  @WorkflowMethod
  ConnectorSpecification run(JobRunConfig jobRunConfig, IntegrationLauncherConfig launcherConfig);

  class WorkflowImpl implements SpecWorkflow {

    final ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofHours(1))
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .build();
    private final SpecActivity activity = Workflow.newActivityStub(SpecActivity.class, options);

    @Override
    public ConnectorSpecification run(final JobRunConfig jobRunConfig, final IntegrationLauncherConfig launcherConfig) {
      return activity.run(jobRunConfig, launcherConfig);
    }

  }

  @ActivityInterface
  interface SpecActivity {

    @ActivityMethod
    ConnectorSpecification run(JobRunConfig jobRunConfig, IntegrationLauncherConfig launcherConfig);

  }

  class SpecActivityImpl implements SpecActivity {

    private final ProcessFactory processFactory;
    private final Path workspaceRoot;
    private final WorkerEnvironment workerEnvironment;
    private final LogConfigs logConfigs;
    private final String databaseUser;
    private final String databasePassword;
    private final String databaseUrl;

    public SpecActivityImpl(final ProcessFactory processFactory,
                            final Path workspaceRoot,
                            final WorkerEnvironment workerEnvironment,
                            final LogConfigs logConfigs,
                            final String databaseUser,
                            final String databasePassword,
                            final String databaseUrl) {
      this.processFactory = processFactory;
      this.workspaceRoot = workspaceRoot;
      this.workerEnvironment = workerEnvironment;
      this.logConfigs = logConfigs;
      this.databaseUser = databaseUser;
      this.databasePassword = databasePassword;
      this.databaseUrl = databaseUrl;
    }

    public ConnectorSpecification run(final JobRunConfig jobRunConfig, final IntegrationLauncherConfig launcherConfig) {
      final Supplier<JobGetSpecConfig> inputSupplier = () -> new JobGetSpecConfig().withDockerImage(launcherConfig.getDockerImage());

      final TemporalAttemptExecution<JobGetSpecConfig, ConnectorSpecification> temporalAttemptExecution =
          new TemporalAttemptExecution<>(
              workspaceRoot, workerEnvironment, logConfigs,
              jobRunConfig,
              getWorkerFactory(launcherConfig),
              inputSupplier,
              new CancellationHandler.TemporalCancellationHandler(), databaseUser, databasePassword, databaseUrl);

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

}
