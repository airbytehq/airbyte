/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import com.google.common.collect.Lists;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.temporal.exception.RetryableException;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import io.airbyte.workers.worker_run.WorkerRun;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
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
  private final ConfigRepository configRepository;
  private final JobCreator jobCreator;

  @Override
  public JobCreationOutput createNewJob(final JobCreationInput input) {
    try {
      if (input.isReset()) {
        final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());

        final DestinationConnection destination = configRepository.getDestinationConnection(standardSync.getDestinationId());

        final StandardDestinationDefinition destinationDef =
            configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
        final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

        final List<StandardSyncOperation> standardSyncOperations = Lists.newArrayList();
        for (final var operationId : standardSync.getOperationIds()) {
          final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
          standardSyncOperations.add(standardSyncOperation);
        }

        final Optional<Long> jobIdOptional =
            jobCreator.createResetConnectionJob(destination, standardSync, destinationImageName, standardSyncOperations);

        final long jobId = jobIdOptional.isEmpty()
            ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
            : jobIdOptional.get();

        return new JobCreationOutput(jobId);
      } else {
        final long jobId = jobFactory.create(input.getConnectionId());

        log.info("New job created, with id: " + jobId);

        return new JobCreationOutput(jobId);
      }
    } catch (final JsonValidationException | ConfigNotFoundException | IOException e) {
      throw new RetryableException(e);
    }
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
        log.warn("The job {} doesn't have any output for the attempt {}", input.getJobId(), input.getAttemptId());
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
      jobPersistence.writeAttemptFailureSummary(input.getJobId(), input.getAttemptId(), input.getAttemptFailureSummary());

      if (input.getStandardSyncOutput() != null) {
        final JobOutput jobOutput = new JobOutput().withSync(input.getStandardSyncOutput());
        jobPersistence.writeOutput(input.getJobId(), input.getAttemptId(), jobOutput);
      } else {
        log.warn("The job {} doesn't have any output for the attempt {}", input.getJobId(), input.getAttemptId());
      }

    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobCancelled(final JobCancelledInput input) {
    try {
      jobPersistence.cancelJob(input.getJobId());
      if (input.getAttemptFailureSummary() != null) {
        jobPersistence.writeAttemptFailureSummary(input.getJobId(), input.getAttemptId(), input.getAttemptFailureSummary());
      }
      final Job job = jobPersistence.getJob(input.getJobId());
      trackCompletion(job, JobStatus.FAILED);
      jobNotifier.failJob("Job was cancelled", job);
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
