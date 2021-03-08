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

package io.airbyte.scheduler.worker_run;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteSource;
import java.nio.file.Path;

public class SyncWorkerRunFactory extends BaseWorkerRunFactory<JobSyncConfig> implements WorkerRunFactory<JobSyncConfig> {

  public SyncWorkerRunFactory() {
    super();
  }

  @VisibleForTesting
  SyncWorkerRunFactory(IntegrationLauncherFactory integrationLauncherFactory, WorkerRunCreator workerRunCreator) {
    super(integrationLauncherFactory, workerRunCreator);
  }

  @Override
  public WorkerRun create(Path jobRoot, ProcessBuilderFactory pbf, long jobId, int attempt, JobSyncConfig config) {
    final DefaultAirbyteSource airbyteSource =
        new DefaultAirbyteSource(integrationLauncherFactory.create(jobId, attempt, config.getSourceDockerImage(), pbf));
    return SyncWorkerRunFactoryUtils.createSyncWorker(
        jobId,
        attempt,
        airbyteSource,
        config.getDestinationDockerImage(),
        createSyncInputSyncConfig(config),
        jobRoot,
        pbf,
        integrationLauncherFactory,
        workerRunCreator);
  }

  public static StandardSyncInput createSyncInputSyncConfig(JobSyncConfig config) {
    return new StandardSyncInput()
        .withPrefix(config.getPrefix())
        .withSourceConfiguration(config.getSourceConfiguration())
        .withDestinationConfiguration(config.getDestinationConfiguration())
        .withCatalog(config.getConfiguredAirbyteCatalog())
        .withState(config.getState());
  }

}
