/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
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
      jobPersistence.succeedAttempt(input.getJobId(), input.getAttemptId());
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobFailure(final JobFailureInput input) {
    try {
      jobPersistence.failJob(input.getJobId());
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void attemptFailure(final AttemptFailureInput input) {
    try {
      jobPersistence.failAttempt(input.getJobId(), input.getAttemptId());
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobCancelled(final JobCancelledInput input) {
    try {
      jobPersistence.cancelJob(input.getJobId());
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

}
