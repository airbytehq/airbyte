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

import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.worker_run.SyncWorkerRunFactories.ResetConnectionWorkerRunFactory;
import io.airbyte.scheduler.worker_run.SyncWorkerRunFactories.SyncWorkerRunFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.nio.file.Path;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SchedulerWorkerRunWithEnvironmentFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerWorkerRunWithEnvironmentFactory.class);

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;
  private final Creator creator;

  public SchedulerWorkerRunWithEnvironmentFactory(final Path workspaceRoot, final ProcessBuilderFactory pbf) {
    this(workspaceRoot, pbf, SchedulerWorkerRunWithEnvironmentFactory::workRunWithEnvironmentCreate);
  }
  public SchedulerWorkerRunWithEnvironmentFactory(final Path workspaceRoot, final ProcessBuilderFactory pbf, Creator creator) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
    this.creator = creator;
  }

  public WorkerRun create(final Job job) {
    final int currentAttempt = job.getAttemptsCount();
    LOGGER.info("job id: {} attempt: {} scope: {} type: {}", job.getId(), currentAttempt, job.getScope(), job.getConfig().getConfigType());

    return switch (job.getConfig().getConfigType()) {
      case GET_SPEC -> creator.create(workspaceRoot, pbf, new GetSpecWorkerRunFactory(), job.getId(), currentAttempt, job.getConfig().getGetSpec());
      case CHECK_CONNECTION_SOURCE, CHECK_CONNECTION_DESTINATION ->
          creator.create(workspaceRoot, pbf, new CheckConnectionWorkerRunFactory(), job.getId(), currentAttempt, job.getConfig().getCheckConnection());
      case DISCOVER_SCHEMA -> creator.create(workspaceRoot, pbf, new DiscoverWorkerRunFactory(), job.getId(), currentAttempt, job.getConfig().getDiscoverCatalog());
      case SYNC -> creator.create(workspaceRoot, pbf, new SyncWorkerRunFactory(), job.getId(), currentAttempt, job.getConfig().getSync());
      case RESET_CONNECTION -> creator.create(workspaceRoot, pbf, new ResetConnectionWorkerRunFactory(), job.getId(), currentAttempt, job.getConfig().getResetConnection());
    };
  }

  public static <T> WorkerRun workRunWithEnvironmentCreate(Path workspaceRoot, ProcessBuilderFactory pbf, WorkerRunFactory<T> workerRunFactory, long jobId, int attempt, T config) {
    return new WorkerRunWithEnvironmentFactory<>(workspaceRoot, pbf, workerRunFactory)
        .create(jobId, attempt, config);
  }

  /*
   * This class is here to help with the testing
   */
  @FunctionalInterface
  interface Creator {

    <T> WorkerRun create(Path workspaceRoot, ProcessBuilderFactory pbf, WorkerRunFactory<T> workerRunFactory, long jobId, int attempt, T config);

  }

}
