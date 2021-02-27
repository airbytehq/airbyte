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

package io.airbyte.scheduler;

import io.airbyte.scheduler.worker_run_factories.WorkerRunAssembly;
import io.airbyte.scheduler.worker_run_factories.CheckConnectionWorkerRunFactory;
import io.airbyte.scheduler.worker_run_factories.DiscoverWorkerRunFactory;
import io.airbyte.scheduler.worker_run_factories.GetSpecWorkerRunFactory;
import io.airbyte.scheduler.worker_run_factories.SyncWorkerRunFactories.ResetConnectionWorkerRunFactory;
import io.airbyte.scheduler.worker_run_factories.SyncWorkerRunFactories.SyncWorkerRunFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class is a runnable that give a job id and db connection figures out how to run the
 * appropriate worker for a given job.
 */
public class SchedulerWorkerRunAssembly {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerWorkerRunAssembly.class);

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;

  public SchedulerWorkerRunAssembly(final Path workspaceRoot,
                                    final ProcessBuilderFactory pbf) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
  }

  public WorkerRun create(final Job job) {
    final int currentAttempt = job.getAttemptsCount();
    LOGGER.info("job id: {} attempt: {} scope: {} type: {}", job.getId(), currentAttempt, job.getScope(), job.getConfig().getConfigType());

    final Path jobRoot = workspaceRoot.resolve(String.valueOf(job.getId())).resolve(String.valueOf(currentAttempt));
    LOGGER.info("job root: {}", jobRoot);

    return switch (job.getConfig().getConfigType()) {
      case GET_SPEC -> new WorkerRunAssembly<>(workspaceRoot, pbf, new GetSpecWorkerRunFactory())
          .create(job.getId(), currentAttempt, job.getConfig().getGetSpec());
      case CHECK_CONNECTION_SOURCE, CHECK_CONNECTION_DESTINATION -> new WorkerRunAssembly<>(workspaceRoot, pbf,
          new CheckConnectionWorkerRunFactory()).create(job.getId(), currentAttempt, job.getConfig().getCheckConnection());
      case DISCOVER_SCHEMA -> new WorkerRunAssembly<>(workspaceRoot, pbf, new DiscoverWorkerRunFactory())
          .create(job.getId(), currentAttempt, job.getConfig().getDiscoverCatalog());
      case SYNC -> new WorkerRunAssembly<>(workspaceRoot, pbf, new SyncWorkerRunFactory())
          .create(job.getId(), currentAttempt, job.getConfig().getSync());
      case RESET_CONNECTION -> new WorkerRunAssembly<>(workspaceRoot, pbf, new ResetConnectionWorkerRunFactory())
          .create(job.getId(), currentAttempt, job.getConfig().getResetConnection());
    };
  }

}
