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
import io.airbyte.config.StandardDiscoverCatalogInput;
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
    private final Path workspaceRoot;

    public DiscoverCatalogActivityImpl(ProcessFactory processFactory, Path workspaceRoot) {
      this.processFactory = processFactory;
      this.workspaceRoot = workspaceRoot;
    }

    public AirbyteCatalog run(JobRunConfig jobRunConfig,
                              IntegrationLauncherConfig launcherConfig,
                              StandardDiscoverCatalogInput config) {
      final Supplier<StandardDiscoverCatalogInput> inputSupplier = () -> config;

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
