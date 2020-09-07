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

package io.dataline.scheduler;

import io.dataline.commons.concurrency.LifecycledCallable;
import io.dataline.config.JobOutput;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import io.dataline.workers.OutputAndStatus;
import java.util.Optional;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

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
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  private void submitJob(Job job) {
    threadPool.submit(new LifecycledCallable.Builder<>((Callable<OutputAndStatus<JobOutput>>) workerRunFactory.create(job))
        .setOnStart(() -> persistence.updateStatus(job.getId(), JobStatus.RUNNING))
        .setOnSuccess(output -> {
          if (output.getOutput().isPresent()) {
            persistence.writeOutput(job.getId(), output.getOutput().get());
          }
          persistence.updateStatus(job.getId(), getStatus(output));
        })
        .setOnException(noop -> persistence.updateStatus(job.getId(), JobStatus.FAILED)).build());
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
