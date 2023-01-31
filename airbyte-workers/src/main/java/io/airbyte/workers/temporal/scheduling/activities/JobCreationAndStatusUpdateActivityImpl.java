/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.config.JobConfig.ConfigType.SYNC;
import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.ATTEMPT_NUMBER_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTION_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.FAILURE_ORIGINS_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.FAILURE_TYPES_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;
import static io.airbyte.persistence.job.models.AttemptStatus.FAILED;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Lists;
import datadog.trace.api.Trace;
import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.commons.util.MoreLists;
import io.airbyte.commons.version.Version;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.db.instance.configs.jooq.generated.enums.ReleaseStage;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.metrics.lib.MetricAttribute;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricTags;
import io.airbyte.metrics.lib.OssMetricsRegistry;
import io.airbyte.persistence.job.JobCreator;
import io.airbyte.persistence.job.JobNotifier;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.errorreporter.SyncJobReportingContext;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.factory.SyncJobFactory;
import io.airbyte.persistence.job.models.Attempt;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.airbyte.persistence.job.tracker.JobTracker.JobState;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.helper.FailureHelper;
import io.airbyte.workers.run.TemporalWorkerRunFactory;
import io.airbyte.workers.run.WorkerRun;
import io.micronaut.context.annotation.Requires;
import io.micronaut.core.util.CollectionUtils;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.OptionalLong;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@Singleton
@Requires(env = WorkerMode.CONTROL_PLANE)
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
  private final OAuthConfigSupplier oAuthConfigSupplier;

  public JobCreationAndStatusUpdateActivityImpl(final SyncJobFactory jobFactory,
                                                final JobPersistence jobPersistence,
                                                final TemporalWorkerRunFactory temporalWorkerRunFactory,
                                                final WorkerEnvironment workerEnvironment,
                                                final LogConfigs logConfigs,
                                                final JobNotifier jobNotifier,
                                                final JobTracker jobTracker,
                                                final ConfigRepository configRepository,
                                                final JobCreator jobCreator,
                                                final StreamResetPersistence streamResetPersistence,
                                                final JobErrorReporter jobErrorReporter,
                                                final OAuthConfigSupplier oAuthConfigSupplier) {
    this.jobFactory = jobFactory;
    this.jobPersistence = jobPersistence;
    this.temporalWorkerRunFactory = temporalWorkerRunFactory;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.jobNotifier = jobNotifier;
    this.jobTracker = jobTracker;
    this.configRepository = configRepository;
    this.jobCreator = jobCreator;
    this.streamResetPersistence = streamResetPersistence;
    this.jobErrorReporter = jobErrorReporter;
    this.oAuthConfigSupplier = oAuthConfigSupplier;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public JobCreationOutput createNewJob(final JobCreationInput input) {
    try {
      ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, input.getConnectionId()));

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

        final JsonNode destinationConfiguration = oAuthConfigSupplier.injectDestinationOAuthParameters(
            destination.getDestinationDefinitionId(),
            destination.getWorkspaceId(),
            destination.getConfiguration());
        destination.setConfiguration(destinationConfiguration);

        final StandardDestinationDefinition destinationDef =
            configRepository.getStandardDestinationDefinition(destination.getDestinationDefinitionId());
        final String destinationImageName = DockerUtils.getTaggedImageName(destinationDef.getDockerRepository(), destinationDef.getDockerImageTag());

        final List<StandardSyncOperation> standardSyncOperations = Lists.newArrayList();
        for (final var operationId : standardSync.getOperationIds()) {
          final StandardSyncOperation standardSyncOperation = configRepository.getStandardSyncOperation(operationId);
          standardSyncOperations.add(standardSyncOperation);
        }

        final Optional<Long> jobIdOptional =
            jobCreator.createResetConnectionJob(destination, standardSync, destinationImageName, new Version(destinationDef.getProtocolVersion()),
                destinationDef.getCustom(),
                standardSyncOperations, streamsToReset);

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
    if (releaseStages == null || releaseStages.isEmpty()) {
      return;
    }

    for (final ReleaseStage stage : releaseStages) {
      if (stage != null) {
        MetricClientFactory.getMetricClient().count(OssMetricsRegistry.JOB_CREATED_BY_RELEASE_STAGE, 1,
            new MetricAttribute(MetricTags.RELEASE_STAGE, MetricTags.getReleaseStage(stage)));
      }
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public AttemptNumberCreationOutput createNewAttemptNumber(final AttemptCreationInput input) throws RetryableException {
    try {
      final long jobId = input.getJobId();
      ApmTraceUtils.addTagsToTrace(Map.of(JOB_ID_KEY, jobId));
      final Job job = jobPersistence.getJob(jobId);

      final WorkerRun workerRun = temporalWorkerRunFactory.create(job);
      final Path logFilePath = workerRun.getJobRoot().resolve(LogClientSingleton.LOG_FILENAME);
      final int persistedAttemptNumber = jobPersistence.createAttempt(jobId, logFilePath);
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.ATTEMPT_CREATED_BY_RELEASE_STAGE, jobId);
      emitAttemptCreatedEvent(job, persistedAttemptNumber);

      LogClientSingleton.getInstance().setJobMdc(workerEnvironment, logConfigs, workerRun.getJobRoot());
      return new AttemptNumberCreationOutput(persistedAttemptNumber);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void jobSuccessWithAttemptNumber(final JobSuccessInputWithAttemptNumber input) {
    ApmTraceUtils.addTagsToTrace(
        Map.of(ATTEMPT_NUMBER_KEY, input.getAttemptNumber(), CONNECTION_ID_KEY, input.getConnectionId(), JOB_ID_KEY, input.getJobId()));
    try {
      final long jobId = input.getJobId();
      final int attemptNumber = input.getAttemptNumber();
      ApmTraceUtils.addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, attemptNumber, JOB_ID_KEY, jobId));

      if (input.getStandardSyncOutput() != null) {
        final JobOutput jobOutput = new JobOutput().withSync(input.getStandardSyncOutput());
        jobPersistence.writeOutput(jobId, attemptNumber, jobOutput);
      } else {
        log.warn("The job {} doesn't have any output for the attempt {}", jobId, attemptNumber);
      }
      jobPersistence.succeedAttempt(jobId, attemptNumber);
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.ATTEMPT_SUCCEEDED_BY_RELEASE_STAGE, jobId);
      final Job job = jobPersistence.getJob(jobId);

      jobNotifier.successJob(job);
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.JOB_SUCCEEDED_BY_RELEASE_STAGE, jobId);
      trackCompletion(job, JobStatus.SUCCEEDED);
    } catch (final IOException e) {
      trackCompletionForInternalFailure(input.getJobId(), input.getConnectionId(), input.getAttemptNumber(), JobStatus.SUCCEEDED, e);
      throw new RetryableException(e);
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void jobFailure(final JobFailureInput input) {
    try {
      final long jobId = input.getJobId();
      jobPersistence.failJob(jobId);
      final Job job = jobPersistence.getJob(jobId);

      jobNotifier.failJob(input.getReason(), job);
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.JOB_FAILED_BY_RELEASE_STAGE, jobId);

      final UUID connectionId = UUID.fromString(job.getScope());
      ApmTraceUtils.addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, input.getAttemptNumber(), CONNECTION_ID_KEY, connectionId, JOB_ID_KEY, jobId));
      final JobSyncConfig jobSyncConfig = job.getConfig().getSync();
      final String sourceDockerImage = jobSyncConfig != null ? jobSyncConfig.getSourceDockerImage() : null;
      final String destinationDockerImage = jobSyncConfig != null ? jobSyncConfig.getDestinationDockerImage() : null;
      final SyncJobReportingContext jobContext = new SyncJobReportingContext(jobId, sourceDockerImage, destinationDockerImage);
      job.getLastFailedAttempt().flatMap(Attempt::getFailureSummary)
          .ifPresent(failureSummary -> jobErrorReporter.reportSyncJobFailure(connectionId, failureSummary, jobContext));
      trackCompletion(job, JobStatus.FAILED);
    } catch (final IOException e) {
      trackCompletionForInternalFailure(input.getJobId(), input.getConnectionId(), input.getAttemptNumber(), JobStatus.FAILED, e);
      throw new RetryableException(e);
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void attemptFailureWithAttemptNumber(final AttemptNumberFailureInput input) {
    ApmTraceUtils.addTagsToTrace(
        Map.of(ATTEMPT_NUMBER_KEY, input.getAttemptNumber(), CONNECTION_ID_KEY, input.getConnectionId(), JOB_ID_KEY, input.getJobId()));

    try {
      final int attemptNumber = input.getAttemptNumber();
      final long jobId = input.getJobId();
      final AttemptFailureSummary failureSummary = input.getAttemptFailureSummary();

      ApmTraceUtils.addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, attemptNumber, JOB_ID_KEY, jobId));
      traceFailures(failureSummary);

      jobPersistence.failAttempt(jobId, attemptNumber);
      jobPersistence.writeAttemptFailureSummary(jobId, attemptNumber, failureSummary);

      if (input.getStandardSyncOutput() != null) {
        final JobOutput jobOutput = new JobOutput().withSync(input.getStandardSyncOutput());
        jobPersistence.writeOutput(jobId, attemptNumber, jobOutput);
      }

      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.ATTEMPT_FAILED_BY_RELEASE_STAGE, jobId);
      trackFailures(failureSummary);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void jobCancelledWithAttemptNumber(final JobCancelledInputWithAttemptNumber input) {
    ApmTraceUtils.addTagsToTrace(
        Map.of(ATTEMPT_NUMBER_KEY, input.getAttemptNumber(), CONNECTION_ID_KEY, input.getConnectionId(), JOB_ID_KEY, input.getJobId()));

    try {
      final long jobId = input.getJobId();
      final int attemptNumber = input.getAttemptNumber();
      ApmTraceUtils.addTagsToTrace(Map.of(ATTEMPT_NUMBER_KEY, attemptNumber, JOB_ID_KEY, jobId));
      jobPersistence.failAttempt(jobId, attemptNumber);
      jobPersistence.writeAttemptFailureSummary(jobId, attemptNumber, input.getAttemptFailureSummary());
      jobPersistence.cancelJob(jobId);

      final Job job = jobPersistence.getJob(jobId);
      emitJobIdToReleaseStagesMetric(OssMetricsRegistry.JOB_CANCELLED_BY_RELEASE_STAGE, jobId);
      jobNotifier.failJob("Job was cancelled", job);
      trackCompletion(job, JobStatus.FAILED);
    } catch (final IOException e) {
      trackCompletionForInternalFailure(input.getJobId(), input.getConnectionId(), input.getAttemptNumber(), JobStatus.FAILED, e);
      throw new RetryableException(e);
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void reportJobStart(final ReportJobStartInput input) {
    try {
      ApmTraceUtils.addTagsToTrace(Map.of(JOB_ID_KEY, input.getJobId()));
      final Job job = jobPersistence.getJob(input.getJobId());
      jobTracker.trackSync(job, JobState.STARTED);
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public void ensureCleanJobState(final EnsureCleanJobStateInput input) {
    ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, input.getConnectionId()));
    failNonTerminalJobs(input.getConnectionId());
  }

  @Override
  public boolean isLastJobOrAttemptFailure(final JobCheckFailureInput input) {
    final int limit = 2;
    boolean lastAttemptCheck = false;
    boolean lastJobCheck = false;

    final Set<JobConfig.ConfigType> configTypes = new HashSet<>();
    configTypes.add(SYNC);

    try {
      final List<Job> jobList = jobPersistence.listJobsIncludingId(configTypes, input.getConnectionId().toString(), input.getJobId(), limit);
      final Optional<Job> optionalActiveJob = jobList.stream().filter(job -> job.getId() == input.getJobId()).findFirst();
      if (optionalActiveJob.isPresent()) {
        lastAttemptCheck = checkActiveJobPreviousAttempt(optionalActiveJob.get(), input.getAttemptId());
      }

      final OptionalLong previousJobId = getPreviousJobId(input.getJobId(), jobList.stream().map(Job::getId).toList());
      if (previousJobId.isPresent()) {
        final Optional<Job> optionalPreviousJob = jobList.stream().filter(job -> job.getId() == previousJobId.getAsLong()).findFirst();
        if (optionalPreviousJob.isPresent()) {
          lastJobCheck = optionalPreviousJob.get().getStatus().equals(io.airbyte.persistence.job.models.JobStatus.FAILED);
        }
      }

      return lastJobCheck || lastAttemptCheck;
    } catch (final IOException e) {
      throw new RetryableException(e);
    }
  }

  private OptionalLong getPreviousJobId(final Long activeJobId, final List<Long> jobIdsList) {
    return jobIdsList.stream()
        .filter(jobId -> !Objects.equals(jobId, activeJobId))
        .mapToLong(jobId -> jobId).max();
  }

  private boolean checkActiveJobPreviousAttempt(final Job activeJob, final int attemptId) {
    final int minAttemptSize = 1;
    boolean result = false;

    if (activeJob.getAttempts().size() > minAttemptSize) {
      final Optional<Attempt> optionalAttempt = activeJob.getAttempts().stream()
          .filter(attempt -> attempt.getAttemptNumber() == (attemptId - 1)).findFirst();
      result = optionalAttempt.isPresent() && optionalAttempt.get().getStatus().equals(FAILED);
    }

    return result;
  }

  private void failNonTerminalJobs(final UUID connectionId) {
    try {
      final List<Job> jobs = jobPersistence.listJobsForConnectionWithStatuses(connectionId, Job.REPLICATION_TYPES,
          io.airbyte.persistence.job.models.JobStatus.NON_TERMINAL_STATUSES);
      for (final Job job : jobs) {
        final long jobId = job.getId();

        // fail all non-terminal attempts
        for (final Attempt attempt : job.getAttempts()) {
          if (Attempt.isAttemptInTerminalState(attempt)) {
            continue;
          }

          final int attemptNumber = attempt.getAttemptNumber();
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

  private static final int MAX_ATTEMPTS = 3;
  private static final Map<ReleaseStage, Integer> RELEASE_STAGE_ORDER = Map.of(
      ReleaseStage.custom, 1,
      ReleaseStage.alpha, 2,
      ReleaseStage.beta, 3,
      ReleaseStage.generally_available, 4);
  private static final Comparator<ReleaseStage> RELEASE_STAGE_COMPARATOR = Comparator.comparingInt(RELEASE_STAGE_ORDER::get);

  @VisibleForTesting
  static List<ReleaseStage> orderByReleaseStageAsc(final List<ReleaseStage> releaseStages) {
    // Using collector to get a mutable list
    return releaseStages.stream()
        .filter(stage -> stage != null)
        .sorted(RELEASE_STAGE_COMPARATOR)
        .toList();
  }

  /**
   * Extract the attempt number from an attempt. If the number is anonymous (not 0,1,2,3) for some
   * reason return null. We don't want to accidentally have high cardinality here because of a bug.
   *
   * @param attemptNumber - attemptNumber to parse
   * @return extract attempt number or null
   */
  private static String parseAttemptNumberOrNull(final int attemptNumber) {
    if (attemptNumber > MAX_ATTEMPTS) {
      return null;
    } else {
      return Integer.toString(attemptNumber);
    }
  }

  private void emitAttemptEvent(final OssMetricsRegistry metric, final Job job, final int attemptNumber) throws IOException {
    emitAttemptEvent(metric, job, attemptNumber, Collections.emptyList());
  }

  private void emitAttemptEvent(final OssMetricsRegistry metric,
                                final Job job,
                                final int attemptNumber,
                                final List<MetricAttribute> additionalAttributes)
      throws IOException {
    final List<ReleaseStage> releaseStages = configRepository.getJobIdToReleaseStages(job.getId());
    final var releaseStagesOrdered = orderByReleaseStageAsc(releaseStages);
    final var connectionId = job.getScope() == null ? null : UUID.fromString(job.getScope());
    final var geography = configRepository.getGeographyForConnection(connectionId);

    final List<MetricAttribute> baseMetricAttributes = List.of(
        new MetricAttribute(MetricTags.GEOGRAPHY, geography == null ? null : geography.toString()),
        new MetricAttribute(MetricTags.ATTEMPT_NUMBER, parseAttemptNumberOrNull(attemptNumber)),
        new MetricAttribute(MetricTags.MIN_CONNECTOR_RELEASE_STATE, MetricTags.getReleaseStage(MoreLists.getOrNull(releaseStagesOrdered, 0))),
        new MetricAttribute(MetricTags.MAX_CONNECTOR_RELEASE_STATE, MetricTags.getReleaseStage(MoreLists.getOrNull(releaseStagesOrdered, 1))));

    final MetricAttribute[] allMetricAttributes = MoreLists
        .concat(baseMetricAttributes, additionalAttributes)
        .toArray(new MetricAttribute[baseMetricAttributes.size() + additionalAttributes.size()]);
    MetricClientFactory.getMetricClient().count(metric, 1, allMetricAttributes);
  }

  private void emitAttemptCreatedEvent(final Job job, final int attemptNumber) throws IOException {
    emitAttemptEvent(OssMetricsRegistry.ATTEMPTS_CREATED, job, attemptNumber);
  }

  private void emitAttemptCompletedEvent(final Job job, final Attempt attempt) throws IOException {
    final Optional<String> failureOrigin = attempt.getFailureSummary().flatMap(summary -> summary.getFailures()
        .stream()
        .map(FailureReason::getFailureOrigin)
        .filter(Objects::nonNull)
        .map(FailureOrigin::name)
        .findFirst());

    final Optional<String> failureType = attempt.getFailureSummary().flatMap(summary -> summary.getFailures()
        .stream()
        .map(FailureReason::getFailureType)
        .filter(Objects::nonNull)
        .map(MetricTags::getFailureType)
        .findFirst());

    final List<MetricAttribute> additionalAttributes = List.of(
        new MetricAttribute(MetricTags.ATTEMPT_OUTCOME, attempt.getStatus().toString()),
        new MetricAttribute(MetricTags.FAILURE_ORIGIN, failureOrigin.orElse(null)),
        new MetricAttribute(MetricTags.FAILURE_TYPE, failureType.orElse(null)),
        new MetricAttribute(MetricTags.ATTEMPT_QUEUE, attempt.getProcessingTaskQueue()));

    emitAttemptEvent(OssMetricsRegistry.ATTEMPTS_COMPLETED, job, attempt.getAttemptNumber(), additionalAttributes);
  }

  private void emitJobIdToReleaseStagesMetric(final OssMetricsRegistry metric, final long jobId) throws IOException {
    final var releaseStages = configRepository.getJobIdToReleaseStages(jobId);
    if (releaseStages == null || releaseStages.isEmpty()) {
      return;
    }

    for (final ReleaseStage stage : releaseStages) {
      if (stage != null) {
        MetricClientFactory.getMetricClient().count(metric, 1,
            new MetricAttribute(MetricTags.RELEASE_STAGE, MetricTags.getReleaseStage(stage)));
      }
    }
  }

  private void trackCompletion(final Job job, final io.airbyte.workers.JobStatus status) throws IOException {
    emitAttemptCompletedEventIfAttemptPresent(job);
    jobTracker.trackSync(job, Enums.convertTo(status, JobState.class));
  }

  private void emitAttemptCompletedEventIfAttemptPresent(final Job job) throws IOException {
    if (job == null) {
      return;
    }

    final Optional<Attempt> lastAttempt = job.getLastAttempt();
    if (lastAttempt.isPresent()) {
      emitAttemptCompletedEvent(job, lastAttempt.get());
    }
  }

  private void trackCompletionForInternalFailure(final Long jobId,
                                                 final UUID connectionId,
                                                 final Integer attemptId,
                                                 final io.airbyte.workers.JobStatus status,
                                                 final Exception e) {
    jobTracker.trackSyncForInternalFailure(jobId, connectionId, attemptId, Enums.convertTo(status, JobState.class), e);
  }

  /**
   * Adds the failure origins to the APM trace.
   *
   * @param failureSummary The {@link AttemptFailureSummary} containing the failure reason(s).
   */
  private void traceFailures(final AttemptFailureSummary failureSummary) {
    if (failureSummary != null) {
      if (CollectionUtils.isNotEmpty(failureSummary.getFailures())) {
        ApmTraceUtils.addTagsToTrace(Map.of(
            FAILURE_TYPES_KEY,
            failureSummary.getFailures()
                .stream()
                .map(FailureReason::getFailureType)
                .map(MetricTags::getFailureType)
                .collect(Collectors.joining(",")),
            FAILURE_ORIGINS_KEY,
            failureSummary.getFailures()
                .stream()
                .map(FailureReason::getFailureOrigin)
                .map(FailureOrigin::name)
                .collect(Collectors.joining(","))));
      }
    } else {
      ApmTraceUtils.addTagsToTrace(Map.of(
          FAILURE_TYPES_KEY, MetricTags.getFailureType(null),
          FAILURE_ORIGINS_KEY, FailureOrigin.UNKNOWN.value()));
    }
  }

  /**
   * Records a metric for each failure reason.
   *
   * @param failureSummary The {@link AttemptFailureSummary} containing the failure reason(s).
   */
  private void trackFailures(final AttemptFailureSummary failureSummary) {
    if (failureSummary != null) {
      for (final FailureReason reason : failureSummary.getFailures()) {
        MetricClientFactory.getMetricClient().count(OssMetricsRegistry.ATTEMPT_FAILED_BY_FAILURE_ORIGIN, 1,
            new MetricAttribute(MetricTags.FAILURE_ORIGIN, MetricTags.getFailureOrigin(reason.getFailureOrigin())),
            new MetricAttribute(MetricTags.FAILURE_TYPE, MetricTags.getFailureType(reason.getFailureType())));
      }
    } else {
      MetricClientFactory.getMetricClient().count(OssMetricsRegistry.ATTEMPT_FAILED_BY_FAILURE_ORIGIN, 1,
          new MetricAttribute(MetricTags.FAILURE_ORIGIN, FailureOrigin.UNKNOWN.value()),
          new MetricAttribute(MetricTags.FAILURE_TYPE, MetricTags.getFailureType(null)));
    }
  }

}
