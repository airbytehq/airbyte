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
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.EmptyAirbyteSource;
import java.nio.file.Path;

public class ResetConnectionWorkerRunFactory extends BaseWorkerRunFactory<JobResetConnectionConfig>
    implements WorkerRunFactory<JobResetConnectionConfig> {

  public ResetConnectionWorkerRunFactory() {
    super();
  }

  @VisibleForTesting
  ResetConnectionWorkerRunFactory(IntegrationLauncherFactory integrationLauncherFactory, WorkerRunCreator workerRunCreator) {
    super(integrationLauncherFactory, workerRunCreator);
  }

  @Override
  public WorkerRun create(Path jobRoot, ProcessBuilderFactory pbf, long jobId, int attempt, JobResetConnectionConfig config) {
    return SyncWorkerRunFactoryUtils.createSyncWorker(
        jobId,
        attempt,
        new EmptyAirbyteSource(),
        config.getDestinationDockerImage(),
        createSyncInputFromResetConfig(config),
        jobRoot,
        pbf,
        integrationLauncherFactory,
        workerRunCreator);
  }

  private static StandardSyncInput createSyncInputFromResetConfig(JobResetConnectionConfig config) {
    return new StandardSyncInput()
        .withPrefix(config.getPrefix())
        .withSourceConfiguration(Jsons.emptyObject())
        .withDestinationConfiguration(config.getDestinationConfiguration())
        .withCatalog(config.getConfiguredAirbyteCatalog());
  }

}
