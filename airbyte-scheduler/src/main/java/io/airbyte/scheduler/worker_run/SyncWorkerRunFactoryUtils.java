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

import io.airbyte.config.StandardSyncInput;
import io.airbyte.scheduler.worker_run.BaseWorkerRunFactory.IntegrationLauncherFactory;
import io.airbyte.scheduler.worker_run.BaseWorkerRunFactory.WorkerRunCreator;
import io.airbyte.workers.DefaultSyncWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessBuilderFactory;
import io.airbyte.workers.protocols.airbyte.AirbyteMessageTracker;
import io.airbyte.workers.protocols.airbyte.AirbyteSource;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteDestination;
import io.airbyte.workers.protocols.airbyte.DefaultAirbyteMapper;
import io.airbyte.workers.wrappers.JobOutputSyncWorker;
import java.nio.file.Path;

public class SyncWorkerRunFactoryUtils {

  public static WorkerRun createSyncWorker(long jobId,
                                           int attempt,
                                           AirbyteSource airbyteSource,
                                           String destinationDockerImage,
                                           StandardSyncInput syncInput,
                                           Path jobRoot,
                                           ProcessBuilderFactory pbf,
                                           IntegrationLauncherFactory integrationLauncherFactory,

                                           WorkerRunCreator workerRunCreator) {
    final IntegrationLauncher destinationLauncher = integrationLauncherFactory.create(jobId, attempt, destinationDockerImage, pbf);

    return workerRunCreator.create(
        jobRoot,
        syncInput,
        new JobOutputSyncWorker(
            new DefaultSyncWorker(
                jobId,
                attempt,
                airbyteSource,
                new DefaultAirbyteMapper(),
                new DefaultAirbyteDestination(destinationLauncher),
                new AirbyteMessageTracker(),
                NormalizationRunnerFactory.create(
                    destinationDockerImage,
                    pbf,
                    syncInput.getDestinationConfiguration()))));
  }

}
