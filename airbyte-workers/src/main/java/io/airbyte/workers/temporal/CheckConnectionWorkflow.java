/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.workers.temporal;

import io.airbyte.commons.functional.CheckedSupplier;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.DefaultCheckConnectionWorker;
import io.airbyte.workers.Worker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
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

    private final ProcessBuilderFactory pbf;
    private final Path workspaceRoot;

    public CheckConnectionActivityImpl(ProcessBuilderFactory pbf, Path workspaceRoot) {
      this.pbf = pbf;
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
            pbf);

        return new DefaultCheckConnectionWorker(integrationLauncher);
      };
    }

  }

}
