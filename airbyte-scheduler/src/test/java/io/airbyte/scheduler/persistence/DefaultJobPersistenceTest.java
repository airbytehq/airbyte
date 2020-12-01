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
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.StandardSync;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.AttemptStatus;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.ScopeHelper;
import io.airbyte.scheduler.persistence.JobPersistence.CancellationReason;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
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
  private static final JobConfig JOB_CONFIG =
      new JobConfig().withSync(new JobSyncConfig().withStandardSync(new StandardSync().withConnectionId(CONNECTION_ID)));
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

  // todo add that it doesn't do anything if in terminal state.
  @Test
  void testResetJob() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.resetJob(jobId);

    final Job updated = jobPersistence.getJob(jobId);

    assertEquals(JobStatus.PENDING, updated.getStatus());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
  }

  @Test
  void testCancelJob() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.cancelJob(jobId, CancellationReason.TOO_MANY_FAILURES);

    final Job updated = jobPersistence.getJob(jobId);

    assertEquals(JobStatus.CANCELLED, updated.getStatus());
    assertTrue(updated.getCancellationReason().isPresent());
    assertEquals(CancellationReason.TOO_MANY_FAILURES, updated.getCancellationReason().get());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
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
  void testCompleteAttemptFailed() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final long attemptId = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.completeAttemptFailed(jobId, attemptId);
    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.FAILED, AttemptStatus.FAILED);
    assertEquals(expected, actual);
  }

  @Test
  void testCompleteAttemptSuccess() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final long attemptId = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.completeAttemptSuccess(jobId, attemptId);
    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.COMPLETED, AttemptStatus.COMPLETED);
    assertEquals(expected, actual);
  }

  @Test
  void testWriteOutput() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final long attemptId = jobPersistence.createAttempt(jobId, LOG_PATH);
    final Job created = jobPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    final JobOutput jobOutput = new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_CATALOG);
    jobPersistence.writeOutput(jobId, attemptId, jobOutput);

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
  public void testListJobsWithStatus() throws IOException {
    // not failed.
    jobPersistence.createJob(SCOPE, JOB_CONFIG);
    // failed
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final long attemptId = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.completeAttemptFailed(jobId, attemptId);

    final List<Job> actualList = jobPersistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED);

    final Job actual = actualList.get(0);
    final Job expected = getExpectedJobOneAttempt(jobId, JobStatus.FAILED, AttemptStatus.FAILED);

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
  public void testGetOldestPendingJob() throws IOException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    jobPersistence.createJob(SCOPE, JOB_CONFIG);

    final Optional<Job> actual = jobPersistence.getOldestPendingJob();

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJobNoAttempts(jobId, JobStatus.PENDING), actual.get());
  }

  @Test
  public void testGetOldestPendingJobOnlyPendingJobs() throws IOException, SQLException {
    final long jobId = jobPersistence.createJob(SCOPE, JOB_CONFIG);
    jobPersistence.cancelJob(jobId, CancellationReason.TOO_MANY_FAILURES);

    final Optional<Job> actual = jobPersistence.getOldestPendingJob();

    assertTrue(actual.isEmpty());
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
        null,
        time,
        time);
  }

}
