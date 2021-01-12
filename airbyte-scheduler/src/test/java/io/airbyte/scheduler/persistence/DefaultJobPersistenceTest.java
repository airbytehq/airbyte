/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.scheduler.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobOutput.OutputType;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.AttemptStatus;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class DefaultJobPersistenceTest {

  private static PostgreSQLContainer<?> container;

  private static final Instant NOW = Instant.now();
  private static final Path LOG_PATH = Path.of("/tmp/logs/all/the/way/down");

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String SCOPE = CONNECTION_ID.toString();
  private static final String SPEC_SCOPE = SCOPE + "-spec";
  private static final String CHECK_SCOPE = SCOPE + "-check";
  private static final String SYNC_SCOPE = SCOPE + "-sync";

  private static final JobConfig SPEC_JOB_CONFIG = new JobConfig()
      .withConfigType(ConfigType.GET_SPEC)
      .withGetSpec(new JobGetSpecConfig());
  private static final JobConfig CHECK_JOB_CONFIG = new JobConfig()
      .withConfigType(ConfigType.CHECK_CONNECTION_DESTINATION)
      .withGetSpec(new JobGetSpecConfig());
  private static final JobConfig SYNC_JOB_CONFIG = new JobConfig()
      .withConfigType(ConfigType.SYNC)
      .withSync(new JobSyncConfig());

  private Database database;
  private Supplier<Instant> timeSupplier;
  private JobPersistence jobPersistence;

  @BeforeAll
  public static void dbSetup() throws Exception {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();

    container.copyFileToContainer(MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
    // execInContainer uses Docker's EXEC so it needs to be split up like this
    container.execInContainer("psql", "-d", "airbyte", "-U", "docker", "-a", "-f", "/etc/init.sql");
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @SuppressWarnings("unchecked")
  @BeforeEach
  public void setup() throws Exception {
    database = Databases.createPostgresDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());

    // todo (cgardens) - truncate whole db.
    database.query(ctx -> ctx.execute("DELETE FROM jobs"));
    database.query(ctx -> ctx.execute("DELETE FROM attempts"));

    timeSupplier = mock(Supplier.class);
    when(timeSupplier.get()).thenReturn(NOW);

    jobPersistence = new DefaultJobPersistence(database, timeSupplier);
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  private Result<Record> getJobRecord(long jobId) throws SQLException {
    return database.query(ctx -> ctx.fetch(DefaultJobPersistence.BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId));
  }

  @Test
  public void testCreateJobAndGetWithoutAttemptJob() throws IOException {
    when(timeSupplier.get()).thenReturn(NOW);
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  public void testCreateJobNoQueueing() throws IOException {
    when(timeSupplier.get()).thenReturn(NOW);
    final Optional<Long> jobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG);
    final Optional<Long> jobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG);

    assertTrue(jobId1.isPresent());
    assertTrue(jobId2.isEmpty());

    final Job actual = jobPersistence.getJob(jobId1.get());
    final Job expected = createJob(jobId1.get(), SYNC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  void testResetJob() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    final Job created = jobPersistence.getJob(jobId);

    jobPersistence.failAttempt(jobId, attemptNumber);
    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.resetJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.PENDING, updated.getStatus());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
  }

  @Test
  void testResetJobCancelled() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

    jobPersistence.cancelJob(jobId);
    assertThrows(IllegalStateException.class, () -> jobPersistence.resetJob(jobId));

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.CANCELLED, updated.getStatus());
  }

  @Test
  void testCancelJob() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.cancelJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.CANCELLED, updated.getStatus());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
  }

  @Test
  void testCancelJobAlreadyTerminal() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    jobPersistence.cancelJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.SUCCEEDED, updated.getStatus());
  }

  @Test
  void failJob() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.failJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.FAILED, updated.getStatus());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
  }

  @Test
  void testFailJobAlreadyTerminal() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    jobPersistence.failJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.SUCCEEDED, updated.getStatus());
  }

  @Test
  void testCreateAttempt() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    jobPersistence.createAttempt(jobId, LOG_PATH);

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.RUNNING,
        Lists.newArrayList(createAttempt(0L, jobId, AttemptStatus.RUNNING, LOG_PATH)),
        NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  void testCreateAttemptAttemptId() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber1 = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failAttempt(jobId, attemptNumber1);

    final Job jobAfterOneAttempts = jobPersistence.getJob(jobId);
    assertEquals(0, attemptNumber1);
    assertEquals(0, jobAfterOneAttempts.getAttempts().get(0).getId());

    final int attemptNumber2 = jobPersistence.createAttempt(jobId, LOG_PATH);
    final Job jobAfterTwoAttempts = jobPersistence.getJob(jobId);
    assertEquals(1, attemptNumber2);
    assertEquals(Sets.newHashSet(0L, 1L), jobAfterTwoAttempts.getAttempts().stream().map(Attempt::getId).collect(Collectors.toSet()));
  }

  @Test
  void testCreateAttemptWhileAttemptAlreadyRunning() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    jobPersistence.createAttempt(jobId, LOG_PATH);

    assertThrows(IllegalStateException.class, () -> jobPersistence.createAttempt(jobId, LOG_PATH));

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.RUNNING,
        Lists.newArrayList(createAttempt(0L, jobId, AttemptStatus.RUNNING, LOG_PATH)),
        NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  void testCreateAttemptTerminal() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    assertThrows(IllegalStateException.class, () -> jobPersistence.createAttempt(jobId, LOG_PATH));

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.SUCCEEDED,
        Lists.newArrayList(createAttempt(0L, jobId, AttemptStatus.SUCCEEDED, LOG_PATH)),
        NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  void testCompleteAttemptFailed() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.failAttempt(jobId, attemptNumber);

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.INCOMPLETE,
        Lists.newArrayList(createAttempt(0L, jobId, AttemptStatus.FAILED, LOG_PATH)),
        NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  void testCompleteAttemptSuccess() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.succeedAttempt(jobId, attemptNumber);

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.SUCCEEDED,
        Lists.newArrayList(createAttempt(0L, jobId, AttemptStatus.SUCCEEDED, LOG_PATH)),
        NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  void testWriteOutput() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    final Job created = jobPersistence.getJob(jobId);
    final JobOutput jobOutput = new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_CATALOG);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.writeOutput(jobId, attemptNumber, jobOutput);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(Optional.of(jobOutput), updated.getAttempts().get(0).getOutput());
    assertNotEquals(created.getAttempts().get(0).getUpdatedAtInSecond(), updated.getAttempts().get(0).getUpdatedAtInSecond());
  }

  @Test
  public void testListJobs() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

    final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString());

    final Job actual = actualList.get(0);
    final Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testListJobsWithMultipleAttempts() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber0 = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.failAttempt(jobId, attemptNumber0);

    final Path secondAttemptLogPath = LOG_PATH.resolve("2");
    final int attemptNumber1 = jobPersistence.createAttempt(jobId, secondAttemptLogPath);

    jobPersistence.succeedAttempt(jobId, attemptNumber1);

    final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString());

    final Job actual = actualList.get(0);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.SUCCEEDED,
        Lists.newArrayList(
            createAttempt(0L, jobId, AttemptStatus.FAILED, LOG_PATH),
            createAttempt(1L, jobId, AttemptStatus.SUCCEEDED, secondAttemptLogPath)),
        NOW.getEpochSecond());

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testListJobsWithStatus() throws IOException {
    // not failed.
    final long pendingSpecJobId = jobPersistence.enqueueJob(SPEC_SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final long pendingSyncJobId = jobPersistence.enqueueJob(SYNC_SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    final long pendingCheckJobId = jobPersistence.enqueueJob(CHECK_SCOPE, CHECK_JOB_CONFIG).orElseThrow();

    // failed
    final long failedSpecJobId = jobPersistence.enqueueJob(SPEC_SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(failedSpecJobId, LOG_PATH);
    jobPersistence.failAttempt(failedSpecJobId, attemptNumber);

    final List<Job> allPendingJobs = jobPersistence.listJobsWithStatus(JobStatus.PENDING);
    final Job expectedPendingSpecJob =
        createJob(pendingSpecJobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Lists.newArrayList(), NOW.getEpochSecond(), SPEC_SCOPE);
    final Job expectedPendingCheckJob =
        createJob(pendingCheckJobId, CHECK_JOB_CONFIG, JobStatus.PENDING, Lists.newArrayList(), NOW.getEpochSecond(), CHECK_SCOPE);
    final Job expectedPendingSyncJob =
        createJob(pendingSyncJobId, SYNC_JOB_CONFIG, JobStatus.PENDING, Lists.newArrayList(), NOW.getEpochSecond(), SYNC_SCOPE);

    final List<Job> allPendingSyncAndSpecJobs = jobPersistence.listJobsWithStatus(Set.of(ConfigType.GET_SPEC, ConfigType.SYNC), JobStatus.PENDING);

    final List<Job> incompleteJobs = jobPersistence.listJobsWithStatus(SPEC_JOB_CONFIG.getConfigType(), JobStatus.INCOMPLETE);
    final Job actualIncompleteJob = incompleteJobs.get(0);
    final Job expectedIncompleteJob = createJob(
        failedSpecJobId,
        SPEC_JOB_CONFIG,
        JobStatus.INCOMPLETE,
        Lists.newArrayList(
            createAttempt(0L, failedSpecJobId, AttemptStatus.FAILED, LOG_PATH)),
        NOW.getEpochSecond(),
        SPEC_SCOPE);

    assertEquals(Sets.newHashSet(expectedPendingCheckJob, expectedPendingSpecJob, expectedPendingSyncJob), Sets.newHashSet(allPendingJobs));
    assertEquals(Sets.newHashSet(expectedPendingSpecJob, expectedPendingSyncJob), Sets.newHashSet(allPendingSyncAndSpecJobs));

    assertEquals(1, incompleteJobs.size());
    assertEquals(expectedIncompleteJob, actualIncompleteJob);
  }

  @Test
  public void testListJobsWithStatuses() throws IOException {
    // not failed.
    jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG);
    // failed
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failAttempt(jobId, attemptNumber);

    final List<Job> actualList = jobPersistence.listJobsWithStatus(JobStatus.INCOMPLETE);

    final Job actual = actualList.get(0);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.INCOMPLETE,
        Lists.newArrayList(
            createAttempt(0L, jobId, AttemptStatus.FAILED, LOG_PATH)),
        NOW.getEpochSecond());

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testGetLastSyncJobForConnectionId() throws IOException {
    final long jobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    jobPersistence.succeedAttempt(jobId1, jobPersistence.createAttempt(jobId1, LOG_PATH));

    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    final long jobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();

    final Optional<Job> actual = jobPersistence.getLastReplicationJob(CONNECTION_ID);
    Job expected = createJob(jobId2, SYNC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), afterNow.getEpochSecond());

    assertEquals(Optional.of(expected), actual);
  }

  @Test
  public void testGetLastSyncJobForConnectionIdEmpty() throws IOException {
    final Optional<Job> actual = jobPersistence.getLastReplicationJob(CONNECTION_ID);

    assertTrue(actual.isEmpty());
  }

  @Test
  public void testGetCurrentStateForConnectionIdNoState() throws IOException {
    // no state when the connection has never had a job.
    assertEquals(Optional.empty(), jobPersistence.getCurrentState(CONNECTION_ID));

    final long jobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    // no state when connection has a job but it has not completed that has not completed
    assertEquals(Optional.empty(), jobPersistence.getCurrentState(CONNECTION_ID));

    jobPersistence.failJob(jobId);

    // no state when connection has a job but it is failed.
    assertEquals(Optional.empty(), jobPersistence.getCurrentState(CONNECTION_ID));

    jobPersistence.cancelJob(jobId);

    // no state when connection has a job but it is cancelled.
    assertEquals(Optional.empty(), jobPersistence.getCurrentState(CONNECTION_ID));

    final JobOutput jobOutput1 = new JobOutput()
        .withSync(new StandardSyncOutput().withState(new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", "1")))));
    jobPersistence.writeOutput(jobId, attemptNumber, jobOutput1);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    // job 1 state, after first success.
    assertEquals(Optional.of(jobOutput1.getSync().getState()), jobPersistence.getCurrentState(CONNECTION_ID));

    when(timeSupplier.get()).thenReturn(NOW.plusSeconds(1000));
    final long jobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    final int attemptNumber2 = jobPersistence.createAttempt(jobId2, LOG_PATH);

    // job 1 state, second job created.
    assertEquals(Optional.of(jobOutput1.getSync().getState()), jobPersistence.getCurrentState(CONNECTION_ID));

    jobPersistence.failJob(jobId2);

    // job 1 state, second job failed.
    assertEquals(Optional.of(jobOutput1.getSync().getState()), jobPersistence.getCurrentState(CONNECTION_ID));

    jobPersistence.cancelJob(jobId2);

    // job 1 state, second job cancelled
    assertEquals(Optional.of(jobOutput1.getSync().getState()), jobPersistence.getCurrentState(CONNECTION_ID));

    final JobOutput jobOutput2 = new JobOutput()
        .withSync(new StandardSyncOutput().withState(new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", "2")))));
    jobPersistence.writeOutput(jobId2, attemptNumber2, jobOutput2);
    jobPersistence.succeedAttempt(jobId2, attemptNumber2);

    // job 2 state, after second job success.
    assertEquals(Optional.of(jobOutput2.getSync().getState()), jobPersistence.getCurrentState(CONNECTION_ID));
  }

  @Test
  public void testGetOldestPendingJob() throws IOException {
    final long jobId = createJobAt(NOW);
    createJobAt(NOW.plusSeconds(1000));

    final Optional<Job> actual = jobPersistence.getNextJob();

    Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(Optional.of(expected), actual);
  }

  @Test
  public void testGetOldestPendingJobWithOtherJobWithSameScopeRunning() throws IOException {
    // create a job and set it to running.
    final long jobId = createJobAt(NOW.minusSeconds(1000));
    jobPersistence.createAttempt(jobId, LOG_PATH);

    // create a pending job.
    createJobAt(NOW);

    final Optional<Job> actual = jobPersistence.getNextJob();

    assertTrue(actual.isEmpty());
  }

  @Test
  public void testGetOldestPendingJobWithOtherJobWithSameScopeIncomplete() throws IOException {
    // create a job and set it to incomplete.
    final long jobId = createJobAt(NOW.minusSeconds(1000));
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failAttempt(jobId, attemptNumber);

    // create a pending job.
    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    createJobAt(NOW);

    final Optional<Job> actual = jobPersistence.getNextJob();

    assertTrue(actual.isEmpty());
  }

  @Test
  public void testGetOldestPendingJobWithOtherJobWithSameScopeFailed() throws IOException {
    // create a job and set it to incomplete.
    final long jobId = createJobAt(NOW.minusSeconds(1000));
    jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failJob(jobId);

    // create a pending job.
    final long jobId2 = createJobAt(NOW);

    final Optional<Job> actual = jobPersistence.getNextJob();

    Job expected = createJob(jobId2, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(Optional.of(expected), actual);
  }

  @Test
  public void testGetOldestPendingJobWithOtherJobWithSameScopeCancelled() throws IOException {
    // create a job and set it to incomplete.
    final long jobId = createJobAt(NOW.minusSeconds(1000));
    jobPersistence.cancelJob(jobId);

    // create a pending job.
    final long jobId2 = createJobAt(NOW);

    final Optional<Job> actual = jobPersistence.getNextJob();

    Job expected = createJob(jobId2, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(Optional.of(expected), actual);
  }

  @Test
  public void testGetOldestPendingJobWithOtherJobWithSameScopeSucceeded() throws IOException {
    // create a job and set it to incomplete.
    final long jobId = createJobAt(NOW.minusSeconds(1000));
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    // create a pending job.
    final long jobId2 = createJobAt(NOW);

    final Optional<Job> actual = jobPersistence.getNextJob();

    Job expected = createJob(jobId2, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(Optional.of(expected), actual);
  }

  private long createJobAt(Instant created_at) throws IOException {
    when(timeSupplier.get()).thenReturn(created_at);
    return jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
  }

  @Test
  public void testGetOldestPendingJobOnlyPendingJobs() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    jobPersistence.cancelJob(jobId);

    final Optional<Job> actual = jobPersistence.getNextJob();

    assertTrue(actual.isEmpty());
  }

  @Test
  void testGetNextJobWithMultipleAttempts() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    jobPersistence.resetJob(jobId);

    final Optional<Job> actual = jobPersistence.getNextJob();

    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.PENDING,
        Lists.newArrayList(
            createAttempt(0L, jobId, AttemptStatus.FAILED, LOG_PATH),
            createAttempt(1L, jobId, AttemptStatus.FAILED, LOG_PATH)),
        NOW.getEpochSecond());

    assertEquals(Optional.of(expected), actual);
  }

  @Test
  void testGetCurrentStateWithMultipleAttempts() throws IOException {
    final State state = new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", 4)));
    final JobOutput jobOutput = new JobOutput().withOutputType(OutputType.SYNC).withSync(new StandardSyncOutput().withState(state));

    final long jobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    final int attemptId = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.writeOutput(jobId, attemptId, jobOutput);
    jobPersistence.succeedAttempt(jobId, attemptId);

    final Optional<State> actual = jobPersistence.getCurrentState(UUID.fromString(SCOPE));

    assertEquals(Optional.of(state), actual);
  }

  @Test
  void testGetLastSyncJobWithMultipleAttempts() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));

    final Optional<Job> actual = jobPersistence.getLastReplicationJob(UUID.fromString(SCOPE));

    final Job expected = createJob(
        jobId,
        SYNC_JOB_CONFIG,
        JobStatus.INCOMPLETE,
        Lists.newArrayList(
            createAttempt(0L, jobId, AttemptStatus.FAILED, LOG_PATH),
            createAttempt(1L, jobId, AttemptStatus.FAILED, LOG_PATH)),
        NOW.getEpochSecond());

    assertEquals(Optional.of(expected), actual);
  }

  @Test
  public void testGetJobFromRecord() throws IOException, SQLException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

    final Optional<Job> actual = DefaultJobPersistence.getJobFromResult(getJobRecord(jobId));

    Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(Optional.of(expected), actual);
  }

  private static Attempt createAttempt(long id, long jobId, AttemptStatus status, Path logPath) {
    return new Attempt(
        id,
        jobId,
        logPath,
        null,
        status,
        NOW.getEpochSecond(),
        NOW.getEpochSecond(),
        null);
  }

  private static Job createJob(long id, JobConfig jobConfig, JobStatus status, List<Attempt> attempts, long time) {
    return createJob(id, jobConfig, status, attempts, time, SCOPE);
  }

  private static Job createJob(long id, JobConfig jobConfig, JobStatus status, List<Attempt> attempts, long time, String scope) {
    return new Job(
        id,
        jobConfig.getConfigType(),
        scope,
        jobConfig,
        attempts,
        status,
        null,
        time,
        time);
  }

}
