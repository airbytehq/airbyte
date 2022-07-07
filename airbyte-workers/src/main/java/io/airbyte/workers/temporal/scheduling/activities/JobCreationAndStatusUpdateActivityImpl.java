/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
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
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_error_reporter.JobErrorReporter;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.run.TemporalWorkerRunFactory;
import io.airbyte.workers.run.WorkerRun;
import io.airbyte.workers.temporal.exception.RetryableException;
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
  private final StreamResetPersistence streamResetPersistence;
  private final JobErrorReporter jobErrorReporter;

  @Override
  public JobCreationOutput createNewJob(final JobCreationInput input) {
    try {
      // Fail non-terminal jobs first to prevent this activity from repeatedly trying to create a new job
      // and failing, potentially resulting in the workflow ending up in a quarantined state.
      // Another non-terminal job is not expected to exist at this point in the normal case, but this
      // could happen in special edge cases for example when migrating to this from the old scheduler.
      failNonTerminalJobs(input.getConnectionId());

      final StandardSync standardSync = configRepository.getStandardSync(input.getConnectionId());
      final List<StreamDescriptor> streamsToReset = streamResetPersistence.getStreamResets(input.getConnectionId());
      log.info("Found the following streams to reset for connection {}: {}", input.getConnectionId(), streamsToReset);

      if (!streamsToReset.isEmpty()) {
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
            jobCreator.createResetConnectionJob(destination, standardSync, destinationImageName, standardSyncOperations, streamsToReset);

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
        MetricClientFactory.getMetricClient().count(OssMetricsRegistry.JOB_CREATED_BY_RELEASE_STAGE, 1, MetricTags.getReleaseStage(stage));
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
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.ATTEMPT_CREATED_BY_RELEASE_STAGE, jobId);

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
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.ATTEMPT_CREATED_BY_RELEASE_STAGE, jobId);

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
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.ATTEMPT_SUCCEEDED_BY_RELEASE_STAGE, jobId);
      final Job job = jobPersistence.getJob(jobId);

      jobNotifier.successJob(job);
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.JOB_SUCCEEDED_BY_RELEASE_STAGE, jobId);
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
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.JOB_FAILED_BY_RELEASE_STAGE, jobId);
      trackCompletion(job, JobStatus.FAILED);

      final UUID connectionId = UUID.fromString(job.getScope());
      job.getLastFailedAttempt().flatMap(Attempt::getFailureSummary)
          .ifPresent(failureSummary -> jobErrorReporter.reportSyncJobFailure(connectionId, failureSummary, job.getConfig().getSync()));
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

      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.ATTEMPT_FAILED_BY_RELEASE_STAGE, jobId);
      for (final FailureReason reason : failureSummary.getFailures()) {
        MetricClientFactory.getMetricClient().count(OssMetricsRegistry.ATTEMPT_FAILED_BY_FAILURE_ORIGIN, 1,
            MetricTags.getFailureOrigin(reason.getFailureOrigin()));
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
      final int attemptId = input.getAttemptId();
      jobPersistence.failAttempt(jobId, attemptId);
      jobPersistence.writeAttemptFailureSummary(jobId, attemptId, input.getAttemptFailureSummary());
      jobPersistence.cancelJob(jobId);

      final Job job = jobPersistence.getJob(jobId);
      trackCompletion(job, JobStatus.FAILED);
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.JOB_CANCELLED_BY_RELEASE_STAGE, jobId);
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

  @Override
  public void ensureCleanJobState(final EnsureCleanJobStateInput input) {
    failNonTerminalJobs(input.getConnectionId());
  }

  private void failNonTerminalJobs(final UUID connectionId) {
    try {
      final List<Job> jobs = jobPersistence.listJobsForConnectionWithStatuses(connectionId, Job.REPLICATION_TYPES,
          io.airbyte.scheduler.models.JobStatus.NON_TERMINAL_STATUSES);
      for (final Job job : jobs) {
        final long jobId = job.getId();

        // fail all non-terminal attempts
        for (final Attempt attempt : job.getAttempts()) {
          if (Attempt.isAttemptInTerminalState(attempt)) {
            continue;
          }

          // the Attempt object 'id' is actually the value of the attempt_number column in the db
          final int attemptNumber = (int) attempt.getId();
          log.info("Failing non-terminal attempt {} for non-terminal job {}", attemptNumber, jobId);
          jobPersistence.failAttempt(jobId, attemptNumber);
          jobPersistence.writeAttemptFailureSummary(jobId, attemptNumber,
              FailureHelper.failureSummaryForTemporalCleaningJobState(jobId, attemptNumber));
        }

        log.info("Failing non-terminal job {}", jobId);
        jobPersistence.failJob(jobId);

        final Job failedJob = jobPersistence.getJob(jobId);
        jobNotifier.failJob("Failing job in order to start from clean job state for new temporal workflow run.", failedJob);
        trackCompletion(failedJob, JobStatus.FAILED);
      }
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  private void emitJobIdToReleaseStagesMetric(final OssMetricsRegistry metric, final long jobId) throws IOException {
    final var releaseStages = configRepository.getJobIdToReleaseStages(jobId);
    if (releaseStages == null || releaseStages.size() == 0) {
      return;
    }

    for (final ReleaseStage stage : releaseStages) {
      if (stage != null) {
        MetricClientFactory.getMetricClient().count(metric, 1, MetricTags.getReleaseStage(stage));
      }
    }
  }

  private void trackCompletion(final Job job, final io.airbyte.workers.JobStatus status) {
    jobTracker.trackSync(job, Enums.convertTo(status, JobState.class));
  }

}
