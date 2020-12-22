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
import io.airbyte.scheduler.ScopeHelper;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class DefaultJobPersistenceTest {

  @SuppressWarnings("rawtypes")
  private static PostgreSQLContainer container;
  private static Database database;

  private static final Instant NOW = Instant.now();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String SCOPE = ScopeHelper.createScope(ConfigType.SYNC, CONNECTION_ID.toString());
  private static final JobConfig JOB_CONFIG = new JobConfig().withSync(new JobSyncConfig());
  private static final Path LOG_PATH = Path.of("/tmp/logs/all/the/way/down");

  private JobPersistence jobPersistence;
  private Supplier<Instant> timeSupplier;

  @SuppressWarnings("rawtypes")
  @BeforeAll
  public static void dbSetup() throws IOException, InterruptedException {
    container = new PostgreSQLContainer("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();

    container.copyFileToContainer(MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
    // execInContainer uses Docker's EXEC so it needs to be split up like this
    container.execInContainer("psql", "-d", "airbyte", "-U", "docker", "-a", "-f", "/etc/init.sql");

    database = Databases.createPostgresDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @AfterAll
  public static void tearDown() {
    container.stop();
    container.close();
  }

  @SuppressWarnings("unchecked")
  @BeforeEach
  public void setup() throws SQLException {
    // todo (cgardens) - truncate whole db.
    database.query(ctx -> ctx.execute("DELETE FROM jobs"));
    database.query(ctx -> ctx.execute("DELETE FROM attempts"));

    timeSupplier = mock(Supplier.class);
    when(timeSupplier.get()).thenReturn(NOW);

    jobPersistence = new DefaultJobPersistence(database, timeSupplier);
  }

  private Result<Record> getJobRecord(long jobId) throws SQLException {
    return database.query(ctx -> ctx.fetch(DefaultJobPersistence.BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId));
  }

  @Test
  public void testCreateJobAndGetWithoutAttemptJob() throws IOException {
    when(timeSupplier.get()).thenReturn(NOW);
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobNoAttempts(jobId, JobStatus.PENDING);
    assertEquals(expected, actual);
  }

  @Test
  void testResetJob() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
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
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);

    jobPersistence.cancelJob(jobId);
    assertThrows(IllegalStateException.class, () -> jobPersistence.resetJob(jobId));

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.CANCELLED, updated.getStatus());
  }

  @Test
  void testCancelJob() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.cancelJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.CANCELLED, updated.getStatus());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
  }

  @Test
  void testCancelJobAlreadyTerminal() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    jobPersistence.cancelJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.SUCCEEDED, updated.getStatus());
  }

  @Test
  void failJob() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.failJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.FAILED, updated.getStatus());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
  }

  @Test
  void testFailJobAlreadyTerminal() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    jobPersistence.failJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(JobStatus.SUCCEEDED, updated.getStatus());
  }

  @Test
  void testCreateAttempt() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    jobPersistence.createAttempt(jobId, LOG_PATH);

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.RUNNING, AttemptStatus.RUNNING);
    assertEquals(expected, actual);
  }

  @Test
  void testCreateAttemptAttemptId() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
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
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    assertThrows(IllegalStateException.class, () -> jobPersistence.createAttempt(jobId, LOG_PATH));

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.RUNNING, AttemptStatus.RUNNING);
    assertEquals(expected, actual);
  }

  @Test
  void testCreateAttemptTerminal() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    assertThrows(IllegalStateException.class, () -> jobPersistence.createAttempt(jobId, LOG_PATH));

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.SUCCEEDED, AttemptStatus.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testCompleteAttemptFailed() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.failAttempt(jobId, attemptNumber);
    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.INCOMPLETE, AttemptStatus.FAILED);
    assertEquals(expected, actual);
  }

  @Test
  void testCompleteAttemptSuccess() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.succeedAttempt(jobId, attemptNumber);
    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.SUCCEEDED, AttemptStatus.SUCCEEDED);
    assertEquals(expected, actual);
  }

  @Test
  void testWriteOutput() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    final JobOutput jobOutput = new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_CATALOG);
    jobPersistence.writeOutput(jobId, attemptNumber, jobOutput);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(Optional.of(jobOutput), updated.getAttempts().get(0).getOutput());
    assertNotEquals(created.getAttempts().get(0).getUpdatedAtInSecond(), updated.getAttempts().get(0).getUpdatedAtInSecond());
  }

  @Test
  public void testListJobs() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);

    final List<Job> actualList = jobPersistence.listJobs(JobConfig.ConfigType.SYNC, CONNECTION_ID.toString());

    final Job actual = actualList.get(0);
    final Job expected = getExpectedJobNoAttempts(jobId, JobStatus.PENDING);

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testListJobsWithMultipleAttempts() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber0 = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failAttempt(jobId, attemptNumber0);
    final Path secondAttemptLogPath = LOG_PATH.resolve("2");
    final int attemptNumber1 = jobPersistence.createAttempt(jobId, secondAttemptLogPath);
    jobPersistence.succeedAttempt(jobId, attemptNumber1);

    final List<Job> actualList = jobPersistence.listJobs(JobConfig.ConfigType.SYNC, CONNECTION_ID.toString());

    final Job actual = actualList.get(0);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.SUCCEEDED, AttemptStatus.FAILED);
    final Attempt expectedAttempt2 = new Attempt(
        1L,
        jobId,
        secondAttemptLogPath,
        null,
        AttemptStatus.SUCCEEDED,
        NOW.getEpochSecond(),
        NOW.getEpochSecond(),
        null);
    expected.getAttempts().add(expectedAttempt2);

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testListJobsWithStatus() throws IOException {
    // not failed.
    jobPersistence.createJob(SCOPE, JOB_CONFIG);
    // failed
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failAttempt(jobId, attemptNumber);

    final List<Job> actualList = jobPersistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.INCOMPLETE);

    final Job actual = actualList.get(0);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.INCOMPLETE, AttemptStatus.FAILED);

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testGetLastSyncJobForConnectionId() throws IOException {
    jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);

    final Optional<Job> actual = jobPersistence.getLastSyncJob(CONNECTION_ID);

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJob(jobId, JobStatus.PENDING, Collections.emptyList(), afterNow.getEpochSecond()), actual.get());
  }

  @Test
  public void testGetLastSyncJobForConnectionIdEmpty() throws IOException {
    final Optional<Job> actual = jobPersistence.getLastSyncJob(CONNECTION_ID);

    assertTrue(actual.isEmpty());
  }

  @Test
  public void testGetCurrentStateForConnectionIdNoState() throws IOException {
    // no state when the connection has never had a job.
    checkCurrentState(null, jobPersistence);

    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    // no state when connection has a job but it has not completed that has not completed
    checkCurrentState(null, jobPersistence);

    jobPersistence.failJob(jobId);

    // no state when connection has a job but it is failed.
    checkCurrentState(null, jobPersistence);

    jobPersistence.cancelJob(jobId);

    // no state when connection has a job but it is cancelled.
    checkCurrentState(null, jobPersistence);

    final JobOutput jobOutput1 = new JobOutput()
        .withSync(new StandardSyncOutput().withState(new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", "1")))));
    jobPersistence.writeOutput(jobId, attemptNumber, jobOutput1);
    jobPersistence.succeedAttempt(jobId, attemptNumber);

    // job 1 state, after first success.
    checkCurrentState(jobOutput1.getSync().getState(), jobPersistence);

    when(timeSupplier.get()).thenReturn(NOW.plusSeconds(1000));
    final long jobId2 = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final int attemptNumber2 = jobPersistence.createAttempt(jobId2, LOG_PATH);

    // job 1 state, second job created.
    checkCurrentState(jobOutput1.getSync().getState(), jobPersistence);

    jobPersistence.failJob(jobId2);

    // job 1 state, second job failed.
    checkCurrentState(jobOutput1.getSync().getState(), jobPersistence);

    jobPersistence.cancelJob(jobId2);

    // job 1 state, second job cancelled
    checkCurrentState(jobOutput1.getSync().getState(), jobPersistence);

    final JobOutput jobOutput2 = new JobOutput()
        .withSync(new StandardSyncOutput().withState(new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", "2")))));
    jobPersistence.writeOutput(jobId2, attemptNumber2, jobOutput2);
    jobPersistence.succeedAttempt(jobId2, attemptNumber2);

    // job 2 state, after second job success.
    checkCurrentState(jobOutput2.getSync().getState(), jobPersistence);
  }

  private static void checkCurrentState(State expectedState, JobPersistence jobPersistence) throws IOException {
    final Optional<State> currentState = jobPersistence.getCurrentState(CONNECTION_ID);

    if (expectedState != null) {
      assertTrue(currentState.isPresent());
      assertEquals(expectedState, currentState.get());
    } else {
      assertTrue(currentState.isEmpty());
    }
  }

  @Test
  public void testGetOldestPendingJob() throws IOException {
    final long jobId = createJobAt(NOW);
    createJobAt(NOW.plusSeconds(1000));

    final Optional<Job> actual = jobPersistence.getNextJob();

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJobNoAttempts(jobId, JobStatus.PENDING), actual.get());
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

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJobNoAttempts(jobId2, JobStatus.PENDING), actual.get());
  }

  @Test
  public void testGetOldestPendingJobWithOtherJobWithSameScopeCancelled() throws IOException {
    // create a job and set it to incomplete.
    final long jobId = createJobAt(NOW.minusSeconds(1000));
    jobPersistence.cancelJob(jobId);

    // create a pending job.
    final long jobId2 = createJobAt(NOW);

    final Optional<Job> actual = jobPersistence.getNextJob();

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJobNoAttempts(jobId2, JobStatus.PENDING), actual.get());
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

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJobNoAttempts(jobId2, JobStatus.PENDING), actual.get());
  }

  private long createJobAt(Instant created_at) throws IOException {
    when(timeSupplier.get()).thenReturn(created_at);
    return jobPersistence.createJob(SCOPE, JOB_CONFIG);
  }

  @Test
  public void testGetOldestPendingJobOnlyPendingJobs() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    jobPersistence.cancelJob(jobId);

    final Optional<Job> actual = jobPersistence.getNextJob();

    assertTrue(actual.isEmpty());
  }

  @Test
  void testGetNextJobWithMultipleAttempts() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    jobPersistence.resetJob(jobId);

    final Optional<Job> actual = jobPersistence.getNextJob();
    final Job expected = getExpectedJobTwoAttempts(jobId, JobStatus.PENDING, AttemptStatus.FAILED);

    assertTrue(actual.isPresent());
    assertEquals(expected, actual.get());
  }

  @Test
  void testGetCurrentStateWithMultipleAttempts() throws IOException {
    final State state = new State().withState(Jsons.jsonNode(ImmutableMap.of("checkpoint", 4)));
    final JobOutput jobOutput = new JobOutput().withOutputType(OutputType.SYNC).withSync(new StandardSyncOutput().withState(state));

    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    final int attemptId = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.writeOutput(jobId, attemptId, jobOutput);
    jobPersistence.succeedAttempt(jobId, attemptId);

    final Optional<State> actual = jobPersistence.getCurrentState(UUID.fromString(ScopeHelper.getConfigId(SCOPE)));

    assertTrue(actual.isPresent());
    assertEquals(state, actual.get());
  }

  @Test
  void testGetLastSyncJobWithMultipleAttempts() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));
    jobPersistence.failAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));

    final Optional<Job> actual = jobPersistence.getLastSyncJob(UUID.fromString(ScopeHelper.getConfigId(SCOPE)));
    final Job expected = getExpectedJobTwoAttempts(jobId, JobStatus.INCOMPLETE, AttemptStatus.FAILED);

    assertTrue(actual.isPresent());
    assertEquals(expected, actual.get());
  }

  @Test
  public void testGetJobFromRecord() throws IOException, SQLException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);

    final Optional<Job> actual = DefaultJobPersistence.getJobFromResult(getJobRecord(jobId));
    final Job expected = getExpectedJobNoAttempts(jobId, JobStatus.PENDING);

    assertTrue(actual.isPresent());
    assertEquals(expected, actual.get());
  }

  private Job getExpectedJobNoAttempts(long jobId, JobStatus jobStatus) {
    return getExpectedJob(jobId, jobStatus, Collections.emptyList());
  }

  private Job getExpectedJobTwoAttempts(long jobId, JobStatus jobStatus, AttemptStatus attemptStatus) {
    final Job job = getExpectedJobOneAttempt(jobId, jobStatus, attemptStatus);
    job.getAttempts().add(new Attempt(
        1L,
        jobId,
        LOG_PATH,
        null,
        attemptStatus,
        NOW.getEpochSecond(),
        NOW.getEpochSecond(),
        null));

    return job;
  }

  private Job getExpectedJobOneAttempt(long jobId, JobStatus jobStatus, AttemptStatus attemptStatus) {
    final Attempt attempt = new Attempt(
        0L,
        jobId,
        LOG_PATH,
        null,
        attemptStatus,
        NOW.getEpochSecond(),
        NOW.getEpochSecond(),
        null);

    return getExpectedJob(jobId, jobStatus, Lists.newArrayList(attempt));
  }

  private Job getExpectedJob(long jobId, JobStatus jobStatus, List<Attempt> attempts) {
    return getExpectedJob(jobId, jobStatus, attempts, NOW.getEpochSecond());
  }

  private Job getExpectedJob(long jobId, JobStatus jobStatus, List<Attempt> attempts, long time) {
    return new Job(
        jobId,
        SCOPE,
        JOB_CONFIG,
        attempts,
        jobStatus,
        null,
        time,
        time);
  }

}
