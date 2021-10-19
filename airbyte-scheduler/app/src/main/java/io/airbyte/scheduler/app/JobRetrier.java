/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobNotifier;
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
  private static final int RETRY_WAIT_MINUTES = 1;

  private final JobPersistence persistence;
  private final Supplier<Instant> timeSupplier;
  private final JobNotifier jobNotifier;
  private final int maxSyncJobAttempts;

  public JobRetrier(final JobPersistence jobPersistence,
                    final Supplier<Instant> timeSupplier,
                    final JobNotifier jobNotifier,
                    final int maxSyncJobAttempts) {
    this.persistence = jobPersistence;
    this.timeSupplier = timeSupplier;
    this.jobNotifier = jobNotifier;
    this.maxSyncJobAttempts = maxSyncJobAttempts;
  }

  @Override
  public void run() {
    LOGGER.debug("Running Job Retrier...");

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

    LOGGER.debug("Completed Job Retrier...");

    final int incompleteJobCount = incompleteJobs.size();
    final int failedJobCount = failedJobs.get();
    final int retriedJobCount = retriedJobs.get();
    if (incompleteJobCount > 0 || failedJobCount > 0 || retriedJobCount > 0) {
      LOGGER.info("Job Retrier Summary. Incomplete jobs: {}, Job set to retry: {}, Jobs set to failed: {}",
          incompleteJobs.size(),
          failedJobs.get(),
          retriedJobs.get());
    }
  }

  private List<Job> incompleteJobs() {
    try {
      return persistence.listJobsWithStatus(JobStatus.INCOMPLETE);
    } catch (final IOException e) {
      throw new RuntimeException("failed to fetch failed jobs", e);
    }
  }

  private boolean hasReachedMaxAttempt(final Job job) {
    if (Job.REPLICATION_TYPES.contains(job.getConfigType())) {
      return job.getAttemptsCount() >= maxSyncJobAttempts;
    } else {
      return job.getAttemptsCount() >= 1;
    }
  }

  private boolean shouldRetry(final Job job) {
    if (Job.REPLICATION_TYPES.contains(job.getConfigType())) {
      final long lastRun = job.getUpdatedAtInSecond();
      // todo (cgardens) - use exponential backoff.
      return lastRun < timeSupplier.get().getEpochSecond() - TimeUnit.MINUTES.toSeconds(RETRY_WAIT_MINUTES);
    } else {
      return false;
    }
  }

  private void failJob(final Job job) {
    try {
      jobNotifier.failJob("max retry limit was reached", job);
      persistence.failJob(job.getId());
    } catch (final IOException e) {
      throw new RuntimeException("failed to update status for job: " + job.getId(), e);
    }
  }

  private void resetJob(final Job job) {
    try {
      persistence.resetJob(job.getId());
    } catch (final IOException e) {
      throw new RuntimeException("failed to update status for job: " + job.getId(), e);
    }
  }

}
