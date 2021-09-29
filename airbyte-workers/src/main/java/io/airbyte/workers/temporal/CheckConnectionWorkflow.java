/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultCheckConnectionWorker;
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
public interface CheckConnectionWorkflow {

  @WorkflowMethod
  StandardCheckConnectionOutput run(JobRunConfig jobRunConfig,
                                    IntegrationLauncherConfig launcherConfig,
                                    StandardCheckConnectionInput connectionConfiguration);

  class WorkflowImpl implements CheckConnectionWorkflow {

    final ActivityOptions options = ActivityOptions.newBuilder()
        .setScheduleToCloseTimeout(Duration.ofHours(1))
        .setRetryOptions(TemporalUtils.NO_RETRY)
        .build();
    private final CheckConnectionActivity activity = Workflow.newActivityStub(CheckConnectionActivity.class, options);

    @Override
    public StandardCheckConnectionOutput run(JobRunConfig jobRunConfig,
                                             IntegrationLauncherConfig launcherConfig,
                                             StandardCheckConnectionInput connectionConfiguration) {
      return activity.run(jobRunConfig, launcherConfig, connectionConfiguration);
    }

  }

  @ActivityInterface
  interface CheckConnectionActivity {

    @ActivityMethod
    StandardCheckConnectionOutput run(JobRunConfig jobRunConfig,
                                      IntegrationLauncherConfig launcherConfig,
                                      StandardCheckConnectionInput connectionConfiguration);

  }

  class CheckConnectionActivityImpl implements CheckConnectionActivity {

    private final ProcessFactory processFactory;
    private final Path workspaceRoot;

    public CheckConnectionActivityImpl(ProcessFactory processFactory, Path workspaceRoot) {
      this.processFactory = processFactory;
      this.workspaceRoot = workspaceRoot;
    }

    public StandardCheckConnectionOutput run(JobRunConfig jobRunConfig,
                                             IntegrationLauncherConfig launcherConfig,
                                             StandardCheckConnectionInput connectionConfiguration) {

      final Supplier<StandardCheckConnectionInput> inputSupplier = () -> connectionConfiguration;

      final TemporalAttemptExecution<StandardCheckConnectionInput, StandardCheckConnectionOutput> temporalAttemptExecution =
          new TemporalAttemptExecution<>(
              workspaceRoot,
              jobRunConfig,
              getWorkerFactory(launcherConfig),
              inputSupplier,
              new CancellationHandler.TemporalCancellationHandler());

      return temporalAttemptExecution.get();
    }

    private CheckedSupplier<Worker<StandardCheckConnectionInput, StandardCheckConnectionOutput>, Exception> getWorkerFactory(IntegrationLauncherConfig launcherConfig) {
      return () -> {
        final IntegrationLauncher integrationLauncher = new AirbyteIntegrationLauncher(
            launcherConfig.getJobId(),
            Math.toIntExact(launcherConfig.getAttemptId()),
            launcherConfig.getDockerImage(),
            processFactory,
            WorkerUtils.DEFAULT_RESOURCE_REQUIREMENTS);

        return new DefaultCheckConnectionWorker(integrationLauncher);
      };
    }

  }

}
