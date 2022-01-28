/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardSyncSummary.ReplicationStatus;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.temporal.exception.RetryableException;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.AttemptFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCancelledInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobCreationOutput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobFailureInput;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivity.JobSuccessInput;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import io.airbyte.workers.worker_run.WorkerRun;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Collections;
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

  @InjectMocks
  private JobCreationAndStatusUpdateActivityImpl jobCreationAndStatusUpdateActivity;

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final long JOB_ID = 123L;
  private static final int ATTEMPT_ID = 0;
  private static final StandardSyncOutput standardSyncOutput = new StandardSyncOutput()
      .withStandardSyncSummary(
          new StandardSyncSummary()
              .withStatus(ReplicationStatus.COMPLETED));

  private static final JobOutput jobOutput = new JobOutput().withSync(standardSyncOutput);

  private static final AttemptFailureSummary failureSummary = new AttemptFailureSummary()
      .withFailures(Collections.singletonList(
          new FailureReason()
              .withFailureOrigin(FailureOrigin.SOURCE)));

  @Nested
  class Creation {

    @Test
    @DisplayName("Test job creation")
    public void createJob() {
      Mockito.when(mJobFactory.create(CONNECTION_ID))
          .thenReturn(JOB_ID);

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

  }

  @Nested
  class Update {

    @Test
    public void setJobSuccess() throws IOException {
      jobCreationAndStatusUpdateActivity.jobSuccess(new JobSuccessInput(JOB_ID, ATTEMPT_ID, standardSyncOutput));

      Mockito.verify(mJobPersistence).writeOutput(JOB_ID, ATTEMPT_ID, jobOutput);
      Mockito.verify(mJobPersistence).succeedAttempt(JOB_ID, ATTEMPT_ID);
      Mockito.verify(mJobNotifier).successJob(Mockito.any());
      Mockito.verify(mJobtracker).trackSync(Mockito.any(), Mockito.eq(JobState.SUCCEEDED));
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
      Mockito.verify(mJobNotifier).failJob(Mockito.eq("reason"), Mockito.any());
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
    public void setJobCancelledWithNoFailures() throws IOException {
      jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(JOB_ID, ATTEMPT_ID, null));

      Mockito.verify(mJobPersistence).cancelJob(JOB_ID);
      Mockito.verify(mJobPersistence, Mockito.never()).writeAttemptFailureSummary(Mockito.anyLong(), Mockito.anyInt(), Mockito.any());
    }

    @Test
    public void setJobCancelledWithFailures() throws IOException {
      jobCreationAndStatusUpdateActivity.jobCancelled(new JobCancelledInput(JOB_ID, ATTEMPT_ID, failureSummary));

      Mockito.verify(mJobPersistence).cancelJob(JOB_ID);
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

  }

}
