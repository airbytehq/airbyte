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

import io.dataline.config.JobConfig;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import java.io.IOException;
import java.time.Instant;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import java.util.stream.Stream;

public class JobRetryer implements Runnable {

  private static final int MAX_ATTEMPTS = 5;
  private static final int RETRY_WAIT_MINUTES = 1;

  private final SchedulerPersistence persistence;
  private final Supplier<Instant> timeSupplier;

  public JobRetryer(SchedulerPersistence schedulerPersistence, Supplier<Instant> timeSupplier) {
    this.persistence = schedulerPersistence;
    this.timeSupplier = timeSupplier;
  }

  @Override
  public void run() {
    listFailedJobs()
        .forEach(job -> {
          if (shouldCancel(job)) {
            setSetStatusTo(job, JobStatus.CANCELLED);
            return;
          }

          if (shouldRetry(job)) {
            setSetStatusTo(job, JobStatus.PENDING);
          }
        });
  }

  private Stream<Job> listFailedJobs() {
    try {
      return persistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED).stream();
    } catch (IOException e) {
      throw new RuntimeException("failed to fetch failed jobs", e);
    }
  }

  private boolean shouldCancel(Job job) {
    return job.getAttempts() >= MAX_ATTEMPTS;
  }

  private boolean shouldRetry(Job job) {
    long lastRun = job.getUpdatedAtInSecond();
    // todo (cgardens) - use exponential backoff.
    return lastRun < timeSupplier.get().getEpochSecond() - TimeUnit.MINUTES.toSeconds(RETRY_WAIT_MINUTES);
  }

  private void setSetStatusTo(Job job, JobStatus status) {
    try {
      persistence.updateStatus(job.getId(), status);
    } catch (IOException e) {
      throw new RuntimeException("failed to update status for job: " + job.getId(), e);
    }
  }

}
