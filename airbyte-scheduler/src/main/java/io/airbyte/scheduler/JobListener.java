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

import com.google.common.annotations.VisibleForTesting;
import com.google.common.base.Charsets;
import com.google.common.base.Strings;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableMap.Builder;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.concurrency.LifecycledCallable;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.helpers.ScheduleHelpers;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConstants;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

public class JobListener implements Runnable {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobListener.class);

  private final JobPersistence persistence;
  private final JobTracking jobTracking;

  public JobListener(final JobPersistence persistence, final JobTracking jobTracking) {
    this.persistence = persistence;
    this.jobTracking = jobTracking;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-listener...");

      final List<Job> runningJobs = persistence.getRunningJobs();

      for(final Job job : runningJobs) {
        persistProgress(job);
      }

      LOGGER.info("Completed Job-Submitter...");
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  @VisibleForTesting
  void persistProgress(Job job) {
    final Object temporalJob = temporalClient.getJob(job.getTemporalId());
    final List<Object> temporalAttempts = temporalClient.getAttempts(job.getTemporalId());

    for(final Object temporalAttempt : temporalAttempts) {
      // if we haven't seen the temporal attempt before, add it to our own persistence.
      if(!job.getAttempts().stream().map(Attempt::getTemporalId).contains(temporalAttempt.getAttemptId())) {
        persistence.createAttempt(jobId, temporalAttempt.getAttemptId(), temporalAttempt.getLogPath());
      }
    }

    final JobStatus jobStatus = mapTemporalStatusToJobStatus(temporalClient.getJobStatus(temporalJob.getStatus()));
    persistence.setStatus(job.getId(), jobStatus);

    if(JobStatus.TERMINAL_STATUSES.contains(jobStatus)) {
      jobTracking.trackCompletion(job, jobStatus);
    }
  }
}
