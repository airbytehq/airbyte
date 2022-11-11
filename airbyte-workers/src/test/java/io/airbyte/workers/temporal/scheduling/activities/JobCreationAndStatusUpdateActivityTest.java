/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static io.airbyte.config.JobConfig.ConfigType.SYNC;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;

import io.airbyte.commons.docker.DockerUtils;
import io.airbyte.commons.temporal.exception.RetryableException;
import io.airbyte.commons.version.Version;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.persistence.job.JobCreator;
import io.airbyte.persistence.job.JobNotifier;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.errorreporter.JobErrorReporter;
import io.airbyte.persistence.job.factory.SyncJobFactory;
import io.airbyte.persistence.job.models.Attempt;
import io.airbyte.persistence.job.models.AttemptStatus;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.persistence.job.tracker.JobTracker;
import io.airbyte.persistence.job.tracker.JobTracker.JobState;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.run.TemporalWorkerRunFactory;
import io.airbyte.workers.run.WorkerRun;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptNumberCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.EnsureCleanJobStateInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCancelledInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobSuccessInput;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InOrder;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class JobCreationAndStatusUpdateActivityTest {

  public static final String REASON = "reason";
  @Mock
  private SyncJobFactory mJobFactory;

  @Mock
  private JobPersistence mJobPersistence;

  @Mock
  private TemporalWorkerRunFactory mTemporalWorkerRunFactory;

  @Mock
  private WorkerEnvironment mWorkerEnvironment;

  @Mock
  private LogConfigs mLogConfigs;

  @Mock
  private JobNotifier mJobNotifier;

  @Mock
  private JobTracker mJobtracker;

  @Mock
  private JobErrorReporter mJobErrorReporter;

  @Mock
  private ConfigRepository mConfigRepository;

  @Mock
  private JobCreator mJobCreator;

  @Mock
  private StreamResetPersistence mStreamResetPersistence;

  @InjectMocks
  private JobCreationAndStatusUpdateActivityImpl jobCreationAndStatusUpdateActivity;

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_ID = UUID.randomUUID();
  private static final UUID DESTINATION_DEFINITION_ID = UUID.randomUUID();
  private static final String DOCKER_REPOSITORY = "docker-repo";
  private static final String DOCKER_IMAGE_TAG = "0.0.1";
  private static final String DOCKER_IMAGE_NAME = DockerUtils.getTaggedImageName(DOCKER_REPOSITORY, DOCKER_IMAGE_TAG);
  private static final Version DESTINATION_PROTOCOL_VERSION = new Version("0.4.0");
  private static final long JOB_ID = 123L;
  private static final long PREVIOUS_JOB_ID = 120L;
  private static final int ATTEMPT_ID = 0;
  private static final int ATTEMPT_NUMBER = 1;
  private static final StreamDescriptor STREAM_DESCRIPTOR1 = new StreamDescriptor().withName("stream 1").withNamespace("namespace 1");
  private static final StreamDescriptor STREAM_DESCRIPTOR2 = new StreamDescriptor().withName("stream 2").withNamespace("namespace 2");
  private static final String TEST_EXCEPTION_MESSAGE = "test";

  private static final StandardSyncOutput standardSyncOutput = new StandardSyncOutput()
      .withStandardSyncSummary(
          new StandardSyncSummary()
              .withStatus(ReplicationStatus.COMPLETED))
      .withNormalizationSummary(
          new NormalizationSummary());

  private static final JobOutput jobOutput = new JobOutput().withSync(standardSyncOutput);

  private static final AttemptFailureSummary failureSummary = new AttemptFailureSummary()
      .withFailures(Collections.singletonList(
          new FailureReason()
              .withFailureOrigin(FailureOrigin.SOURCE)));

  @Nested
  class Creation {

    @Test
    @DisplayName("Test job creation")
    void createJob() throws JsonValidationException, ConfigNotFoundException, IOException {
      Mockito.when(mJobFactory.create(CONNECTION_ID))
          .thenReturn(JOB_ID);
      Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID))
          .thenReturn(Mockito.mock(StandardSync.class));

      final JobCreationOutput output = jobCreationAndStatusUpdateActivity.createNewJob(new JobCreationInput(CONNECTION_ID));

      Assertions.assertThat(output.getJobId()).isEqualTo(JOB_ID);
    }

    @Test
    @DisplayName("Test reset job creation")
    void createResetJob() throws JsonValidationException, ConfigNotFoundException, IOException {
      final StandardSync standardSync = new StandardSync().withDestinationId(DESTINATION_ID);
      Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID)).thenReturn(standardSync);
      final DestinationConnection destination = new DestinationConnection().withDestinationDefinitionId(DESTINATION_DEFINITION_ID);
      Mockito.when(mConfigRepository.getDestinationConnection(DESTINATION_ID)).thenReturn(destination);
      final StandardDestinationDefinition destinationDefinition = new StandardDestinationDefinition()
          .withDockerRepository(DOCKER_REPOSITORY)
          .withDockerImageTag(DOCKER_IMAGE_TAG)
          .withProtocolVersion(DESTINATION_PROTOCOL_VERSION.serialize());
      Mockito.when(mConfigRepository.getStandardDestinationDefinition(DESTINATION_DEFINITION_ID)).thenReturn(destinationDefinition);
      final List<StreamDescriptor> streamsToReset = List.of(STREAM_DESCRIPTOR1, STREAM_DESCRIPTOR2);
      Mockito.when(mStreamResetPersistence.getStreamResets(CONNECTION_ID)).thenReturn(streamsToReset);

      Mockito
          .when(mJobCreator.createResetConnectionJob(destination, standardSync, DOCKER_IMAGE_NAME, DESTINATION_PROTOCOL_VERSION, List.of(),
              streamsToReset))
          .thenReturn(Optional.of(JOB_ID));

      final JobCreationOutput output = jobCreationAndStatusUpdateActivity.createNewJob(new JobCreationInput(CONNECTION_ID));

      Assertions.assertThat(output.getJobId()).isEqualTo(JOB_ID);
    }

    @Test
    @DisplayName("Test attempt creation")
    void createAttempt() throws IOException {
      final Job mJob = Mockito.mock(Job.class);

      Mockito.when(mJobPersistence.getJob(JOB_ID))
          .thenReturn(mJob);

      final WorkerRun mWorkerRun = Mockito.mock(WorkerRun.class);

      Mockito.when(mTemporalWorkerRunFactory.create(mJob))
          .thenReturn(mWorkerRun);

      final Path mPath = Mockito.mock(Path.class);
      final Path path = Path.of("test");
      Mockito.when(mPath.resolve(Mockito.anyString()))
          .thenReturn(path);
      Mockito.when(mWorkerRun.getJobRoot())
          .thenReturn(mPath);

      Mockito.when(mJobPersistence.createAttempt(JOB_ID, path))
          .thenReturn(ATTEMPT_ID);

      final LogClientSingleton mLogClientSingleton = Mockito.mock(LogClientSingleton.class);
      try (final MockedStatic<LogClientSingleton> utilities = Mockito.mockStatic(LogClientSingleton.class)) {
        utilities.when(() -> LogClientSingleton.getInstance())
            .thenReturn(mLogClientSingleton);

        final AttemptCreationOutput output = jobCreationAndStatusUpdateActivity.createNewAttempt(new AttemptCreationInput(
            JOB_ID));

        verify(mLogClientSingleton).setJobMdc(mWorkerEnvironment, mLogConfigs, mPath);
        Assertions.assertThat(output.getAttemptId()).isEqualTo(ATTEMPT_ID);
      }
    }

    @Test
    void isLastJobOrAttemptFailureTrueTest() throws Exception {
      final int activeAttemptNumber = 0;
      final Attempt activeAttempt = new Attempt(activeAttemptNumber, 1, Path.of(""), null, AttemptStatus.RUNNING, null, 4L, 5L, null);

      final Job previousJob = new Job(PREVIOUS_JOB_ID, ConfigType.SYNC, CONNECTION_ID.toString(),
          new JobConfig(), List.of(), JobStatus.SUCCEEDED, 4L, 4L, 5L);
      final Job activeJob = new Job(JOB_ID, ConfigType.SYNC, CONNECTION_ID.toString(), new JobConfig(), List.of(activeAttempt),
          JobStatus.RUNNING, 2L, 2L, 3L);

      final Set<ConfigType> configTypes = new HashSet<>();
      configTypes.add(SYNC);

      Mockito.when(mJobPersistence.listJobsIncludingId(configTypes, CONNECTION_ID.toString(), JOB_ID, 2))
          .thenReturn(List.of(activeJob, previousJob));
      final boolean result = jobCreationAndStatusUpdateActivity
          .isLastJobOrAttemptFailure(new JobCreationAndStatusUpdateActivity.JobCheckFailureInput(JOB_ID, 0, CONNECTION_ID));
      Assertions.assertThat(result).isEqualTo(false);
    }

    @Test
    void isLastJobOrAttemptFailureFalseTest() throws Exception {
      final int activeAttemptNumber = 0;
      final Attempt activeAttempt = new Attempt(activeAttemptNumber, 1, Path.of(""), null, AttemptStatus.RUNNING, null, 4L, 5L, null);

      final Job previousJob = new Job(PREVIOUS_JOB_ID, ConfigType.SYNC, CONNECTION_ID.toString(),
          new JobConfig(), List.of(), JobStatus.FAILED, 4L, 4L, 5L);
      final Job activeJob = new Job(JOB_ID, ConfigType.SYNC, CONNECTION_ID.toString(), new JobConfig(), List.of(activeAttempt),
          JobStatus.RUNNING, 2L, 2L, 3L);

      final Set<ConfigType> configTypes = new HashSet<>();
      configTypes.add(SYNC);

      Mockito.when(mJobPersistence.listJobsIncludingId(configTypes, CONNECTION_ID.toString(), JOB_ID, 2))
          .thenReturn(List.of(activeJob, previousJob));
      final boolean result = jobCreationAndStatusUpdateActivity
          .isLastJobOrAttemptFailure(new JobCreationAndStatusUpdateActivity.JobCheckFailureInput(JOB_ID, 0, CONNECTION_ID));
      Assertions.assertThat(result).isEqualTo(true);
    }

    @Test
    void isLastJobOrAttemptFailurePreviousAttemptFailureTest() throws Exception {
      final Attempt previousAttempt = new Attempt(0, 1, Path.of(""), null, AttemptStatus.FAILED, null, 2L, 3L, 3L);
      final int activeAttemptNumber = 1;
      final Attempt activeAttempt = new Attempt(activeAttemptNumber, 1, Path.of(""), null, AttemptStatus.RUNNING, null, 4L, 5L, null);

      final Job previousJob = new Job(PREVIOUS_JOB_ID, ConfigType.SYNC, CONNECTION_ID.toString(), new JobConfig(), List.of(),
          JobStatus.SUCCEEDED, 4L, 4L, 5L);
      final Job activeJob = new Job(JOB_ID, ConfigType.SYNC, CONNECTION_ID.toString(), new JobConfig(), List.of(activeAttempt, previousAttempt),
          JobStatus.RUNNING, 2L, 2L, 3L);

      final Set<ConfigType> configTypes = new HashSet<>();
      configTypes.add(SYNC);

      Mockito.when(mJobPersistence.listJobsIncludingId(configTypes, CONNECTION_ID.toString(), JOB_ID, 2))
          .thenReturn(List.of(activeJob, previousJob));
      final boolean result = jobCreationAndStatusUpdateActivity
          .isLastJobOrAttemptFailure(new JobCreationAndStatusUpdateActivity.JobCheckFailureInput(JOB_ID, 1, CONNECTION_ID));
      Assertions.assertThat(result).isEqualTo(true);
    }

    @Test
    @DisplayName("Test exception errors are properly wrapped")
    void createAttemptThrowException() throws IOException {
      Mockito.when(mJobPersistence.getJob(JOB_ID))
          .thenThrow(new IOException());

      Assertions.assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.createNewAttempt(new AttemptCreationInput(
          JOB_ID)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

    @Test
    @DisplayName("Test attempt creation")
    void createAttemptNumber() throws IOException {
      final Job mJob = Mockito.mock(Job.class);

      Mockito.when(mJobPersistence.getJob(JOB_ID))
          .thenReturn(mJob);

      final WorkerRun mWorkerRun = Mockito.mock(WorkerRun.class);

      Mockito.when(mTemporalWorkerRunFactory.create(mJob))
          .thenReturn(mWorkerRun);

      final Path mPath = Mockito.mock(Path.class);
      final Path path = Path.of("test");
      Mockito.when(mPath.resolve(Mockito.anyString()))
          .thenReturn(path);
      Mockito.when(mWorkerRun.getJobRoot())
          .thenReturn(mPath);

      Mockito.when(mJobPersistence.createAttempt(JOB_ID, path))
          .thenReturn(ATTEMPT_NUMBER);

      final LogClientSingleton mLogClientSingleton = Mockito.mock(LogClientSingleton.class);
      try (final MockedStatic<LogClientSingleton> utilities = Mockito.mockStatic(LogClientSingleton.class)) {
        utilities.when(() -> LogClientSingleton.getInstance())
            .thenReturn(mLogClientSingleton);

        final AttemptNumberCreationOutput output = jobCreationAndStatusUpdateActivity.createNewAttemptNumber(new AttemptCreationInput(
            JOB_ID));

        verify(mLogClientSingleton).setJobMdc(mWorkerEnvironment, mLogConfigs, mPath);
        Assertions.assertThat(output.getAttemptNumber()).isEqualTo(ATTEMPT_NUMBER);
      }
    }

    @Test
    @DisplayName("Test exception errors are properly wrapped")
    void createAttemptNumberThrowException() throws IOException {
      Mockito.when(mJobPersistence.getJob(JOB_ID))
          .thenThrow(new IOException());

      Assertions.assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.createNewAttemptNumber(new AttemptCreationInput(
          JOB_ID)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

  }

  @Nested
  class Update {

    @Test
    void setJobSuccess() throws IOException {
      jobCreationAndStatusUpdateActivity.jobSuccess(new JobSuccessInput(JOB_ID, ATTEMPT_ID, CONNECTION_ID, standardSyncOutput));

      verify(mJobPersistence).writeOutput(JOB_ID, ATTEMPT_ID, jobOutput);
      verify(mJobPersistence).succeedAttempt(JOB_ID, ATTEMPT_ID);
      verify(mJobNotifier).successJob(Mockito.any());
      verify(mJobtracker).trackSync(Mockito.any(), eq(JobState.SUCCEEDED));
    }

    @Test
    void setJobSuccessWrapException() throws IOException {
      final IOException exception = new IOException(TEST_EXCEPTION_MESSAGE);
      Mockito.doThrow(exception)
          .when(mJobPersistence).succeedAttempt(JOB_ID, ATTEMPT_ID);

      Assertions.assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.jobSuccess(new JobSuccessInput(JOB_ID, ATTEMPT_ID, CONNECTION_ID, null)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);

      verify(mJobtracker, times(1)).trackSyncForInternalFailure(JOB_ID, CONNECTION_ID, ATTEMPT_ID, JobState.SUCCEEDED, exception);
    }

    @Test
    void setJobFailure() throws IOException {
      final Attempt mAttempt = Mockito.mock(Attempt.class);
      Mockito.when(mAttempt.getFailureSummary()).thenReturn(Optional.of(failureSummary));

      final JobSyncConfig mJobSyncConfig = Mockito.mock(JobSyncConfig.class);
      Mockito.when(mJobSyncConfig.getSourceDockerImage()).thenReturn(DOCKER_IMAGE_NAME);
      Mockito.when(mJobSyncConfig.getDestinationDockerImage()).thenReturn(DOCKER_IMAGE_NAME);

      final JobConfig mJobConfig = Mockito.mock(JobConfig.class);
      Mockito.when(mJobConfig.getSync()).thenReturn(mJobSyncConfig);

      final Job mJob = Mockito.mock(Job.class);
      Mockito.when(mJob.getScope()).thenReturn(CONNECTION_ID.toString());
      Mockito.when(mJob.getConfig()).thenReturn(mJobConfig);
      Mockito.when(mJob.getLastFailedAttempt()).thenReturn(Optional.of(mAttempt));

      Mockito.when(mJobPersistence.getJob(JOB_ID))
          .thenReturn(mJob);

      jobCreationAndStatusUpdateActivity.jobFailure(new JobFailureInput(JOB_ID, 1, CONNECTION_ID, REASON));

      verify(mJobPersistence).failJob(JOB_ID);
      verify(mJobNotifier).failJob(eq(REASON), Mockito.any());
      verify(mJobErrorReporter).reportSyncJobFailure(eq(CONNECTION_ID), eq(failureSummary), Mockito.any());
    }

    @Test
    void setJobFailureWrapException() throws IOException {
      final Exception exception = new IOException(TEST_EXCEPTION_MESSAGE);
      Mockito.doThrow(exception)
          .when(mJobPersistence).failJob(JOB_ID);

      Assertions
          .assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.jobFailure(new JobFailureInput(JOB_ID, ATTEMPT_NUMBER, CONNECTION_ID, "")))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);

      verify(mJobtracker, times(1)).trackSyncForInternalFailure(JOB_ID, CONNECTION_ID, ATTEMPT_NUMBER, JobState.FAILED, exception);
    }

    @Test
    void setJobFailureWithNullJobSyncConfig() throws IOException {
      final Attempt mAttempt = Mockito.mock(Attempt.class);
      Mockito.when(mAttempt.getFailureSummary()).thenReturn(Optional.of(failureSummary));

      final JobConfig mJobConfig = Mockito.mock(JobConfig.class);
      Mockito.when(mJobConfig.getSync()).thenReturn(null);

      final Job mJob = Mockito.mock(Job.class);
      Mockito.when(mJob.getScope()).thenReturn(CONNECTION_ID.toString());
      Mockito.when(mJob.getConfig()).thenReturn(mJobConfig);
      Mockito.when(mJob.getLastFailedAttempt()).thenReturn(Optional.of(mAttempt));

      Mockito.when(mJobPersistence.getJob(JOB_ID))
          .thenReturn(mJob);

      jobCreationAndStatusUpdateActivity.jobFailure(new JobFailureInput(JOB_ID, 1, CONNECTION_ID, REASON));

      verify(mJobPersistence).failJob(JOB_ID);
      verify(mJobNotifier).failJob(eq(REASON), Mockito.any());
      verify(mJobErrorReporter).reportSyncJobFailure(eq(CONNECTION_ID), eq(failureSummary), Mockito.any());
    }

    @Test
    void setAttemptFailure() throws IOException {
      jobCreationAndStatusUpdateActivity
          .attemptFailure(new AttemptFailureInput(JOB_ID, ATTEMPT_ID, CONNECTION_ID, standardSyncOutput, failureSummary));

      verify(mJobPersistence).failAttempt(JOB_ID, ATTEMPT_ID);
      verify(mJobPersistence).writeOutput(JOB_ID, ATTEMPT_ID, jobOutput);
      verify(mJobPersistence).writeAttemptFailureSummary(JOB_ID, ATTEMPT_ID, failureSummary);
    }

    @Test
    void setAttemptFailureWrapException() throws IOException {
      final Exception exception = new IOException(TEST_EXCEPTION_MESSAGE);
      Mockito.doThrow(exception)
          .when(mJobPersistence).failAttempt(JOB_ID, ATTEMPT_ID);

      Assertions
          .assertThatThrownBy(
              () -> jobCreationAndStatusUpdateActivity
                  .attemptFailure(new AttemptFailureInput(JOB_ID, ATTEMPT_ID, CONNECTION_ID, null, failureSummary)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

    @Test
    void setJobCancelled() throws IOException {
      jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(JOB_ID, ATTEMPT_ID, CONNECTION_ID, failureSummary));

      // attempt must be failed before job is cancelled, or else job state machine is not respected
      final InOrder orderVerifier = Mockito.inOrder(mJobPersistence);
      orderVerifier.verify(mJobPersistence).failAttempt(JOB_ID, ATTEMPT_ID);
      orderVerifier.verify(mJobPersistence).writeAttemptFailureSummary(JOB_ID, ATTEMPT_ID, failureSummary);
      orderVerifier.verify(mJobPersistence).cancelJob(JOB_ID);
    }

    @Test
    void setJobCancelledWrapException() throws IOException {
      final Exception exception = new IOException();
      Mockito.doThrow(exception)
          .when(mJobPersistence).cancelJob(JOB_ID);

      Assertions
          .assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(JOB_ID, ATTEMPT_ID, CONNECTION_ID, null)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);

      verify(mJobtracker, times(1)).trackSyncForInternalFailure(JOB_ID, CONNECTION_ID, ATTEMPT_ID, JobState.FAILED, exception);
    }

    @Test
    void ensureCleanJobState() throws IOException {
      final Attempt failedAttempt = new Attempt(0, 1, Path.of(""), null, AttemptStatus.FAILED, null, 2L, 3L, 3L);
      final int runningAttemptNumber = 1;
      final Attempt runningAttempt = new Attempt(runningAttemptNumber, 1, Path.of(""), null, AttemptStatus.RUNNING, null, 4L, 5L, null);
      final Job runningJob = new Job(1, ConfigType.SYNC, CONNECTION_ID.toString(), new JobConfig(), List.of(failedAttempt, runningAttempt),
          JobStatus.RUNNING, 2L, 2L, 3L);

      final Job pendingJob = new Job(2, ConfigType.SYNC, CONNECTION_ID.toString(), new JobConfig(), List.of(), JobStatus.PENDING, 4L, 4L, 5L);

      Mockito.when(mJobPersistence.listJobsForConnectionWithStatuses(CONNECTION_ID, Job.REPLICATION_TYPES, JobStatus.NON_TERMINAL_STATUSES))
          .thenReturn(List.of(runningJob, pendingJob));
      Mockito.when(mJobPersistence.getJob(runningJob.getId())).thenReturn(runningJob);
      Mockito.when(mJobPersistence.getJob(pendingJob.getId())).thenReturn(pendingJob);

      jobCreationAndStatusUpdateActivity.ensureCleanJobState(new EnsureCleanJobStateInput(CONNECTION_ID));

      verify(mJobPersistence).failJob(runningJob.getId());
      verify(mJobPersistence).failJob(pendingJob.getId());
      verify(mJobPersistence).failAttempt(runningJob.getId(), runningAttemptNumber);
      verify(mJobPersistence).writeAttemptFailureSummary(eq(runningJob.getId()), eq(runningAttemptNumber), any());
      verify(mJobPersistence).getJob(runningJob.getId());
      verify(mJobPersistence).getJob(pendingJob.getId());
      verify(mJobNotifier).failJob(any(), eq(runningJob));
      verify(mJobNotifier).failJob(any(), eq(pendingJob));
      verify(mJobtracker).trackSync(runningJob, JobState.FAILED);
      verify(mJobtracker).trackSync(pendingJob, JobState.FAILED);
      Mockito.verifyNoMoreInteractions(mJobPersistence, mJobNotifier, mJobtracker);
    }

  }

}
