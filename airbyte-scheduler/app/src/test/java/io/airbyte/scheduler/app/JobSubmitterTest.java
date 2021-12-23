/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.RETURNS_DEEP_STUBS;
import static org.mockito.Mockito.atLeast;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doReturn;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.inOrder;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.util.concurrent.MoreExecutors;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.workers.JobStatus;
import io.airbyte.workers.OutputAndStatus;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import io.airbyte.workers.worker_run.WorkerRun;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicReference;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;
import org.mockito.Mockito;
import org.slf4j.MDC;

public class JobSubmitterTest {

  private static final OutputAndStatus<JobOutput> SUCCESS_OUTPUT = new OutputAndStatus<>(JobStatus.SUCCEEDED, new JobOutput());
  private static final OutputAndStatus<JobOutput> FAILED_OUTPUT = new OutputAndStatus<>(JobStatus.FAILED);
  private static final long JOB_ID = 1L;
  private static final int ATTEMPT_NUMBER = 12;

  private JobPersistence persistence;
  private TemporalWorkerRunFactory workerRunFactory;
  private WorkerRun workerRun;
  private Job job;
  private Path logPath;

  private JobSubmitter jobSubmitter;
  private JobTracker jobTracker;
  private JobNotifier jobNotifier;
  private ConfigRepository configRepository;

  @BeforeEach
  public void setup() throws IOException {
    job = mock(Job.class, RETURNS_DEEP_STUBS);
    jobTracker = mock(JobTracker.class);
    when(job.getId()).thenReturn(JOB_ID);
    when(job.getAttempts().size()).thenReturn(ATTEMPT_NUMBER);

    workerRun = mock(WorkerRun.class);
    final Path jobRoot = Files.createTempDirectory("test");
    final Path logPath = jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    when(workerRun.getJobRoot()).thenReturn(jobRoot);
    workerRunFactory = mock(TemporalWorkerRunFactory.class);
    when(workerRunFactory.create(job)).thenReturn(workerRun);

    persistence = mock(JobPersistence.class);
    this.logPath = jobRoot.resolve(LogClientSingleton.LOG_FILENAME);
    when(persistence.getNextJob()).thenReturn(Optional.of(job));
    when(persistence.createAttempt(JOB_ID, logPath)).thenReturn(ATTEMPT_NUMBER);
    jobNotifier = mock(JobNotifier.class);

    configRepository = mock(ConfigRepository.class);

    jobSubmitter = spy(new JobSubmitter(
        MoreExecutors.newDirectExecutorService(),
        persistence,
        workerRunFactory,
        jobTracker,
        jobNotifier,
        WorkerEnvironment.DOCKER,
        LogConfigs.EMPTY,
        configRepository));
  }

  @Test
  public void testRun() {
    doNothing().when(jobSubmitter).submitJob(any());

    jobSubmitter.run();

    verify(jobTracker).trackSync(job, JobState.STARTED);
    verify(jobSubmitter).submitJob(job);
  }

  @Test
  public void testPersistenceNoJob() throws Exception {
    doReturn(Optional.empty()).when(persistence).getNextJob();

    jobSubmitter.run();

    verifyNoInteractions(workerRunFactory);
    verify(jobTracker, never()).trackSync(any(), any());
  }

  @Test
  public void testSuccess() throws Exception {
    doReturn(SUCCESS_OUTPUT).when(workerRun).call();

    final StandardWorkspace completedSyncWorkspace = new StandardWorkspace()
        .withFirstCompletedSync(true);
    final StandardWorkspace nonCompletedSyncWorkspace = new StandardWorkspace()
        .withFirstCompletedSync(false);

    when(configRepository.listStandardWorkspaces(false))
        .thenReturn(Lists.newArrayList(completedSyncWorkspace, nonCompletedSyncWorkspace));

    jobSubmitter.submitJob(job);

    final InOrder inOrder = inOrder(persistence, jobSubmitter);
    inOrder.verify(persistence).createAttempt(JOB_ID, logPath);
    inOrder.verify(persistence).writeOutput(JOB_ID, ATTEMPT_NUMBER, new JobOutput());
    inOrder.verify(persistence).succeedAttempt(JOB_ID, ATTEMPT_NUMBER);
    verify(jobTracker).trackSync(job, JobState.SUCCEEDED);
    inOrder.verifyNoMoreInteractions();
  }

  @Test
  public void testSuccessCompleteWorkspace() throws Exception {
    doReturn(SUCCESS_OUTPUT).when(workerRun).call();

    final StandardWorkspace completedSyncWorkspace = new StandardWorkspace()
        .withFirstCompletedSync(true);
    final StandardWorkspace nonCompletedSyncWorkspace = new StandardWorkspace()
        .withFirstCompletedSync(false);

    when(configRepository.getStandardWorkspaceFromConnection(any(UUID.class), eq(false)))
        .thenReturn(nonCompletedSyncWorkspace);

    when(job.getScope())
        .thenReturn(UUID.randomUUID().toString());
    when(job.getConfigType())
        .thenReturn(ConfigType.SYNC);

    jobSubmitter.submitJob(job);

    verify(configRepository).writeStandardWorkspace(nonCompletedSyncWorkspace);
  }

  @Test
  public void testFailure() throws Exception {
    doReturn(FAILED_OUTPUT).when(workerRun).call();

    jobSubmitter.run();

    final InOrder inOrder = inOrder(persistence, jobSubmitter);
    inOrder.verify(persistence).createAttempt(JOB_ID, logPath);
    inOrder.verify(persistence).failAttempt(JOB_ID, ATTEMPT_NUMBER);
    verify(jobTracker).trackSync(job, JobState.FAILED);
    inOrder.verifyNoMoreInteractions();
    verifyNoInteractions(configRepository);
  }

  @Test
  public void testException() throws Exception {
    doThrow(new RuntimeException()).when(workerRun).call();

    jobSubmitter.run();

    final InOrder inOrder = inOrder(persistence, jobTracker);
    inOrder.verify(persistence).createAttempt(JOB_ID, logPath);
    inOrder.verify(persistence).failAttempt(JOB_ID, ATTEMPT_NUMBER);
    inOrder.verify(jobTracker).trackSync(job, JobState.FAILED);
    inOrder.verifyNoMoreInteractions();
    verifyNoInteractions(configRepository);
  }

  @Test
  public void testPersistenceExceptionMismatchAttemptId() throws Exception {
    when(persistence.createAttempt(JOB_ID, logPath)).thenReturn(ATTEMPT_NUMBER + 1);

    jobSubmitter.run();

    final InOrder inOrder = inOrder(persistence, jobTracker);
    inOrder.verify(persistence).createAttempt(JOB_ID, logPath);
    inOrder.verify(persistence).failAttempt(JOB_ID, ATTEMPT_NUMBER);
    inOrder.verify(jobTracker).trackSync(job, JobState.FAILED);
    inOrder.verifyNoMoreInteractions();
  }

  @Test
  public void testPersistenceExceptionStart() throws Exception {
    doThrow(new RuntimeException()).when(persistence).createAttempt(anyLong(), any());

    jobSubmitter.run();

    final InOrder inOrder = inOrder(persistence, jobTracker);
    inOrder.verify(persistence).createAttempt(JOB_ID, logPath);
    inOrder.verify(persistence).failAttempt(JOB_ID, ATTEMPT_NUMBER);
    inOrder.verify(jobTracker).trackSync(job, JobState.FAILED);
    inOrder.verifyNoMoreInteractions();
  }

  @Test
  public void testPersistenceExceptionOutput() throws Exception {
    doReturn(SUCCESS_OUTPUT).when(workerRun).call();
    doThrow(new RuntimeException()).when(persistence).writeOutput(anyLong(), anyInt(), any());

    jobSubmitter.run();

    final InOrder inOrder = inOrder(persistence, jobTracker);
    inOrder.verify(persistence).createAttempt(JOB_ID, logPath);
    inOrder.verify(persistence).failAttempt(JOB_ID, ATTEMPT_NUMBER);
    inOrder.verify(jobTracker).trackSync(job, JobState.FAILED);
    inOrder.verifyNoMoreInteractions();
  }

  @Test
  void testMDC() throws Exception {
    final AtomicReference<Map<String, String>> mdcMap = new AtomicReference<>();
    when(workerRun.call()).then(invocation -> {
      mdcMap.set(MDC.getCopyOfContextMap());
      return SUCCESS_OUTPUT;
    });

    jobSubmitter.run();

    verify(workerRun).call();

    assertEquals(
        ImmutableMap.of(
            "job_log_path", workerRun.getJobRoot() + "/" + LogClientSingleton.LOG_FILENAME),
        mdcMap.get());

    assertTrue(MDC.getCopyOfContextMap().isEmpty());
  }

  @Nested
  class OnlyOneJobIdRunning {

    /**
     * See {@link JobSubmitter#attemptJobSubmit()} to understand why we need to test that only one job
     * id can be successfully submited at once.
     */
    @Test
    public void testOnlyOneJobCanBeSubmittedAtOnce() throws Exception {
      final var jobDone = new AtomicReference<>(false);
      when(workerRun.call()).thenAnswer((a) -> {
        Thread.sleep(5000);
        jobDone.set(true);
        return SUCCESS_OUTPUT;
      });

      // Simulate the same job being submitted over and over again.
      final var simulatedJobSubmitterPool = Executors.newFixedThreadPool(10);
      while (!jobDone.get()) {
        // This sleep mimics our SchedulerApp loop.
        Thread.sleep(1000);
        simulatedJobSubmitterPool.submit(() -> {
          if (!jobDone.get()) {
            jobSubmitter.run();
          }
        });
      }

      simulatedJobSubmitterPool.shutdownNow();
      // This is expected to be called at least once due to the various threads.
      verify(persistence, atLeast(2)).getNextJob();
      // Assert that the job is actually only submitted once.
      verify(jobSubmitter, Mockito.times(1)).submitJob(Mockito.any());
    }

    @Test
    public void testSuccessShouldUnlockId() throws Exception {
      when(workerRun.call()).thenReturn(SUCCESS_OUTPUT);

      jobSubmitter.run();

      // This sleep mimics our SchedulerApp loop.
      Thread.sleep(1000);

      // If the id was not removed, the second call would not trigger submitJob().
      jobSubmitter.run();

      verify(persistence, Mockito.times(2)).getNextJob();
      verify(jobSubmitter, Mockito.times(2)).submitJob(Mockito.any());
    }

    @Test
    public void testFailureShouldUnlockId() throws Exception {
      when(workerRun.call()).thenThrow(new RuntimeException());

      jobSubmitter.run();

      // This sleep mimics our SchedulerApp loop.
      Thread.sleep(1000);

      // If the id was not removed, the second call would not trigger submitJob().
      jobSubmitter.run();

      verify(persistence, Mockito.times(2)).getNextJob();
      verify(jobSubmitter, Mockito.times(2)).submitJob(Mockito.any());
    }

  }

}
