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

package io.airbyte.scheduler.app;

import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.time.Instant;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobRetrier implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobRetrier.class);
  private static final int MAX_SYNC_JOB_ATTEMPTS = 3;
  private static final int RETRY_WAIT_MINUTES = 1;

  private final JobPersistence persistence;
  private final Supplier<Instant> timeSupplier;

  public JobRetrier(JobPersistence jobPersistence, Supplier<Instant> timeSupplier) {
    this.persistence = jobPersistence;
    this.timeSupplier = timeSupplier;
  }

  @Override
  public void run() {
    LOGGER.info("Running Job Retrier...");

    final AtomicInteger failedJobs = new AtomicInteger();
    final AtomicInteger retriedJobs = new AtomicInteger();
    final List<Job> incompleteJobs = incompleteJobs();

    incompleteJobs.forEach(job -> {
      if (hasReachedMaxAttempt(job)) {
        failJob(job);
        failedJobs.incrementAndGet();
      } else if (shouldRetry(job)) {
        retriedJobs.incrementAndGet();
        resetJob(job);
      }
    });

    LOGGER.info("Completed Job Retrier...");
    LOGGER.info("Job Retrier Summary. Incomplete jobs: {}, Job set to retry: {}, Jobs set to failed: {}",
        incompleteJobs.size(),
        failedJobs.get(),
        retriedJobs.get());
  }

  private List<Job> incompleteJobs() {
    try {
      return persistence.listJobsWithStatus(JobStatus.INCOMPLETE);
    } catch (IOException e) {
      throw new RuntimeException("failed to fetch failed jobs", e);
    }
  }

  private boolean hasReachedMaxAttempt(Job job) {
    if (Job.REPLICATION_TYPES.contains(job.getConfigType())) {
      return job.getAttemptsCount() >= MAX_SYNC_JOB_ATTEMPTS;
    } else {
      return job.getAttemptsCount() >= 1;
    }
  }

  private boolean shouldRetry(Job job) {
    if (Job.REPLICATION_TYPES.contains(job.getConfigType())) {
      long lastRun = job.getUpdatedAtInSecond();
      // todo (cgardens) - use exponential backoff.
      return lastRun < timeSupplier.get().getEpochSecond() - TimeUnit.MINUTES.toSeconds(RETRY_WAIT_MINUTES);
    } else {
      return false;
    }
  }

  private void failJob(Job job) {
    try {
      persistence.failJob(job.getId());
    } catch (IOException e) {
      throw new RuntimeException("failed to update status for job: " + job.getId(), e);
    }
  }

  private void resetJob(Job job) {
    try {
      persistence.resetJob(job.getId());
    } catch (IOException e) {
      throw new RuntimeException("failed to update status for job: " + job.getId(), e);
    }
  }

}
