/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import com.google.common.collect.Lists;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.instance.configs.jooq.enums.ReleaseStage;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.MetricsRegistry;
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
import java.util.UUID;
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
      final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());
      if (input.isReset()) {

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
        emitSrcIdDstIdToReleaseStagesMetric(standardSync.getSourceId(), standardSync.getDestinationId());

        return new JobCreationOutput(jobId);
      }
    } catch (final JsonValidationException | ConfigNotFoundException | IOException e) {
      throw new RetryableException(e);
    }
  }

  private void emitSrcIdDstIdToReleaseStagesMetric(final UUID srcId, final UUID dstId) throws IOException {
    final var releaseStages = configRepository.getSrcIdAndDestIdToReleaseStages(srcId, dstId);
    if (releaseStages == null || releaseStages.size() == 0) {
      return;
    }

    for (final ReleaseStage stage : releaseStages) {
      if (stage != null) {
        DogStatsDMetricSingleton.count(MetricsRegistry.JOB_CREATED_BY_RELEASE_STAGE, 1, MetricTags.getReleaseStage(stage));
      }
    }
  }

  @Override
  public AttemptCreationOutput createNewAttempt(final AttemptCreationInput input) throws RetryableException {
    try {
      final long jobId = input.getJobId();
      final Job createdJob = jobPersistence.getJob(jobId);

      final WorkerRun workerRun = temporalWorkerRunFactory.create(createdJob);
      final Path logFilePath = workerRun.getJobRoot().resolve(LogClientSingleton.LOG_FILENAME);
      final int persistedAttemptId = jobPersistence.createAttempt(jobId, logFilePath);
      emitJobIdToReleaseStagesMetric(MetricsRegistry.ATTEMPT_CREATED_BY_RELEASE_STAGE, jobId);

      LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, workerRun.getJobRoot());
      return new AttemptCreationOutput(persistedAttemptId);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public AttemptNumberCreationOutput createNewAttemptNumber(final AttemptCreationInput input) throws RetryableException {
    try {
      final long jobId = input.getJobId();
      final Job createdJob = jobPersistence.getJob(jobId);

      final WorkerRun workerRun = temporalWorkerRunFactory.create(createdJob);
      final Path logFilePath = workerRun.getJobRoot().resolve(LogClientSingleton.LOG_FILENAME);
      final int persistedAttemptNumber = jobPersistence.createAttempt(jobId, logFilePath);
      emitJobIdToReleaseStagesMetric(MetricsRegistry.ATTEMPT_CREATED_BY_RELEASE_STAGE, jobId);

      LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, workerRun.getJobRoot());
      return new AttemptNumberCreationOutput(persistedAttemptNumber);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobSuccess(final JobSuccessInput input) {
    try {
      final long jobId = input.getJobId();
      final int attemptId = input.getAttemptId();

      if (input.getStandardSyncOutput() != null) {
        final JobOutput jobOutput = new JobOutput().withSync(input.getStandardSyncOutput());
        jobPersistence.writeOutput(jobId, attemptId, jobOutput);
      } else {
        log.warn("The job {} doesn't have any output for the attempt {}", jobId, attemptId);
      }
      jobPersistence.succeedAttempt(jobId, attemptId);
      emitJobIdToReleaseStagesMetric(MetricsRegistry.ATTEMPT_SUCCEEDED_BY_RELEASE_STAGE, jobId);
      final Job job = jobPersistence.getJob(jobId);

      jobNotifier.successJob(job);
      emitJobIdToReleaseStagesMetric(MetricsRegistry.JOB_SUCCEEDED_BY_RELEASE_STAGE, jobId);
      trackCompletion(job, JobStatus.SUCCEEDED);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobSuccessWithAttemptNumber(final JobSuccessInputWithAttemptNumber input) {
    jobSuccess(new JobSuccessInput(
        input.getJobId(),
        input.getAttemptNumber(),
        input.getStandardSyncOutput()));
  }

  @Override
  public void jobFailure(final JobFailureInput input) {
    try {
      final var jobId = input.getJobId();
      jobPersistence.failJob(jobId);
      final Job job = jobPersistence.getJob(jobId);

      jobNotifier.failJob(input.getReason(), job);
      emitJobIdToReleaseStagesMetric(MetricsRegistry.JOB_FAILED_BY_RELEASE_STAGE, jobId);
      trackCompletion(job, JobStatus.FAILED);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void attemptFailure(final AttemptFailureInput input) {
    try {
      final int attemptId = input.getAttemptId();
      final long jobId = input.getJobId();
      final AttemptFailureSummary failureSummary = input.getAttemptFailureSummary();

      jobPersistence.failAttempt(jobId, attemptId);
      jobPersistence.writeAttemptFailureSummary(jobId, attemptId, failureSummary);

      if (input.getStandardSyncOutput() != null) {
        final JobOutput jobOutput = new JobOutput().withSync(input.getStandardSyncOutput());
        jobPersistence.writeOutput(jobId, attemptId, jobOutput);
      }

      emitJobIdToReleaseStagesMetric(MetricsRegistry.ATTEMPT_FAILED_BY_RELEASE_STAGE, jobId);
      for (final FailureReason reason : failureSummary.getFailures()) {
        DogStatsDMetricSingleton.count(MetricsRegistry.ATTEMPT_FAILED_BY_FAILURE_ORIGIN, 1, MetricTags.getFailureOrigin(reason.getFailureOrigin()));
      }
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void attemptFailureWithAttemptNumber(final AttemptNumberFailureInput input) {
    attemptFailure(new AttemptFailureInput(
        input.getJobId(),
        input.getAttemptNumber(),
        input.getStandardSyncOutput(),
        input.getAttemptFailureSummary()));
  }

  @Override
  public void jobCancelled(final JobCancelledInput input) {
    try {
      final long jobId = input.getJobId();
      jobPersistence.cancelJob(jobId);
      final int attemptId = input.getAttemptId();
      jobPersistence.failAttempt(jobId, attemptId);
      jobPersistence.writeAttemptFailureSummary(jobId, attemptId, input.getAttemptFailureSummary());

      final Job job = jobPersistence.getJob(jobId);
      trackCompletion(job, JobStatus.FAILED);
      emitJobIdToReleaseStagesMetric(MetricsRegistry.JOB_CANCELLED_BY_RELEASE_STAGE, jobId);
      jobNotifier.failJob("Job was cancelled", job);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Override
  public void jobCancelledWithAttemptNumber(final JobCancelledInputWithAttemptNumber input) {
    jobCancelled(new JobCancelledInput(
        input.getJobId(),
        input.getAttemptNumber(),
        input.getAttemptFailureSummary()));
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

  private void emitJobIdToReleaseStagesMetric(final MetricsRegistry metric, final long jobId) throws IOException {
    final var releaseStages = configRepository.getJobIdToReleaseStages(jobId);
    if (releaseStages == null || releaseStages.size() == 0) {
      return;
    }

    for (final ReleaseStage stage : releaseStages) {
      if (stage != null) {
        DogStatsDMetricSingleton.count(metric, 1, MetricTags.getReleaseStage(stage));
      }
    }
  }

  private void trackCompletion(final Job job, final io.airbyte.workers.JobStatus status) {
    jobTracker.trackSync(job, Enums.convertTo(status, JobState.class));
  }

}
