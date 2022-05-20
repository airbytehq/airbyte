/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.AttemptStatus;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.run.TemporalWorkerRunFactory;
import io.airbyte.workers.run.WorkerRun;
import io.airbyte.workers.temporal.exception.RetryableException;
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
import java.util.List;
import java.util.UUID;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class JobCreationAndStatusUpdateActivityTest {

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
  private ConfigRepository mConfigRepository;

  @InjectMocks
  private JobCreationAndStatusUpdateActivityImpl jobCreationAndStatusUpdateActivity;

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final long JOB_ID = 123L;
  private static final int ATTEMPT_ID = 0;
  private static final int ATTEMPT_NUMBER = 1;
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
    public void createJob() throws JsonValidationException, ConfigNotFoundException, IOException {
      Mockito.when(mJobFactory.create(CONNECTION_ID))
          .thenReturn(JOB_ID);
      Mockito.when(mConfigRepository.getStandardSync(CONNECTION_ID))
          .thenReturn(Mockito.mock(StandardSync.class));

      final JobCreationOutput output = jobCreationAndStatusUpdateActivity.createNewJob(new JobCreationInput(CONNECTION_ID, false));

      Assertions.assertThat(output.getJobId()).isEqualTo(JOB_ID);
    }

    @Test
    @DisplayName("Test attempt creation")
    public void createAttempt() throws IOException {
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

        Mockito.verify(mLogClientSingleton).setJobMdc(mWorkerEnvironment, mLogConfigs, mPath);
        Assertions.assertThat(output.getAttemptId()).isEqualTo(ATTEMPT_ID);
      }
    }

    @Test
    @DisplayName("Test exception errors are properly wrapped")
    public void createAttemptThrowException() throws IOException {
      Mockito.when(mJobPersistence.getJob(JOB_ID))
          .thenThrow(new IOException());

      Assertions.assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.createNewAttempt(new AttemptCreationInput(
          JOB_ID)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

    @Test
    @DisplayName("Test attempt creation")
    public void createAttemptNumber() throws IOException {
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

        Mockito.verify(mLogClientSingleton).setJobMdc(mWorkerEnvironment, mLogConfigs, mPath);
        Assertions.assertThat(output.getAttemptNumber()).isEqualTo(ATTEMPT_NUMBER);
      }
    }

    @Test
    @DisplayName("Test exception errors are properly wrapped")
    public void createAttemptNumberThrowException() throws IOException {
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
    public void setJobSuccess() throws IOException {
      jobCreationAndStatusUpdateActivity.jobSuccess(new JobSuccessInput(JOB_ID, ATTEMPT_ID, standardSyncOutput));

      Mockito.verify(mJobPersistence).writeOutput(JOB_ID, ATTEMPT_ID, jobOutput);
      Mockito.verify(mJobPersistence).succeedAttempt(JOB_ID, ATTEMPT_ID);
      Mockito.verify(mJobNotifier).successJob(Mockito.any());
      Mockito.verify(mJobtracker).trackSync(Mockito.any(), eq(JobState.SUCCEEDED));
    }

    @Test
    public void setJobSuccessWrapException() throws IOException {
      Mockito.doThrow(new IOException())
          .when(mJobPersistence).succeedAttempt(JOB_ID, ATTEMPT_ID);

      Assertions.assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.jobSuccess(new JobSuccessInput(JOB_ID, ATTEMPT_ID, null)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

    @Test
    public void setJobFailure() throws IOException {
      jobCreationAndStatusUpdateActivity.jobFailure(new JobFailureInput(JOB_ID, "reason"));

      Mockito.verify(mJobPersistence).failJob(JOB_ID);
      Mockito.verify(mJobNotifier).failJob(eq("reason"), Mockito.any());
    }

    @Test
    public void setJobFailureWrapException() throws IOException {
      Mockito.doThrow(new IOException())
          .when(mJobPersistence).failJob(JOB_ID);

      Assertions.assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.jobFailure(new JobFailureInput(JOB_ID, "")))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

    @Test
    public void setAttemptFailure() throws IOException {
      jobCreationAndStatusUpdateActivity.attemptFailure(new AttemptFailureInput(JOB_ID, ATTEMPT_ID, standardSyncOutput, failureSummary));

      Mockito.verify(mJobPersistence).failAttempt(JOB_ID, ATTEMPT_ID);
      Mockito.verify(mJobPersistence).writeOutput(JOB_ID, ATTEMPT_ID, jobOutput);
      Mockito.verify(mJobPersistence).writeAttemptFailureSummary(JOB_ID, ATTEMPT_ID, failureSummary);
    }

    @Test
    public void setAttemptFailureWrapException() throws IOException {
      Mockito.doThrow(new IOException())
          .when(mJobPersistence).failAttempt(JOB_ID, ATTEMPT_ID);

      Assertions
          .assertThatThrownBy(
              () -> jobCreationAndStatusUpdateActivity.attemptFailure(new AttemptFailureInput(JOB_ID, ATTEMPT_ID, null, failureSummary)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

    @Test
    public void setJobCancelled() throws IOException {
      jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(JOB_ID, ATTEMPT_ID, failureSummary));

      Mockito.verify(mJobPersistence).cancelJob(JOB_ID);
      Mockito.verify(mJobPersistence).failAttempt(JOB_ID, ATTEMPT_ID);
      Mockito.verify(mJobPersistence).writeAttemptFailureSummary(JOB_ID, ATTEMPT_ID, failureSummary);
    }

    @Test
    public void setJobCancelledWrapException() throws IOException {
      Mockito.doThrow(new IOException())
          .when(mJobPersistence).cancelJob(JOB_ID);

      Assertions.assertThatThrownBy(() -> jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(JOB_ID, ATTEMPT_ID, null)))
          .isInstanceOf(RetryableException.class)
          .hasCauseInstanceOf(IOException.class);
    }

    @Test
    public void ensureCleanJobState() throws IOException {
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

      Mockito.verify(mJobPersistence).failJob(runningJob.getId());
      Mockito.verify(mJobPersistence).failJob(pendingJob.getId());
      Mockito.verify(mJobPersistence).failAttempt(runningJob.getId(), runningAttemptNumber);
      Mockito.verify(mJobPersistence).writeAttemptFailureSummary(eq(runningJob.getId()), eq(runningAttemptNumber), any());
      Mockito.verify(mJobPersistence).getJob(runningJob.getId());
      Mockito.verify(mJobPersistence).getJob(pendingJob.getId());
      Mockito.verify(mJobNotifier).failJob(any(), eq(runningJob));
      Mockito.verify(mJobNotifier).failJob(any(), eq(pendingJob));
      Mockito.verify(mJobtracker).trackSync(runningJob, JobState.FAILED);
      Mockito.verify(mJobtracker).trackSync(pendingJob, JobState.FAILED);
      Mockito.verifyNoMoreInteractions(mJobPersistence, mJobNotifier, mJobtracker);
    }

  }

}
