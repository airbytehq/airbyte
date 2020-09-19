/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

import io.airbyte.commons.concurrency.LifecycledCallable;
import io.airbyte.scheduler.persistence.SchedulerPersistence;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.WorkerConstants;
import java.nio.file.Path;
import java.util.Optional;
import java.util.concurrent.ExecutorService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class JobSubmitter implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobSubmitter.class);

  private final ExecutorService threadPool;
  private final SchedulerPersistence persistence;
  private final WorkerRunFactory workerRunFactory;

  public JobSubmitter(final ExecutorService threadPool,
                      final SchedulerPersistence persistence,
                      final WorkerRunFactory workerRunFactory) {
    this.threadPool = threadPool;
    this.persistence = persistence;
    this.workerRunFactory = workerRunFactory;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-submitter...");

      Optional<Job> oldestPendingJob = persistence.getOldestPendingJob();

      oldestPendingJob.ifPresent(this::submitJob);

      LOGGER.info("Completed job-submitter...");
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  private void submitJob(Job job) {
    final WorkerRun workerRun = workerRunFactory.create(job);
    threadPool.submit(new LifecycledCallable.Builder<>(workerRun)
        .setOnStart(() -> {
          persistence.updateStatus(job.getId(), JobStatus.RUNNING);
          final Path logFilePath = workerRun.getJobRoot().resolve(WorkerConstants.LOG_FILENAME);
          persistence.updateLogPath(job.getId(), logFilePath);
          persistence.incrementAttempts(job.getId());
          MDC.put("context", "worker");
          MDC.put("job_id", String.valueOf(job.getId()));
          MDC.put("job_root", logFilePath.getParent().toString());
          MDC.put("job_log_filename", logFilePath.getFileName().toString());
        })
        .setOnSuccess(output -> {
          if (output.getOutput().isPresent()) {
            persistence.writeOutput(job.getId(), output.getOutput().get());
          }
          persistence.updateStatus(job.getId(), getStatus(output));
        })
        .setOnException(noop -> persistence.updateStatus(job.getId(), JobStatus.FAILED))
        .setOnFinish(MDC::clear)
        .build());
  }

  private JobStatus getStatus(OutputAndStatus<?> output) {
    switch (output.getStatus()) {
      case SUCCESSFUL:
        return JobStatus.COMPLETED;
      case FAILED:
        return JobStatus.FAILED;
      default:
        throw new RuntimeException("Unknown state " + output.getStatus());
    }
  }

}
