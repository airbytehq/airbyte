/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.commons.enums.Enums;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobOutput;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.temporal.exception.RetryableException;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import io.airbyte.workers.worker_run.WorkerRun;
import java.io.IOException;
import java.nio.file.Path;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;

@AllArgsConstructor
@Slf4j
public class JobCreationAndStatusUpdateActivityImpl implements JobCreationAndStatusUpdateActivity {

  private final SyncJobFactory jobFactory;
  private final JobPersistence jobPersistence;
  private final TemporalWorkerRunFactory temporalWorkerRunFactory;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final JobNotifier jobNotifier;
  private final JobTracker jobTracker;

  @Override
  public JobCreationOutput createNewJob(final JobCreationInput input) {
    final long jobId = jobFactory.create(input.getConnectionId());

    log.info("New job created, with id: " + jobId);

    return new JobCreationOutput(jobId);
  }

  @Override
  public AttemptCreationOutput createNewAttempt(final AttemptCreationInput input) throws RetryableException {
    try {
      final Job createdJob = jobPersistence.getJob(input.getJobId());

      final WorkerRun workerRun = temporalWorkerRunFactory.create(createdJob);
      final Path logFilePath = workerRun.getJobRoot().resolve(LogClientSingleton.LOG_FILENAME);
      final int persistedAttemptId = jobPersistence.createAttempt(input.getJobId(), logFilePath);

      LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, workerRun.getJobRoot());

      return new AttemptCreationOutput(persistedAttemptId);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobSuccess(final JobSuccessInput input) {
    try {
      if (input.getStandardSyncOutput() != null) {
        final JobOutput jobOutput = new JobOutput().withSync(input.getStandardSyncOutput());
        jobPersistence.writeOutput(input.getJobId(), input.getAttemptId(), jobOutput);
      } else {
        log.warn("The job {} doesn't have an input for the attempt {}", input.getJobId(), input.getAttemptId());
      }
      jobPersistence.succeedAttempt(input.getJobId(), input.getAttemptId());
      final Job job = jobPersistence.getJob(input.getJobId());
      jobNotifier.successJob(job);
      trackCompletion(job, JobStatus.SUCCEEDED);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobFailure(final JobFailureInput input) {
    try {
      jobPersistence.failJob(input.getJobId());
      final Job job = jobPersistence.getJob(input.getJobId());
      jobNotifier.failJob(input.getReason(), job);
      trackCompletion(job, JobStatus.FAILED);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void attemptFailure(final AttemptFailureInput input) {
    try {
      jobPersistence.failAttempt(input.getJobId(), input.getAttemptId());
      final Job job = jobPersistence.getJob(input.getJobId());
      jobNotifier.failJob("Job was cancelled", job);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobCancelled(final JobCancelledInput input) {
    try {
      jobPersistence.cancelJob(input.getJobId());
      final Job job = jobPersistence.getJob(input.getJobId());
      trackCompletion(job, JobStatus.FAILED);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void reportJobStart(final ReportJobStartInput input) {
    try {
      final Job job = jobPersistence.getJob(input.getJobId());
      jobTracker.trackSync(job, JobState.STARTED);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  private void trackCompletion(final Job job, final io.airbyte.workers.JobStatus status) {
    jobTracker.trackSync(job, Enums.convertTo(status, JobState.class));
  }

}
