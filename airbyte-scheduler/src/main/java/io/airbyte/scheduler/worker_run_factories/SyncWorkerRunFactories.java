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

package io.airbyte.scheduler.worker_run_factories;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.WorkerRun;
import io.airbyte.workers.DefaultSyncWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import io.airbyte.workers.protocols.airbyte.EmptyAirbyteSource;
import io.airbyte.workers.wrappers.JobOutputSyncWorker;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SyncWorkerRunFactories {

  private static final Logger LOGGER = LoggerFactory.getLogger(SyncWorkerRunFactories.class);

  public static class ResetConnectionWorkerRunFactory implements WorkerRunFactory<JobResetConnectionConfig> {

    @Override
    public WorkerRun create(Path jobRoot, ProcessBuilderFactory pbf, long jobId, int attempt, JobResetConnectionConfig config) {
      return createSyncWorker(
          jobId,
          attempt,
          new EmptyAirbyteSource(),
          config.getDestinationDockerImage(),
          getSyncInputFromResetConfig(config),
          jobRoot,
          pbf);
    }

    private static StandardSyncInput getSyncInputFromResetConfig(JobResetConnectionConfig config) {
      return new StandardSyncInput()
          .withSourceConfiguration(Jsons.emptyObject())
          .withDestinationConfiguration(config.getDestinationConfiguration())
          .withCatalog(config.getConfiguredAirbyteCatalog());
    }

  }

  public static class SyncWorkerRunFactory implements WorkerRunFactory<JobSyncConfig> {

    @Override
    public WorkerRun create(Path jobRoot, ProcessBuilderFactory pbf, long jobId, int attempt, JobSyncConfig config) {
      final DefaultAirbyteSource airbyteSource =
          new DefaultAirbyteSource(WorkerRunFactoryUtils.createLauncher(jobId, attempt, config.getSourceDockerImage(), pbf));
      return createSyncWorker(
          jobId,
          attempt,
          airbyteSource,
          config.getDestinationDockerImage(),
          getSyncInputSyncConfig(config),
          jobRoot,
          pbf);
    }

    private static StandardSyncInput getSyncInputSyncConfig(JobSyncConfig config) {
      return new StandardSyncInput()
          .withSourceConfiguration(config.getSourceConfiguration())
          .withDestinationConfiguration(config.getDestinationConfiguration())
          .withCatalog(config.getConfiguredAirbyteCatalog())
          .withState(config.getState());
    }

  }

  private static WorkerRun createSyncWorker(long jobId,
                                            int attempt,
                                            AirbyteSource airbyteSource,
                                            String destinationDockerImage,
                                            StandardSyncInput syncInput,
                                            Path jobRoot,
                                            ProcessBuilderFactory pbf

  ) {
    final IntegrationLauncher destinationLauncher = WorkerRunFactoryUtils.createLauncher(jobId, attempt, destinationDockerImage, pbf);

    return new WorkerRun(
        jobRoot,
        syncInput,
        new JobOutputSyncWorker(
            new DefaultSyncWorker(
                jobId,
                attempt,
                airbyteSource,
                new DefaultAirbyteDestination(destinationLauncher),
                new AirbyteMessageTracker(),
                NormalizationRunnerFactory.create(
                    destinationDockerImage,
                    pbf,
                    syncInput.getDestinationConfiguration()))));
  }

}
