/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.persistence.job;

import static io.airbyte.db.instance.jobs.jooq.generated.Tables.AIRBYTE_METADATA;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.ATTEMPTS;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.JOBS;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.STREAM_STATS;
import static io.airbyte.db.instance.jobs.jooq.generated.Tables.SYNC_STATS;
import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Sqls;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.AirbyteProtocolVersionRange;
import io.airbyte.commons.version.Version;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StreamSyncStats;
import io.airbyte.config.SyncStats;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.instance.jobs.JobsDatabaseSchema;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.persistence.job.JobPersistence.AttemptStats;
import io.airbyte.persistence.job.JobPersistence.JobAttemptPair;
import io.airbyte.persistence.job.models.Attempt;
import io.airbyte.persistence.job.models.AttemptStatus;
import io.airbyte.persistence.job.models.AttemptWithJobInfo;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.persistence.job.models.JobWithStatusAndTimestamp;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.testcontainers.containers.PostgreSQLContainer;

@SuppressWarnings({"PMD.JUnitTestsShouldIncludeAssert", "PMD.AvoidDuplicateLiterals"})
@DisplayName("DefaultJobPersistance")
class DefaultJobPersistenceTest {

  private static final Instant NOW = Instant.now();
  private static final Path LOG_PATH = Path.of("/tmp/logs/all/the/way/down");
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String SCOPE = CONNECTION_ID.toString();
  private static final String SPEC_SCOPE = SCOPE + "-spec";
  private static final String CHECK_SCOPE = SCOPE + "-check";
  private static final String SYNC_SCOPE = SCOPE + "-sync";
  private static final UUID CONNECTION_ID2 = UUID.randomUUID();
  private static final JobConfig SPEC_JOB_CONFIG = new JobConfig()
      .withConfigType(ConfigType.GET_SPEC)
      .withGetSpec(new JobGetSpecConfig());
  private static final JobConfig CHECK_JOB_CONFIG = new JobConfig()
      .withConfigType(ConfigType.CHECK_CONNECTION_DESTINATION)
      .withGetSpec(new JobGetSpecConfig());
  private static final JobConfig SYNC_JOB_CONFIG = new JobConfig()
      .withConfigType(ConfigType.SYNC)
      .withSync(new JobSyncConfig());

  private static final JobConfig RESET_JOB_CONFIG = new JobConfig()
      .withConfigType(ConfigType.RESET_CONNECTION)
      .withSync(new JobSyncConfig());

  private static final int DEFAULT_MINIMUM_AGE_IN_DAYS = 30;
  private static final int DEFAULT_EXCESSIVE_NUMBER_OF_JOBS = 500;
  private static final int DEFAULT_MINIMUM_RECENCY_COUNT = 10;

  private static PostgreSQLContainer<?> container;
  private Database jobDatabase;
  private Supplier<Instant> timeSupplier;
  private JobPersistence jobPersistence;
  private DataSource dataSource;
  private DSLContext dslContext;

  @BeforeAll
  static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  static void dbDown() {
    container.close();
  }

  private static Attempt createAttempt(final int id, final long jobId, final AttemptStatus status, final Path logPath) {
    return new Attempt(
        id,
        jobId,
        logPath,
        null,
        status,
        null,
        null,
        NOW.getEpochSecond(),
        NOW.getEpochSecond(),
        NOW.getEpochSecond());
  }

  private static Attempt createUnfinishedAttempt(final int id, final long jobId, final AttemptStatus status, final Path logPath) {
    return new Attempt(
        id,
        jobId,
        logPath,
        null,
        status,
        null,
        null,
        NOW.getEpochSecond(),
        NOW.getEpochSecond(),
        null);
  }

  private static Job createJob(final long id, final JobConfig jobConfig, final JobStatus status, final List<Attempt> attempts, final long time) {
    return createJob(id, jobConfig, status, attempts, time, SCOPE);
  }

  private static Job createJob(
                               final long id,
                               final JobConfig jobConfig,
                               final JobStatus status,
                               final List<Attempt> attempts,
                               final long time,
                               final String scope) {
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

  @SuppressWarnings("unchecked")
  @BeforeEach
  void setup() throws Exception {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(dataSource, dslContext);
    jobDatabase = databaseProviders.createNewJobsDatabase();
    resetDb();

    timeSupplier = mock(Supplier.class);
    when(timeSupplier.get()).thenReturn(NOW);

    jobPersistence = new DefaultJobPersistence(jobDatabase, timeSupplier, DEFAULT_MINIMUM_AGE_IN_DAYS, DEFAULT_EXCESSIVE_NUMBER_OF_JOBS,
        DEFAULT_MINIMUM_RECENCY_COUNT);
  }

  @AfterEach
  void tearDown() throws Exception {
    dslContext.close();
    DataSourceFactory.close(dataSource);
  }

  private void resetDb() throws SQLException {
    // todo (cgardens) - truncate whole db.
    jobDatabase.query(ctx -> ctx.truncateTable(JOBS).cascade().execute());
    jobDatabase.query(ctx -> ctx.truncateTable(ATTEMPTS).cascade().execute());
    jobDatabase.query(ctx -> ctx.truncateTable(AIRBYTE_METADATA).cascade().execute());
    jobDatabase.query(ctx -> ctx.truncateTable(SYNC_STATS));
  }

  private Result<Record> getJobRecord(final long jobId) throws SQLException {
    return jobDatabase.query(ctx -> ctx.fetch(DefaultJobPersistence.BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId));
  }

  @Test
  @DisplayName("Should set a job to incomplete if an attempt fails")
  void testCompleteAttemptFailed() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.failAttempt(jobId, attemptNumber);

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.INCOMPLETE,
        Lists.newArrayList(createAttempt(0, jobId, AttemptStatus.FAILED, LOG_PATH)),
        NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("Should set a job to succeeded if an attempt succeeds")
  void testCompleteAttemptSuccess() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

    jobPersistence.succeedAttempt(jobId, attemptNumber);

    final Job actual = jobPersistence.getJob(jobId);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.SUCCEEDED,
        Lists.newArrayList(createAttempt(0, jobId, AttemptStatus.SUCCEEDED, LOG_PATH)),
        NOW.getEpochSecond());
    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("Should be able to read what is written")
  void testWriteOutput() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    final Job created = jobPersistence.getJob(jobId);
    final SyncStats syncStats =
        new SyncStats().withBytesEmitted(100L).withRecordsEmitted(9L).withRecordsCommitted(10L).withDestinationStateMessagesEmitted(1L)
            .withSourceStateMessagesEmitted(4L).withMaxSecondsBeforeSourceStateMessageEmitted(5L).withMeanSecondsBeforeSourceStateMessageEmitted(2L)
            .withMaxSecondsBetweenStateMessageEmittedandCommitted(10L).withMeanSecondsBetweenStateMessageEmittedandCommitted(3L);
    final FailureReason failureReason1 = new FailureReason().withFailureOrigin(FailureOrigin.DESTINATION).withFailureType(FailureType.SYSTEM_ERROR)
        .withExternalMessage("There was a normalization error");
    final FailureReason failureReason2 = new FailureReason().withFailureOrigin(FailureOrigin.SOURCE).withFailureType(FailureType.CONFIG_ERROR)
        .withExternalMessage("There was another normalization error");

    final NormalizationSummary normalizationSummary =
        new NormalizationSummary().withStartTime(10L).withEndTime(500L).withFailures(List.of(failureReason1, failureReason2));
    final StandardSyncOutput standardSyncOutput =
        new StandardSyncOutput().withStandardSyncSummary(new StandardSyncSummary().withTotalStats(syncStats))
            .withNormalizationSummary(normalizationSummary);
    final JobOutput jobOutput = new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_CATALOG).withSync(standardSyncOutput);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.writeOutput(jobId, attemptNumber, jobOutput);

    final Job updated = jobPersistence.getJob(jobId);

    assertEquals(Optional.of(jobOutput), updated.getAttempts().get(0).getOutput());
    assertNotEquals(created.getAttempts().get(0).getUpdatedAtInSecond(), updated.getAttempts().get(0).getUpdatedAtInSecond());

    final SyncStats storedSyncStats = jobPersistence.getAttemptStats(jobId, attemptNumber).combinedStats();
    assertEquals(100L, storedSyncStats.getBytesEmitted());
    assertEquals(9L, storedSyncStats.getRecordsEmitted());
    assertEquals(10L, storedSyncStats.getRecordsCommitted());
    assertEquals(4L, storedSyncStats.getSourceStateMessagesEmitted());
    assertEquals(1L, storedSyncStats.getDestinationStateMessagesEmitted());
    assertEquals(5L, storedSyncStats.getMaxSecondsBeforeSourceStateMessageEmitted());
    assertEquals(2L, storedSyncStats.getMeanSecondsBeforeSourceStateMessageEmitted());
    assertEquals(10L, storedSyncStats.getMaxSecondsBetweenStateMessageEmittedandCommitted());
    assertEquals(3L, storedSyncStats.getMeanSecondsBetweenStateMessageEmittedandCommitted());

    final NormalizationSummary storedNormalizationSummary = jobPersistence.getNormalizationSummary(jobId, attemptNumber).stream().findFirst().get();
    assertEquals(10L, storedNormalizationSummary.getStartTime());
    assertEquals(500L, storedNormalizationSummary.getEndTime());
    assertEquals(List.of(failureReason1, failureReason2), storedNormalizationSummary.getFailures());
  }

  @Test
  @DisplayName("Should be able to read attemptFailureSummary that was written")
  void testWriteAttemptFailureSummary() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
    final Job created = jobPersistence.getJob(jobId);
    final AttemptFailureSummary failureSummary = new AttemptFailureSummary().withFailures(
        Collections.singletonList(new FailureReason().withFailureOrigin(FailureOrigin.SOURCE)));

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    jobPersistence.writeAttemptFailureSummary(jobId, attemptNumber, failureSummary);

    final Job updated = jobPersistence.getJob(jobId);
    assertEquals(Optional.of(failureSummary), updated.getAttempts().get(0).getFailureSummary());
    assertNotEquals(created.getAttempts().get(0).getUpdatedAtInSecond(), updated.getAttempts().get(0).getUpdatedAtInSecond());
  }

  @Nested
  @DisplayName("Stats Related Tests")
  class Stats {

    @Test
    @DisplayName("Writing stats the first time should only write record and bytes information correctly")
    void testWriteStatsFirst() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
      final var streamStats = List.of(
          new StreamSyncStats().withStreamName("name1").withStreamNamespace("ns")
              .withStats(new SyncStats().withBytesEmitted(500L).withRecordsEmitted(500L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)),
          new StreamSyncStats().withStreamName("name2").withStreamNamespace("ns")
              .withStats(new SyncStats().withBytesEmitted(500L).withRecordsEmitted(500L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobId, attemptNumber, 1000, 1000, 1000, 1000, streamStats);

      final AttemptStats stats = jobPersistence.getAttemptStats(jobId, attemptNumber);
      final var combined = stats.combinedStats();
      assertEquals(1000, combined.getBytesEmitted());
      assertEquals(1000, combined.getRecordsEmitted());
      assertEquals(1000, combined.getEstimatedBytes());
      assertEquals(1000, combined.getEstimatedRecords());

      // As of this writing, committed and state messages are not expected.
      assertEquals(null, combined.getRecordsCommitted());
      assertEquals(null, combined.getDestinationStateMessagesEmitted());

      final var actStreamStats = stats.perStreamStats();
      assertEquals(2, actStreamStats.size());
      assertEquals(streamStats, actStreamStats);
    }

    @Test
    @DisplayName("Writing stats multiple times should write record and bytes information correctly without exceptions")
    void testWriteStatsRepeated() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

      // First write.
      var streamStats = List.of(
          new StreamSyncStats().withStreamName("name1").withStreamNamespace("ns")
              .withStats(new SyncStats().withBytesEmitted(500L).withRecordsEmitted(500L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobId, attemptNumber, 1000, 1000, 1000, 1000, streamStats);

      // Second write.
      when(timeSupplier.get()).thenReturn(Instant.now());
      streamStats = List.of(
          new StreamSyncStats().withStreamName("name1").withStreamNamespace("ns")
              .withStats(new SyncStats().withBytesEmitted(1000L).withRecordsEmitted(1000L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobId, attemptNumber, 2000, 2000, 2000, 2000, streamStats);

      final AttemptStats stats = jobPersistence.getAttemptStats(jobId, attemptNumber);
      final var combined = stats.combinedStats();
      assertEquals(2000, combined.getBytesEmitted());
      assertEquals(2000, combined.getRecordsEmitted());
      assertEquals(2000, combined.getEstimatedBytes());
      assertEquals(2000, combined.getEstimatedRecords());

      final var actStreamStats = stats.perStreamStats();
      assertEquals(1, actStreamStats.size());
      assertEquals(streamStats, actStreamStats);

    }

    @Test
    @DisplayName("Writing multiple stats of the same attempt id, stream name and namespace should update the previous record")
    void testWriteStatsUpsert() throws IOException, SQLException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

      // First write.
      var streamStats = List.of(
          new StreamSyncStats().withStreamName("name1").withStreamNamespace("ns")
              .withStats(new SyncStats().withBytesEmitted(500L).withRecordsEmitted(500L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobId, attemptNumber, 1000, 1000, 1000, 1000, streamStats);

      // Second write.
      when(timeSupplier.get()).thenReturn(Instant.now());
      streamStats = List.of(
          new StreamSyncStats().withStreamName("name1").withStreamNamespace("ns")
              .withStats(new SyncStats().withBytesEmitted(1000L).withRecordsEmitted(1000L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobId, attemptNumber, 2000, 2000, 2000, 2000, streamStats);

      final var syncStatsRec = jobDatabase.query(ctx -> {
        final var attemptId = DefaultJobPersistence.getAttemptId(jobId, attemptNumber, ctx);
        return ctx.fetch("SELECT * from sync_stats where attempt_id = ?", attemptId).stream().findFirst().get();
      });

      // Check time stamps to confirm upsert.
      assertNotEquals(syncStatsRec.get(SYNC_STATS.CREATED_AT), syncStatsRec.get(SYNC_STATS.UPDATED_AT));

      final var streamStatsRec = jobDatabase.query(ctx -> {
        final var attemptId = DefaultJobPersistence.getAttemptId(jobId, attemptNumber, ctx);
        return ctx.fetch("SELECT * from stream_stats where attempt_id = ?", attemptId).stream().findFirst().get();
      });
      // Check time stamps to confirm upsert.
      assertNotEquals(streamStatsRec.get(STREAM_STATS.CREATED_AT), streamStatsRec.get(STREAM_STATS.UPDATED_AT));
    }

    @Test
    @DisplayName("Writing multiple stats a stream with null namespace should write correctly without exceptions")
    void testWriteNullNamespace() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

      // First write.
      var streamStats = List.of(
          new StreamSyncStats().withStreamName("name1")
              .withStats(new SyncStats().withBytesEmitted(500L).withRecordsEmitted(500L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobId, attemptNumber, 1000, 1000, 1000, 1000, streamStats);

      // Second write.
      when(timeSupplier.get()).thenReturn(Instant.now());
      streamStats = List.of(
          new StreamSyncStats().withStreamName("name1")
              .withStats(new SyncStats().withBytesEmitted(1000L).withRecordsEmitted(1000L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobId, attemptNumber, 2000, 2000, 2000, 2000, streamStats);

      final AttemptStats stats = jobPersistence.getAttemptStats(jobId, attemptNumber);
      final var combined = stats.combinedStats();
      assertEquals(2000, combined.getBytesEmitted());
      assertEquals(2000, combined.getRecordsEmitted());
      assertEquals(2000, combined.getEstimatedBytes());
      assertEquals(2000, combined.getEstimatedRecords());

      final var actStreamStats = stats.perStreamStats();
      assertEquals(1, actStreamStats.size());
      assertEquals(streamStats, actStreamStats);
    }

    @Test
    @DisplayName("Writing multiple stats a stream with null namespace should write correctly without exceptions")
    void testGetStatsNoResult() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

      final AttemptStats stats = jobPersistence.getAttemptStats(jobId, attemptNumber);
      assertNull(stats.combinedStats());
      assertEquals(0, stats.perStreamStats().size());

    }

    @Test
    @DisplayName("Retrieving all attempts stats for a job should return the right information")
    void testGetMultipleStats() throws IOException {
      final long jobOneId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int jobOneAttemptNumberOne = jobPersistence.createAttempt(jobOneId, LOG_PATH);

      // First write for first attempt.
      var streamStats = List.of(
          new StreamSyncStats().withStreamName("name1")
              .withStats(new SyncStats().withBytesEmitted(500L).withRecordsEmitted(500L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobOneId, jobOneAttemptNumberOne, 1000, 1000, 1000, 1000, streamStats);

      // Second write for first attempt. This is the record that should be returned.
      when(timeSupplier.get()).thenReturn(Instant.now());
      streamStats = List.of(
          new StreamSyncStats().withStreamName("name1")
              .withStats(new SyncStats().withBytesEmitted(1000L).withRecordsEmitted(1000L).withEstimatedBytes(10000L).withEstimatedRecords(2000L)));
      jobPersistence.writeStats(jobOneId, jobOneAttemptNumberOne, 2000, 2000, 2000, 2000, streamStats);
      jobPersistence.failAttempt(jobOneId, jobOneAttemptNumberOne);

      // Second attempt for first job.
      final int jobOneAttemptNumberTwo = jobPersistence.createAttempt(jobOneId, LOG_PATH);
      jobPersistence.writeStats(jobOneId, jobOneAttemptNumberTwo, 1000, 1000, 1000, 1000, streamStats);

      // First attempt for second job.
      final long jobTwoId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int jobTwoAttemptNumberOne = jobPersistence.createAttempt(jobTwoId, LOG_PATH);
      jobPersistence.writeStats(jobTwoId, jobTwoAttemptNumberOne, 1000, 1000, 1000, 1000, streamStats);

      final var stats = jobPersistence.getAttemptStats(List.of(jobOneId, jobTwoId));
      final var exp = Map.of(
          new JobAttemptPair(jobOneId, jobOneAttemptNumberOne),
          new AttemptStats(
              new SyncStats().withRecordsEmitted(2000L).withBytesEmitted(2000L).withEstimatedBytes(2000L).withEstimatedRecords(2000L),
              List.of(new StreamSyncStats().withStreamName("name1").withStats(
                  new SyncStats().withEstimatedBytes(10000L).withEstimatedRecords(2000L).withBytesEmitted(1000L).withRecordsEmitted(1000L)))),
          new JobAttemptPair(jobOneId, jobOneAttemptNumberTwo),
          new AttemptStats(
              new SyncStats().withRecordsEmitted(1000L).withBytesEmitted(1000L).withEstimatedBytes(1000L).withEstimatedRecords(1000L),
              List.of(new StreamSyncStats().withStreamName("name1").withStats(
                  new SyncStats().withEstimatedBytes(10000L).withEstimatedRecords(2000L).withBytesEmitted(1000L).withRecordsEmitted(1000L)))),
          new JobAttemptPair(jobTwoId, jobTwoAttemptNumberOne),
          new AttemptStats(
              new SyncStats().withRecordsEmitted(1000L).withBytesEmitted(1000L).withEstimatedBytes(1000L).withEstimatedRecords(1000L),
              List.of(new StreamSyncStats().withStreamName("name1").withStats(
                  new SyncStats().withEstimatedBytes(10000L).withEstimatedRecords(2000L).withBytesEmitted(1000L).withRecordsEmitted(1000L)))));

      assertEquals(exp, stats);

    }

    @Test
    @DisplayName("Retrieving stats for an empty list should not cause an exception.")
    void testGetStatsForEmptyJobList() throws IOException {
      assertNotNull(jobPersistence.getAttemptStats(List.of()));
    }

    @Test
    @DisplayName("Retrieving stats for a bad job attempt input should not cause an exception.")
    void testGetStatsForBadJobAttemptInput() throws IOException {
      assertNotNull(jobPersistence.getAttemptStats(-1, -1));
    }

  }

  @Test
  @DisplayName("When getting the last replication job should return the most recently created job")
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
            createAttempt(0, jobId, AttemptStatus.FAILED, LOG_PATH),
            createAttempt(1, jobId, AttemptStatus.FAILED, LOG_PATH)),
        NOW.getEpochSecond());

    assertEquals(Optional.of(expected), actual);
  }

  @Test
  @DisplayName("Should extract a Job model from a JOOQ result set")
  void testGetJobFromRecord() throws IOException, SQLException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

    final Optional<Job> actual = DefaultJobPersistence.getJobFromResult(getJobRecord(jobId));

    final Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
    assertEquals(Optional.of(expected), actual);
  }

  @Test
  @DisplayName("Should be able to import database that was exported")
  void testExportImport() throws IOException, SQLException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber0 = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failAttempt(jobId, attemptNumber0);
    final Path secondAttemptLogPath = LOG_PATH.resolve("2");
    final int attemptNumber1 = jobPersistence.createAttempt(jobId, secondAttemptLogPath);
    jobPersistence.succeedAttempt(jobId, attemptNumber1);

    final Map<JobsDatabaseSchema, Stream<JsonNode>> inputStreams = jobPersistence.exportDatabase();

    // Collect streams to memory for temporary storage
    final Map<JobsDatabaseSchema, List<JsonNode>> tempData = new HashMap<>();
    final Map<JobsDatabaseSchema, Stream<JsonNode>> outputStreams = new HashMap<>();
    for (final Entry<JobsDatabaseSchema, Stream<JsonNode>> entry : inputStreams.entrySet()) {
      final List<JsonNode> tableData = entry.getValue().collect(Collectors.toList());
      tempData.put(entry.getKey(), tableData);
      outputStreams.put(entry.getKey(), tableData.stream());
    }
    resetDb();

    jobPersistence.importDatabase("test", outputStreams);

    final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString(), 9999, 0);
    final Job actual = actualList.get(0);
    final Job expected = createJob(
        jobId,
        SPEC_JOB_CONFIG,
        JobStatus.SUCCEEDED,
        Lists.newArrayList(
            createAttempt(0, jobId, AttemptStatus.FAILED, LOG_PATH),
            createAttempt(1, jobId, AttemptStatus.SUCCEEDED, secondAttemptLogPath)),
        NOW.getEpochSecond());

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  @DisplayName("Should return correct set of jobs when querying on end timestamp")
  void testListJobsWithTimestamp() throws IOException {
    // TODO : Once we fix the problem of precision loss in DefaultJobPersistence, change the test value
    // to contain milliseconds as well
    final Instant now = Instant.parse("2021-01-01T00:00:00Z");
    final Supplier<Instant> timeSupplier = incrementingSecondSupplier(now);

    jobPersistence = new DefaultJobPersistence(jobDatabase, timeSupplier, DEFAULT_MINIMUM_AGE_IN_DAYS, DEFAULT_EXCESSIVE_NUMBER_OF_JOBS,
        DEFAULT_MINIMUM_RECENCY_COUNT);
    final long syncJobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    final int syncJobAttemptNumber0 = jobPersistence.createAttempt(syncJobId, LOG_PATH);
    jobPersistence.failAttempt(syncJobId, syncJobAttemptNumber0);
    final Path syncJobSecondAttemptLogPath = LOG_PATH.resolve("2");
    final int syncJobAttemptNumber1 = jobPersistence.createAttempt(syncJobId, syncJobSecondAttemptLogPath);
    jobPersistence.failAttempt(syncJobId, syncJobAttemptNumber1);

    final long specJobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int specJobAttemptNumber0 = jobPersistence.createAttempt(specJobId, LOG_PATH);
    jobPersistence.failAttempt(specJobId, specJobAttemptNumber0);
    final Path specJobSecondAttemptLogPath = LOG_PATH.resolve("2");
    final int specJobAttemptNumber1 = jobPersistence.createAttempt(specJobId, specJobSecondAttemptLogPath);
    jobPersistence.succeedAttempt(specJobId, specJobAttemptNumber1);

    final List<Job> jobs = jobPersistence.listJobs(ConfigType.SYNC, Instant.EPOCH);
    assertEquals(jobs.size(), 1);
    assertEquals(jobs.get(0).getId(), syncJobId);
    assertEquals(jobs.get(0).getAttempts().size(), 2);
    assertEquals(jobs.get(0).getAttempts().get(0).getAttemptNumber(), 0);
    assertEquals(jobs.get(0).getAttempts().get(1).getAttemptNumber(), 1);

    final Path syncJobThirdAttemptLogPath = LOG_PATH.resolve("3");
    final int syncJobAttemptNumber2 = jobPersistence.createAttempt(syncJobId, syncJobThirdAttemptLogPath);
    jobPersistence.succeedAttempt(syncJobId, syncJobAttemptNumber2);

    final long newSyncJobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
    final int newSyncJobAttemptNumber0 = jobPersistence.createAttempt(newSyncJobId, LOG_PATH);
    jobPersistence.failAttempt(newSyncJobId, newSyncJobAttemptNumber0);
    final Path newSyncJobSecondAttemptLogPath = LOG_PATH.resolve("2");
    final int newSyncJobAttemptNumber1 = jobPersistence.createAttempt(newSyncJobId, newSyncJobSecondAttemptLogPath);
    jobPersistence.succeedAttempt(newSyncJobId, newSyncJobAttemptNumber1);

    final Long maxEndedAtTimestamp =
        jobs.get(0).getAttempts().stream().map(c -> c.getEndedAtInSecond().orElseThrow()).max(Long::compareTo).orElseThrow();

    final List<Job> secondQueryJobs = jobPersistence.listJobs(ConfigType.SYNC, Instant.ofEpochSecond(maxEndedAtTimestamp));
    assertEquals(secondQueryJobs.size(), 2);
    assertEquals(secondQueryJobs.get(0).getId(), syncJobId);
    assertEquals(secondQueryJobs.get(0).getAttempts().size(), 1);
    assertEquals(secondQueryJobs.get(0).getAttempts().get(0).getAttemptNumber(), 2);

    assertEquals(secondQueryJobs.get(1).getId(), newSyncJobId);
    assertEquals(secondQueryJobs.get(1).getAttempts().size(), 2);
    assertEquals(secondQueryJobs.get(1).getAttempts().get(0).getAttemptNumber(), 0);
    assertEquals(secondQueryJobs.get(1).getAttempts().get(1).getAttemptNumber(), 1);

    Long maxEndedAtTimestampAfterSecondQuery = -1L;
    for (final Job c : secondQueryJobs) {
      final List<Attempt> attempts = c.getAttempts();
      final Long maxEndedAtTimestampForJob = attempts.stream().map(attempt -> attempt.getEndedAtInSecond().orElseThrow())
          .max(Long::compareTo).orElseThrow();
      if (maxEndedAtTimestampForJob > maxEndedAtTimestampAfterSecondQuery) {
        maxEndedAtTimestampAfterSecondQuery = maxEndedAtTimestampForJob;
      }
    }

    assertEquals(0, jobPersistence.listJobs(ConfigType.SYNC, Instant.ofEpochSecond(maxEndedAtTimestampAfterSecondQuery)).size());
  }

  @Test
  @DisplayName("Should return correct list of AttemptWithJobInfo when querying on end timestamp, sorted by attempt end time")
  void testListAttemptsWithJobInfo() throws IOException {
    final Instant now = Instant.parse("2021-01-01T00:00:00Z");
    final Supplier<Instant> timeSupplier = incrementingSecondSupplier(now);
    jobPersistence = new DefaultJobPersistence(jobDatabase, timeSupplier, DEFAULT_MINIMUM_AGE_IN_DAYS, DEFAULT_EXCESSIVE_NUMBER_OF_JOBS,
        DEFAULT_MINIMUM_RECENCY_COUNT);

    final long job1 = jobPersistence.enqueueJob(SCOPE + "-1", SYNC_JOB_CONFIG).orElseThrow();
    final long job2 = jobPersistence.enqueueJob(SCOPE + "-2", SYNC_JOB_CONFIG).orElseThrow();

    final int job1Attempt1 = jobPersistence.createAttempt(job1, LOG_PATH.resolve("1"));
    final int job2Attempt1 = jobPersistence.createAttempt(job2, LOG_PATH.resolve("2"));
    jobPersistence.failAttempt(job1, job1Attempt1);
    jobPersistence.failAttempt(job2, job2Attempt1);

    final int job1Attempt2 = jobPersistence.createAttempt(job1, LOG_PATH.resolve("3"));
    final int job2Attempt2 = jobPersistence.createAttempt(job2, LOG_PATH.resolve("4"));
    jobPersistence.failAttempt(job2, job2Attempt2); // job 2 attempt 2 fails before job 1 attempt 2 fails
    jobPersistence.failAttempt(job1, job1Attempt2);

    final int job1Attempt3 = jobPersistence.createAttempt(job1, LOG_PATH.resolve("5"));
    final int job2Attempt3 = jobPersistence.createAttempt(job2, LOG_PATH.resolve("6"));
    jobPersistence.succeedAttempt(job1, job1Attempt3);
    jobPersistence.succeedAttempt(job2, job2Attempt3);

    final List<AttemptWithJobInfo> allAttempts = jobPersistence.listAttemptsWithJobInfo(ConfigType.SYNC, Instant.ofEpochSecond(0));
    assertEquals(6, allAttempts.size());

    assertEquals(job1, allAttempts.get(0).getJobInfo().getId());
    assertEquals(job1Attempt1, allAttempts.get(0).getAttempt().getAttemptNumber());

    assertEquals(job2, allAttempts.get(1).getJobInfo().getId());
    assertEquals(job2Attempt1, allAttempts.get(1).getAttempt().getAttemptNumber());

    assertEquals(job2, allAttempts.get(2).getJobInfo().getId());
    assertEquals(job2Attempt2, allAttempts.get(2).getAttempt().getAttemptNumber());

    assertEquals(job1, allAttempts.get(3).getJobInfo().getId());
    assertEquals(job1Attempt2, allAttempts.get(3).getAttempt().getAttemptNumber());

    assertEquals(job1, allAttempts.get(4).getJobInfo().getId());
    assertEquals(job1Attempt3, allAttempts.get(4).getAttempt().getAttemptNumber());

    assertEquals(job2, allAttempts.get(5).getJobInfo().getId());
    assertEquals(job2Attempt3, allAttempts.get(5).getAttempt().getAttemptNumber());

    final List<AttemptWithJobInfo> attemptsAfterTimestamp = jobPersistence.listAttemptsWithJobInfo(ConfigType.SYNC,
        Instant.ofEpochSecond(allAttempts.get(2).getAttempt().getEndedAtInSecond().orElseThrow()));
    assertEquals(3, attemptsAfterTimestamp.size());

    assertEquals(job1, attemptsAfterTimestamp.get(0).getJobInfo().getId());
    assertEquals(job1Attempt2, attemptsAfterTimestamp.get(0).getAttempt().getAttemptNumber());

    assertEquals(job1, attemptsAfterTimestamp.get(1).getJobInfo().getId());
    assertEquals(job1Attempt3, attemptsAfterTimestamp.get(1).getAttempt().getAttemptNumber());

    assertEquals(job2, attemptsAfterTimestamp.get(2).getJobInfo().getId());
    assertEquals(job2Attempt3, attemptsAfterTimestamp.get(2).getAttempt().getAttemptNumber());
  }

  private static Supplier<Instant> incrementingSecondSupplier(final Instant startTime) {
    // needs to be an array to work with lambda
    final int[] intArray = {0};

    final Supplier<Instant> timeSupplier = () -> startTime.plusSeconds(intArray[0]++);
    return timeSupplier;
  }

  @Test
  @DisplayName("Should have valid yaml schemas in exported database")
  void testYamlSchemas() throws IOException {
    final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
    final int attemptNumber0 = jobPersistence.createAttempt(jobId, LOG_PATH);
    jobPersistence.failAttempt(jobId, attemptNumber0);
    final Path secondAttemptLogPath = LOG_PATH.resolve("2");
    final int attemptNumber1 = jobPersistence.createAttempt(jobId, secondAttemptLogPath);
    jobPersistence.succeedAttempt(jobId, attemptNumber1);
    final JsonSchemaValidator jsonSchemaValidator = new JsonSchemaValidator();

    final Map<JobsDatabaseSchema, Stream<JsonNode>> inputStreams = jobPersistence.exportDatabase();
    inputStreams.forEach((tableSchema, tableStream) -> {
      final String tableName = tableSchema.name();
      final JsonNode schema = tableSchema.getTableDefinition();
      assertNotNull(schema,
          "Json schema files should be created in airbyte-persistence/job-persistence/src/main/resources/tables for every table in the Database to validate its content");
      tableStream.forEach(row -> {
        try {
          jsonSchemaValidator.ensure(schema, row);
        } catch (final JsonValidationException e) {
          fail(String.format("JSON Schema validation failed for %s with record %s", tableName, row.toPrettyString()));
        }
      });
    });
  }

  @Test
  void testSecretMigrationMetadata() throws IOException {
    boolean isMigrated = jobPersistence.isSecretMigrated();
    assertFalse(isMigrated);
    jobPersistence.setSecretMigrationDone();
    isMigrated = jobPersistence.isSecretMigrated();
    assertTrue(isMigrated);
  }

  @Test
  void testAirbyteProtocolVersionMaxMetadata() throws IOException {
    assertTrue(jobPersistence.getAirbyteProtocolVersionMax().isEmpty());

    final Version maxVersion1 = new Version("0.1.0");
    jobPersistence.setAirbyteProtocolVersionMax(maxVersion1);
    final Optional<Version> maxVersion1read = jobPersistence.getAirbyteProtocolVersionMax();
    assertEquals(maxVersion1, maxVersion1read.orElseThrow());

    final Version maxVersion2 = new Version("1.2.1");
    jobPersistence.setAirbyteProtocolVersionMax(maxVersion2);
    final Optional<Version> maxVersion2read = jobPersistence.getAirbyteProtocolVersionMax();
    assertEquals(maxVersion2, maxVersion2read.orElseThrow());
  }

  @Test
  void testAirbyteProtocolVersionMinMetadata() throws IOException {
    assertTrue(jobPersistence.getAirbyteProtocolVersionMin().isEmpty());

    final Version minVersion1 = new Version("1.1.0");
    jobPersistence.setAirbyteProtocolVersionMin(minVersion1);
    final Optional<Version> minVersion1read = jobPersistence.getAirbyteProtocolVersionMin();
    assertEquals(minVersion1, minVersion1read.orElseThrow());

    final Version minVersion2 = new Version("3.0.1");
    jobPersistence.setAirbyteProtocolVersionMin(minVersion2);
    final Optional<Version> minVersion2read = jobPersistence.getAirbyteProtocolVersionMin();
    assertEquals(minVersion2, minVersion2read.orElseThrow());
  }

  @Test
  void testAirbyteProtocolVersionRange() throws IOException {
    final Version v1 = new Version("1.5.0");
    final Version v2 = new Version("2.5.0");
    final Optional<AirbyteProtocolVersionRange> range = jobPersistence.getCurrentProtocolVersionRange();
    assertEquals(Optional.empty(), range);

    jobPersistence.setAirbyteProtocolVersionMax(v2);
    final Optional<AirbyteProtocolVersionRange> range2 = jobPersistence.getCurrentProtocolVersionRange();
    assertEquals(Optional.of(new AirbyteProtocolVersionRange(AirbyteProtocolVersion.DEFAULT_AIRBYTE_PROTOCOL_VERSION, v2)), range2);

    jobPersistence.setAirbyteProtocolVersionMin(v1);
    final Optional<AirbyteProtocolVersionRange> range3 = jobPersistence.getCurrentProtocolVersionRange();
    assertEquals(Optional.of(new AirbyteProtocolVersionRange(v1, v2)), range3);
  }

  private long createJobAt(final Instant created_at) throws IOException {
    when(timeSupplier.get()).thenReturn(created_at);
    return jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
  }

  @Nested
  class TemporalWorkflowInfo {

    @Test
    void testSuccessfulGet() throws IOException, SQLException {
      final var jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final var attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);

      final var defaultWorkflowId = jobPersistence.getAttemptTemporalWorkflowId(jobId, attemptNumber);
      assertTrue(defaultWorkflowId.isEmpty());

      jobDatabase.query(ctx -> ctx.execute(
          "UPDATE attempts SET temporal_workflow_id = '56a81f3a-006c-42d7-bce2-29d675d08ea4' WHERE job_id = ? AND attempt_number =?", jobId,
          attemptNumber));
      final var workflowId = jobPersistence.getAttemptTemporalWorkflowId(jobId, attemptNumber).get();
      assertEquals(workflowId, "56a81f3a-006c-42d7-bce2-29d675d08ea4");
    }

    @Test
    void testGetMissingAttempt() throws IOException {
      assertTrue(jobPersistence.getAttemptTemporalWorkflowId(0, 0).isEmpty());
    }

    @Test
    void testSuccessfulSet() throws IOException, SQLException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final var attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
      final var temporalWorkflowId = "test-id-usually-uuid";
      final var syncQueue = "SYNC";

      jobPersistence.setAttemptTemporalWorkflowInfo(jobId, attemptNumber, temporalWorkflowId, syncQueue);

      final var workflowId = jobPersistence.getAttemptTemporalWorkflowId(jobId, attemptNumber).get();
      assertEquals(workflowId, temporalWorkflowId);

      final var taskQueue = jobDatabase.query(ctx -> ctx.fetch(
          "SELECT processing_task_queue FROM attempts WHERE job_id = ? AND attempt_number =?", jobId,
          attemptNumber)).stream().findFirst().get().get("processing_task_queue", String.class);
      assertEquals(syncQueue, taskQueue);
    }

  }

  @Nested
  class GetAndSetVersion {

    @Test
    void testSetVersion() throws IOException {
      final String version = UUID.randomUUID().toString();
      jobPersistence.setVersion(version);
      assertEquals(version, jobPersistence.getVersion().orElseThrow());
    }

    @Test
    void testSetVersionReplacesExistingId() throws IOException {
      final String deploymentId1 = UUID.randomUUID().toString();
      final String deploymentId2 = UUID.randomUUID().toString();
      jobPersistence.setVersion(deploymentId1);
      jobPersistence.setVersion(deploymentId2);
      assertEquals(deploymentId2, jobPersistence.getVersion().orElseThrow());
    }

  }

  @Nested
  class GetAndSetDeployment {

    @Test
    void testSetDeployment() throws IOException {
      final UUID deploymentId = UUID.randomUUID();
      jobPersistence.setDeployment(deploymentId);
      assertEquals(deploymentId, jobPersistence.getDeployment().orElseThrow());
    }

    @Test
    void testSetDeploymentIdDoesNotReplaceExistingId() throws IOException {
      final UUID deploymentId1 = UUID.randomUUID();
      final UUID deploymentId2 = UUID.randomUUID();
      jobPersistence.setDeployment(deploymentId1);
      jobPersistence.setDeployment(deploymentId2);
      assertEquals(deploymentId1, jobPersistence.getDeployment().orElseThrow());
    }

  }

  @Nested
  @DisplayName("When cancelling job")
  class CancelJob {

    @Test
    @DisplayName("Should cancel job and leave job in cancelled state")
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
    @DisplayName("Should not raise an exception if job is already succeeded")
    void testCancelJobAlreadySuccessful() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
      jobPersistence.succeedAttempt(jobId, attemptNumber);

      assertDoesNotThrow(() -> jobPersistence.cancelJob(jobId));

      final Job updated = jobPersistence.getJob(jobId);
      assertEquals(JobStatus.SUCCEEDED, updated.getStatus());
    }

  }

  @Nested
  @DisplayName("When creating attempt")
  class CreateAttempt {

    @Test
    @DisplayName("Should create an attempt")
    void testCreateAttempt() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      jobPersistence.createAttempt(jobId, LOG_PATH);

      final Job actual = jobPersistence.getJob(jobId);
      final Job expected = createJob(
          jobId,
          SPEC_JOB_CONFIG,
          JobStatus.RUNNING,
          Lists.newArrayList(createUnfinishedAttempt(0, jobId, AttemptStatus.RUNNING, LOG_PATH)),
          NOW.getEpochSecond());
      assertEquals(expected, actual);
    }

    @Test
    @DisplayName("Should increment attempt id if creating multiple attemps")
    void testCreateAttemptAttemptId() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber1 = jobPersistence.createAttempt(jobId, LOG_PATH);
      jobPersistence.failAttempt(jobId, attemptNumber1);

      final Job jobAfterOneAttempts = jobPersistence.getJob(jobId);
      assertEquals(0, attemptNumber1);
      assertEquals(0, jobAfterOneAttempts.getAttempts().get(0).getAttemptNumber());

      final int attemptNumber2 = jobPersistence.createAttempt(jobId, LOG_PATH);
      final Job jobAfterTwoAttempts = jobPersistence.getJob(jobId);
      assertEquals(1, attemptNumber2);
      assertEquals(Sets.newHashSet(0, 1), jobAfterTwoAttempts.getAttempts().stream().map(Attempt::getAttemptNumber).collect(Collectors.toSet()));
    }

    @Test
    @DisplayName("Should not create an attempt if an attempt is running")
    void testCreateAttemptWhileAttemptAlreadyRunning() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      jobPersistence.createAttempt(jobId, LOG_PATH);

      assertThrows(IllegalStateException.class, () -> jobPersistence.createAttempt(jobId, LOG_PATH));

      final Job actual = jobPersistence.getJob(jobId);
      final Job expected = createJob(
          jobId,
          SPEC_JOB_CONFIG,
          JobStatus.RUNNING,
          Lists.newArrayList(createUnfinishedAttempt(0, jobId, AttemptStatus.RUNNING, LOG_PATH)),
          NOW.getEpochSecond());
      assertEquals(expected, actual);
    }

    @Test
    @DisplayName("Should not create an attempt if job is in terminal state")
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
          Lists.newArrayList(createAttempt(0, jobId, AttemptStatus.SUCCEEDED, LOG_PATH)),
          NOW.getEpochSecond());
      assertEquals(expected, actual);
    }

  }

  @Nested
  @DisplayName("When enqueueing job")
  class EnqueueJob {

    @Test
    @DisplayName("Should create initial job without attempt")
    void testCreateJobAndGetWithoutAttemptJob() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

      final Job actual = jobPersistence.getJob(jobId);
      final Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
      assertEquals(expected, actual);
    }

    @Test
    @DisplayName("Should not create a second job if a job under the same scope is in a non-terminal state")
    void testCreateJobNoQueueing() throws IOException {
      final Optional<Long> jobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG);
      final Optional<Long> jobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG);

      assertTrue(jobId1.isPresent());
      assertTrue(jobId2.isEmpty());

      final Job actual = jobPersistence.getJob(jobId1.get());
      final Job expected = createJob(jobId1.get(), SYNC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
      assertEquals(expected, actual);
    }

    @Test
    @DisplayName("Should create a second job if a previous job under the same scope has failed")
    void testCreateJobIfPrevJobFailed() throws IOException {
      final Optional<Long> jobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG);
      assertTrue(jobId1.isPresent());

      jobPersistence.failJob(jobId1.get());
      final Optional<Long> jobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG);
      assertTrue(jobId2.isPresent());

      final Job actual = jobPersistence.getJob(jobId2.get());
      final Job expected = createJob(jobId2.get(), SYNC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
      assertEquals(expected, actual);
    }

  }

  @Nested
  @DisplayName("When failing job")
  class FailJob {

    @Test
    @DisplayName("Should set job status to failed")
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
    @DisplayName("Should not raise an exception if job is already succeeded")
    void testFailJobAlreadySucceeded() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
      jobPersistence.succeedAttempt(jobId, attemptNumber);

      assertDoesNotThrow(() -> jobPersistence.failJob(jobId));

      final Job updated = jobPersistence.getJob(jobId);
      assertEquals(JobStatus.SUCCEEDED, updated.getStatus());
    }

  }

  @Nested
  @DisplayName("When getting last replication job")
  class GetLastReplicationJob {

    @Test
    @DisplayName("Should return nothing if no job exists")
    void testGetLastReplicationJobForConnectionIdEmpty() throws IOException {
      final Optional<Job> actual = jobPersistence.getLastReplicationJob(CONNECTION_ID);

      assertTrue(actual.isEmpty());
    }

    @Test
    @DisplayName("Should return the last sync job")
    void testGetLastSyncJobForConnectionId() throws IOException {
      final long jobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(jobId1, jobPersistence.createAttempt(jobId1, LOG_PATH));

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);
      final long jobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();

      final Optional<Job> actual = jobPersistence.getLastReplicationJob(CONNECTION_ID);
      final Job expected = createJob(jobId2, SYNC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), afterNow.getEpochSecond());

      assertEquals(Optional.of(expected), actual);
    }

    @Test
    @DisplayName("Should return the last reset job")
    void testGetLastResetJobForConnectionId() throws IOException {
      final long jobId1 = jobPersistence.enqueueJob(SCOPE, RESET_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(jobId1, jobPersistence.createAttempt(jobId1, LOG_PATH));

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);
      final long jobId2 = jobPersistence.enqueueJob(SCOPE, RESET_JOB_CONFIG).orElseThrow();

      final Optional<Job> actual = jobPersistence.getLastReplicationJob(CONNECTION_ID);
      final Job expected = createJob(jobId2, RESET_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), afterNow.getEpochSecond());

      assertEquals(Optional.of(expected), actual);
    }

  }

  @Nested
  @DisplayName("When getting last sync job")
  class GetLastSyncJob {

    @Test
    @DisplayName("Should return nothing if no job exists")
    void testGetLastSyncJobForConnectionIdEmpty() throws IOException {
      final Optional<Job> actual = jobPersistence.getLastSyncJob(CONNECTION_ID);

      assertTrue(actual.isEmpty());
    }

    @Test
    @DisplayName("Should return the last enqueued sync job")
    void testGetLastSyncJobForConnectionId() throws IOException {
      final long jobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(jobId1, jobPersistence.createAttempt(jobId1, LOG_PATH));

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);
      final long jobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(jobId2, LOG_PATH);

      // Return the latest sync job even if failed
      jobPersistence.failAttempt(jobId2, attemptNumber);
      final Attempt attempt = jobPersistence.getJob(jobId2).getAttempts().stream().findFirst().orElseThrow();
      jobPersistence.failJob(jobId2);

      final Optional<Job> actual = jobPersistence.getLastSyncJob(CONNECTION_ID);
      final Job expected = createJob(jobId2, SYNC_JOB_CONFIG, JobStatus.FAILED, List.of(attempt), afterNow.getEpochSecond());

      assertEquals(Optional.of(expected), actual);
    }

    @Test
    @DisplayName("Should return nothing if only reset job exists")
    void testGetLastSyncJobForConnectionIdEmptyBecauseOnlyReset() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, RESET_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);

      final Optional<Job> actual = jobPersistence.getLastSyncJob(CONNECTION_ID);

      assertTrue(actual.isEmpty());
    }

  }

  @Nested
  @DisplayName("When getting the last sync job for multiple connections")
  class GetLastSyncJobForConnections {

    private static final UUID CONNECTION_ID_1 = UUID.randomUUID();
    private static final UUID CONNECTION_ID_2 = UUID.randomUUID();
    private static final UUID CONNECTION_ID_3 = UUID.randomUUID();
    private static final String SCOPE_1 = CONNECTION_ID_1.toString();
    private static final String SCOPE_2 = CONNECTION_ID_2.toString();
    private static final String SCOPE_3 = CONNECTION_ID_3.toString();
    private static final List<UUID> CONNECTION_IDS = List.of(CONNECTION_ID_1, CONNECTION_ID_2, CONNECTION_ID_3);

    @Test
    @DisplayName("Should return nothing if no sync job exists")
    void testGetLastSyncJobsForConnectionsEmpty() throws IOException {
      final List<Job> actual = jobPersistence.getLastSyncJobForConnections(CONNECTION_IDS);

      assertTrue(actual.isEmpty());
    }

    @Test
    @DisplayName("Should return the last enqueued sync job for each connection")
    void testGetLastSyncJobForConnections() throws IOException {
      final long scope1Job1 = jobPersistence.enqueueJob(SCOPE_1, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(scope1Job1, jobPersistence.createAttempt(scope1Job1, LOG_PATH));

      final long scope2Job1 = jobPersistence.enqueueJob(SCOPE_2, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(scope2Job1, jobPersistence.createAttempt(scope2Job1, LOG_PATH));

      final long scope3Job1 = jobPersistence.enqueueJob(SCOPE_3, SYNC_JOB_CONFIG).orElseThrow();

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);

      final long scope1Job2 = jobPersistence.enqueueJob(SCOPE_1, SYNC_JOB_CONFIG).orElseThrow();
      final int scope1Job2AttemptNumber = jobPersistence.createAttempt(scope1Job2, LOG_PATH);

      // should return the latest sync job even if failed
      jobPersistence.failAttempt(scope1Job2, scope1Job2AttemptNumber);
      final Attempt scope1Job2attempt = jobPersistence.getJob(scope1Job2).getAttempts().stream().findFirst().orElseThrow();
      jobPersistence.failJob(scope1Job2);

      // will leave this job running
      final long scope2Job2 = jobPersistence.enqueueJob(SCOPE_2, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.createAttempt(scope2Job2, LOG_PATH);
      final Attempt scope2Job2attempt = jobPersistence.getJob(scope2Job2).getAttempts().stream().findFirst().orElseThrow();

      final List<Job> actual = jobPersistence.getLastSyncJobForConnections(CONNECTION_IDS);
      final List<Job> expected = new ArrayList<>();
      expected.add(createJob(scope1Job2, SYNC_JOB_CONFIG, JobStatus.FAILED, List.of(scope1Job2attempt), afterNow.getEpochSecond(), SCOPE_1));
      expected.add(createJob(scope2Job2, SYNC_JOB_CONFIG, JobStatus.RUNNING, List.of(scope2Job2attempt), afterNow.getEpochSecond(), SCOPE_2));
      expected.add(createJob(scope3Job1, SYNC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond(), SCOPE_3));

      assertTrue(expected.size() == actual.size() && expected.containsAll(actual) && actual.containsAll(expected));
    }

    @Test
    @DisplayName("Should return nothing if only reset job exists")
    void testGetLastSyncJobsForConnectionsEmptyBecauseOnlyReset() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE_1, RESET_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(jobId, jobPersistence.createAttempt(jobId, LOG_PATH));

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);

      final List<Job> actual = jobPersistence.getLastSyncJobForConnections(CONNECTION_IDS);

      assertTrue(actual.isEmpty());
    }

  }

  @Nested
  @DisplayName("When getting the last running sync job for multiple connections")
  class GetRunningSyncJobForConnections {

    private static final UUID CONNECTION_ID_1 = UUID.randomUUID();
    private static final UUID CONNECTION_ID_2 = UUID.randomUUID();
    private static final UUID CONNECTION_ID_3 = UUID.randomUUID();
    private static final String SCOPE_1 = CONNECTION_ID_1.toString();
    private static final String SCOPE_2 = CONNECTION_ID_2.toString();
    private static final String SCOPE_3 = CONNECTION_ID_3.toString();
    private static final List<UUID> CONNECTION_IDS = List.of(CONNECTION_ID_1, CONNECTION_ID_2, CONNECTION_ID_3);

    @Test
    @DisplayName("Should return nothing if no sync job exists")
    void testGetRunningSyncJobsForConnectionsEmpty() throws IOException {
      final List<Job> actual = jobPersistence.getRunningSyncJobForConnections(CONNECTION_IDS);

      assertTrue(actual.isEmpty());
    }

    @Test
    @DisplayName("Should return the last running sync job for each connection")
    void testGetRunningSyncJobsForConnections() throws IOException {
      // succeeded jobs should not be present in the result
      final long scope1Job1 = jobPersistence.enqueueJob(SCOPE_1, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(scope1Job1, jobPersistence.createAttempt(scope1Job1, LOG_PATH));

      // fail scope2's first job, but later start a running job that should show up in the result
      final long scope2Job1 = jobPersistence.enqueueJob(SCOPE_2, SYNC_JOB_CONFIG).orElseThrow();
      final int scope2Job1AttemptNumber = jobPersistence.createAttempt(scope2Job1, LOG_PATH);
      jobPersistence.failAttempt(scope2Job1, scope2Job1AttemptNumber);
      jobPersistence.failJob(scope2Job1);

      // pending jobs should be present in the result
      final long scope3Job1 = jobPersistence.enqueueJob(SCOPE_3, SYNC_JOB_CONFIG).orElseThrow();

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);

      // create a running job/attempt for scope2
      final long scope2Job2 = jobPersistence.enqueueJob(SCOPE_2, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.createAttempt(scope2Job2, LOG_PATH);
      final Attempt scope2Job2attempt = jobPersistence.getJob(scope2Job2).getAttempts().stream().findFirst().orElseThrow();

      final List<Job> expected = new ArrayList<>();
      expected.add(createJob(scope2Job2, SYNC_JOB_CONFIG, JobStatus.RUNNING, List.of(scope2Job2attempt), afterNow.getEpochSecond(), SCOPE_2));
      expected.add(createJob(scope3Job1, SYNC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond(), SCOPE_3));

      final List<Job> actual = jobPersistence.getRunningSyncJobForConnections(CONNECTION_IDS);
      assertTrue(expected.size() == actual.size() && expected.containsAll(actual) && actual.containsAll(expected));
    }

    @Test
    @DisplayName("Should return nothing if only a running reset job exists")
    void testGetRunningSyncJobsForConnectionsEmptyBecauseOnlyReset() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE_1, RESET_JOB_CONFIG).orElseThrow();
      jobPersistence.createAttempt(jobId, LOG_PATH);

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);

      final List<Job> actual = jobPersistence.getRunningSyncJobForConnections(CONNECTION_IDS);

      assertTrue(actual.isEmpty());
    }

  }

  @Nested
  @DisplayName("When getting first replication job")
  class GetFirstReplicationJob {

    @Test
    @DisplayName("Should return nothing if no job exists")
    void testGetFirstSyncJobForConnectionIdEmpty() throws IOException {
      final Optional<Job> actual = jobPersistence.getFirstReplicationJob(CONNECTION_ID);

      assertTrue(actual.isEmpty());
    }

    @Test
    @DisplayName("Should return the first job")
    void testGetFirstSyncJobForConnectionId() throws IOException {
      final long jobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(jobId1, jobPersistence.createAttempt(jobId1, LOG_PATH));
      final List<AttemptWithJobInfo> attemptsWithJobInfo = jobPersistence.listAttemptsWithJobInfo(SYNC_JOB_CONFIG.getConfigType(), Instant.EPOCH);
      final List<Attempt> attempts = Collections.singletonList(attemptsWithJobInfo.get(0).getAttempt());

      final Instant afterNow = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(afterNow);
      jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();

      final Optional<Job> actual = jobPersistence.getFirstReplicationJob(CONNECTION_ID);
      final Job expected = createJob(jobId1, SYNC_JOB_CONFIG, JobStatus.SUCCEEDED, attempts, NOW.getEpochSecond());

      assertEquals(Optional.of(expected), actual);
    }

  }

  @Nested
  @DisplayName("When getting next job")
  class GetNextJob {

    @Test
    @DisplayName("Should always return oldest pending job")
    void testGetOldestPendingJob() throws IOException {
      final long jobId = createJobAt(NOW);
      createJobAt(NOW.plusSeconds(1000));

      final Optional<Job> actual = jobPersistence.getNextJob();

      final Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
      assertEquals(Optional.of(expected), actual);
    }

    @Test
    @DisplayName("Should return nothing if no jobs pending")
    void testGetOldestPendingJobOnlyPendingJobs() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      jobPersistence.cancelJob(jobId);

      final Optional<Job> actual = jobPersistence.getNextJob();

      assertTrue(actual.isEmpty());
    }

    @Test
    @DisplayName("Should return job if job is pending even if it has multiple failed attempts")
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
              createAttempt(0, jobId, AttemptStatus.FAILED, LOG_PATH),
              createAttempt(1, jobId, AttemptStatus.FAILED, LOG_PATH)),
          NOW.getEpochSecond());

      assertEquals(Optional.of(expected), actual);
    }

    @Test
    @DisplayName("Should return oldest pending job even if another job with same scope failed")
    void testGetOldestPendingJobWithOtherJobWithSameScopeFailed() throws IOException {
      // create a job and set it to incomplete.
      final long jobId = createJobAt(NOW.minusSeconds(1000));
      jobPersistence.createAttempt(jobId, LOG_PATH);
      jobPersistence.failJob(jobId);

      // create a pending job.
      final long jobId2 = createJobAt(NOW);

      final Optional<Job> actual = jobPersistence.getNextJob();

      final Job expected = createJob(jobId2, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
      assertEquals(Optional.of(expected), actual);
    }

    @Test
    @DisplayName("Should return oldest pending job even if another job with same scope cancelled")
    void testGetOldestPendingJobWithOtherJobWithSameScopeCancelled() throws IOException {
      // create a job and set it to incomplete.
      final long jobId = createJobAt(NOW.minusSeconds(1000));
      jobPersistence.cancelJob(jobId);

      // create a pending job.
      final long jobId2 = createJobAt(NOW);

      final Optional<Job> actual = jobPersistence.getNextJob();

      final Job expected = createJob(jobId2, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
      assertEquals(Optional.of(expected), actual);
    }

    @Test
    @DisplayName("Should return oldest pending job even if another job with same scope succeeded")
    void testGetOldestPendingJobWithOtherJobWithSameScopeSucceeded() throws IOException {
      // create a job and set it to incomplete.
      final long jobId = createJobAt(NOW.minusSeconds(1000));
      final int attemptNumber = jobPersistence.createAttempt(jobId, LOG_PATH);
      jobPersistence.succeedAttempt(jobId, attemptNumber);

      // create a pending job.
      final long jobId2 = createJobAt(NOW);

      final Optional<Job> actual = jobPersistence.getNextJob();

      final Job expected = createJob(jobId2, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());
      assertEquals(Optional.of(expected), actual);
    }

    @Test
    @DisplayName("Should not return pending job if job with same scope is running")
    void testGetOldestPendingJobWithOtherJobWithSameScopeRunning() throws IOException {
      // create a job and set it to running.
      final long jobId = createJobAt(NOW.minusSeconds(1000));
      jobPersistence.createAttempt(jobId, LOG_PATH);

      // create a pending job.
      createJobAt(NOW);

      final Optional<Job> actual = jobPersistence.getNextJob();

      assertTrue(actual.isEmpty());
    }

    @Test
    @DisplayName("Should not return pending job if job with same scope is incomplete")
    void testGetOldestPendingJobWithOtherJobWithSameScopeIncomplete() throws IOException {
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

  }

  @Nested
  @DisplayName("When getting the count of jobs")
  class GetJobCount {

    @Test
    @DisplayName("Should return the total job count for the connection")
    void testGetJobCount() throws IOException {
      final int numJobsToCreate = 10;
      for (int i = 0; i < numJobsToCreate; i++) {
        jobPersistence.enqueueJob(CONNECTION_ID.toString(), SPEC_JOB_CONFIG);
      }

      final Long actualJobCount = jobPersistence.getJobCount(Set.of(SPEC_JOB_CONFIG.getConfigType()), CONNECTION_ID.toString());

      assertEquals(numJobsToCreate, actualJobCount);
    }

    @Test
    @DisplayName("Should return 0 if there are no jobs for this connection")
    void testGetJobCountNoneForConnection() throws IOException {
      final UUID otherConnectionId1 = UUID.randomUUID();
      final UUID otherConnectionId2 = UUID.randomUUID();

      jobPersistence.enqueueJob(otherConnectionId1.toString(), SPEC_JOB_CONFIG);
      jobPersistence.enqueueJob(otherConnectionId2.toString(), SPEC_JOB_CONFIG);

      final Long actualJobCount = jobPersistence.getJobCount(Set.of(SPEC_JOB_CONFIG.getConfigType()), CONNECTION_ID.toString());

      assertEquals(0, actualJobCount);
    }

  }

  @Nested
  @DisplayName("When listing jobs, use paged results")
  class ListJobs {

    @Test
    @DisplayName("Should return the correct page of results with multiple pages of history")
    void testListJobsByPage() throws IOException {
      final List<Long> ids = new ArrayList<Long>();
      for (int i = 0; i < 50; i++) {
        final long jobId = jobPersistence.enqueueJob(CONNECTION_ID.toString(), SPEC_JOB_CONFIG).orElseThrow();
        ids.add(jobId);

        // create two attempts per job to verify pagination is applied at the job record level
        final int attemptNum1 = jobPersistence.createAttempt(jobId, LOG_PATH);
        jobPersistence.failAttempt(jobId, attemptNum1);
        jobPersistence.createAttempt(jobId, LOG_PATH);

        // also create a job for another connection, to verify the query is properly filtering down to only
        // jobs for the desired connection
        jobPersistence.enqueueJob(CONNECTION_ID2.toString(), SPEC_JOB_CONFIG).orElseThrow();
      }
      final int pagesize = 10;
      final int offset = 3;

      final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString(), pagesize, offset);
      assertEquals(pagesize, actualList.size());
      assertEquals(ids.get(ids.size() - 1 - offset), actualList.get(0).getId());
    }

    @Test
    @DisplayName("Should return the results in the correct sort order")
    void testListJobsSortsDescending() throws IOException {
      final List<Long> ids = new ArrayList<Long>();
      for (int i = 0; i < 100; i++) {
        // These have strictly the same created_at due to the setup() above, so should come back sorted by
        // id desc instead.
        final long jobId = jobPersistence.enqueueJob(CONNECTION_ID.toString(), SPEC_JOB_CONFIG).orElseThrow();
        ids.add(jobId);
      }
      final int pagesize = 200;
      final int offset = 0;
      final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString(), pagesize, offset);
      for (int i = 0; i < 100; i++) {
        assertEquals(ids.get(ids.size() - (i + 1)), actualList.get(i).getId(), "Job ids should have been in order but weren't.");
      }
    }

    @Test
    @DisplayName("Should list all jobs")
    void testListJobs() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

      final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString(), 9999, 0);

      final Job actual = actualList.get(0);
      final Job expected = createJob(jobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond());

      assertEquals(1, actualList.size());
      assertEquals(expected, actual);
    }

    @Test
    @DisplayName("Should list all jobs matching multiple config types")
    void testListJobsMultipleConfigTypes() throws IOException {
      final long specJobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final long checkJobId = jobPersistence.enqueueJob(SCOPE, CHECK_JOB_CONFIG).orElseThrow();
      // add a third config type that is not added in the listJobs request, to verify that it is not
      // included in the results
      jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();

      final List<Job> actualList =
          jobPersistence.listJobs(Set.of(SPEC_JOB_CONFIG.getConfigType(), CHECK_JOB_CONFIG.getConfigType()), CONNECTION_ID.toString(), 9999, 0);

      final List<Job> expectedList =
          List.of(createJob(checkJobId, CHECK_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond()),
              createJob(specJobId, SPEC_JOB_CONFIG, JobStatus.PENDING, Collections.emptyList(), NOW.getEpochSecond()));

      assertEquals(expectedList, actualList);
    }

    @Test
    @DisplayName("Should list all jobs with all attempts")
    void testListJobsWithMultipleAttempts() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber0 = jobPersistence.createAttempt(jobId, LOG_PATH);

      jobPersistence.failAttempt(jobId, attemptNumber0);

      final Path secondAttemptLogPath = LOG_PATH.resolve("2");
      final int attemptNumber1 = jobPersistence.createAttempt(jobId, secondAttemptLogPath);

      jobPersistence.succeedAttempt(jobId, attemptNumber1);

      final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString(), 9999, 0);

      final Job actual = actualList.get(0);
      final Job expected = createJob(
          jobId,
          SPEC_JOB_CONFIG,
          JobStatus.SUCCEEDED,
          Lists.newArrayList(
              createAttempt(0, jobId, AttemptStatus.FAILED, LOG_PATH),
              createAttempt(1, jobId, AttemptStatus.SUCCEEDED, secondAttemptLogPath)),
          NOW.getEpochSecond());

      assertEquals(1, actualList.size());
      assertEquals(expected, actual);
    }

    @Test
    @DisplayName("Should list all jobs with all attempts in descending order")
    void testListJobsWithMultipleAttemptsInDescOrder() throws IOException {
      // create first job with multiple attempts
      final var jobId1 = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final var job1Attempt1 = jobPersistence.createAttempt(jobId1, LOG_PATH);
      jobPersistence.failAttempt(jobId1, job1Attempt1);
      final var job1Attempt2LogPath = LOG_PATH.resolve("2");
      final int job1Attempt2 = jobPersistence.createAttempt(jobId1, job1Attempt2LogPath);
      jobPersistence.succeedAttempt(jobId1, job1Attempt2);

      // create second job with multiple attempts
      final var laterTime = NOW.plusSeconds(1000);
      when(timeSupplier.get()).thenReturn(laterTime);
      final var jobId2 = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final var job2Attempt1LogPath = LOG_PATH.resolve("3");
      final var job2Attempt1 = jobPersistence.createAttempt(jobId2, job2Attempt1LogPath);
      jobPersistence.succeedAttempt(jobId2, job2Attempt1);

      final List<Job> actualList = jobPersistence.listJobs(SPEC_JOB_CONFIG.getConfigType(), CONNECTION_ID.toString(), 9999, 0);

      assertEquals(2, actualList.size());
      assertEquals(jobId2, actualList.get(0).getId());
    }

    @Test
    @DisplayName("Should list jobs including the specified job")
    void testListJobsIncludingId() throws IOException {
      final List<Long> ids = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        // This makes each enqueued job have an increasingly higher createdAt time
        when(timeSupplier.get()).thenReturn(Instant.ofEpochSecond(i));
        // Alternate between spec and check job config types to verify that both config types are fetched
        // properly
        final JobConfig jobConfig = i % 2 == 0 ? SPEC_JOB_CONFIG : CHECK_JOB_CONFIG;
        final long jobId = jobPersistence.enqueueJob(CONNECTION_ID.toString(), jobConfig).orElseThrow();
        ids.add(jobId);
        // also create an attempt for each job to verify that joining with attempts does not cause failures
        jobPersistence.createAttempt(jobId, LOG_PATH);
      }

      final int includingIdIndex = 90;
      final int pageSize = 25;
      final List<Job> actualList = jobPersistence.listJobsIncludingId(Set.of(SPEC_JOB_CONFIG.getConfigType(), CHECK_JOB_CONFIG.getConfigType()),
          CONNECTION_ID.toString(), ids.get(includingIdIndex), pageSize);
      final List<Long> expectedJobIds = Lists.reverse(ids.subList(ids.size() - pageSize, ids.size()));
      assertEquals(expectedJobIds, actualList.stream().map(Job::getId).toList());
    }

    @Test
    @DisplayName("Should list jobs including the specified job, including multiple pages if necessary")
    void testListJobsIncludingIdMultiplePages() throws IOException {
      final List<Long> ids = new ArrayList<>();
      for (int i = 0; i < 100; i++) {
        // This makes each enqueued job have an increasingly higher createdAt time
        when(timeSupplier.get()).thenReturn(Instant.ofEpochSecond(i));
        // Alternate between spec and check job config types to verify that both config types are fetched
        // properly
        final JobConfig jobConfig = i % 2 == 0 ? SPEC_JOB_CONFIG : CHECK_JOB_CONFIG;
        final long jobId = jobPersistence.enqueueJob(CONNECTION_ID.toString(), jobConfig).orElseThrow();
        ids.add(jobId);
        // also create an attempt for each job to verify that joining with attempts does not cause failures
        jobPersistence.createAttempt(jobId, LOG_PATH);
      }

      // including id is on the second page, so response should contain two pages of jobs
      final int includingIdIndex = 60;
      final int pageSize = 25;
      final List<Job> actualList = jobPersistence.listJobsIncludingId(Set.of(SPEC_JOB_CONFIG.getConfigType(), CHECK_JOB_CONFIG.getConfigType()),
          CONNECTION_ID.toString(), ids.get(includingIdIndex), pageSize);
      final List<Long> expectedJobIds = Lists.reverse(ids.subList(ids.size() - (pageSize * 2), ids.size()));
      assertEquals(expectedJobIds, actualList.stream().map(Job::getId).toList());
    }

    @Test
    @DisplayName("Should return an empty list if there is no job with the includingJob ID for this connection")
    void testListJobsIncludingIdFromWrongConnection() throws IOException {
      for (int i = 0; i < 10; i++) {
        jobPersistence.enqueueJob(CONNECTION_ID.toString(), SPEC_JOB_CONFIG);
      }

      final long otherConnectionJobId = jobPersistence.enqueueJob(UUID.randomUUID().toString(), SPEC_JOB_CONFIG).orElseThrow();

      final List<Job> actualList =
          jobPersistence.listJobsIncludingId(Set.of(SPEC_JOB_CONFIG.getConfigType()), CONNECTION_ID.toString(), otherConnectionJobId, 25);
      assertEquals(List.of(), actualList);
    }

  }

  @Nested
  @DisplayName("When listing job with status")
  class ListJobsWithStatus {

    @Test
    @DisplayName("Should only list jobs with requested status")
    void testListJobsWithStatus() throws IOException {
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
              createAttempt(0, jobId, AttemptStatus.FAILED, LOG_PATH)),
          NOW.getEpochSecond());

      assertEquals(1, actualList.size());
      assertEquals(expected, actual);
    }

    @Test
    @DisplayName("Should only list jobs with requested status and config type")
    void testListJobsWithStatusAndConfigType() throws IOException, InterruptedException {
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
              createAttempt(0, failedSpecJobId, AttemptStatus.FAILED, LOG_PATH)),
          NOW.getEpochSecond(),
          SPEC_SCOPE);

      assertEquals(Sets.newHashSet(expectedPendingCheckJob, expectedPendingSpecJob, expectedPendingSyncJob), Sets.newHashSet(allPendingJobs));
      assertEquals(Sets.newHashSet(expectedPendingSpecJob, expectedPendingSyncJob), Sets.newHashSet(allPendingSyncAndSpecJobs));

      assertEquals(1, incompleteJobs.size());
      assertEquals(expectedIncompleteJob, actualIncompleteJob);
    }

    @Test
    @DisplayName("Should only list jobs for the requested connection and with the requested statuses and config types")
    void testListJobsWithStatusesAndConfigTypesForConnection() throws IOException, InterruptedException {
      final UUID desiredConnectionId = UUID.randomUUID();
      final UUID otherConnectionId = UUID.randomUUID();

      // desired connection, statuses, and config types
      final long desiredJobId1 = jobPersistence.enqueueJob(desiredConnectionId.toString(), SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(desiredJobId1, jobPersistence.createAttempt(desiredJobId1, LOG_PATH));
      final long desiredJobId2 = jobPersistence.enqueueJob(desiredConnectionId.toString(), SYNC_JOB_CONFIG).orElseThrow();
      final long desiredJobId3 = jobPersistence.enqueueJob(desiredConnectionId.toString(), CHECK_JOB_CONFIG).orElseThrow();
      jobPersistence.succeedAttempt(desiredJobId3, jobPersistence.createAttempt(desiredJobId3, LOG_PATH));
      final long desiredJobId4 = jobPersistence.enqueueJob(desiredConnectionId.toString(), CHECK_JOB_CONFIG).orElseThrow();

      // right connection id and status, wrong config type
      jobPersistence.enqueueJob(desiredConnectionId.toString(), SPEC_JOB_CONFIG).orElseThrow();
      // right config type and status, wrong connection id
      jobPersistence.enqueueJob(otherConnectionId.toString(), SYNC_JOB_CONFIG).orElseThrow();
      // right connection id and config type, wrong status
      final long otherJobId3 = jobPersistence.enqueueJob(desiredConnectionId.toString(), CHECK_JOB_CONFIG).orElseThrow();
      jobPersistence.failAttempt(otherJobId3, jobPersistence.createAttempt(otherJobId3, LOG_PATH));

      final List<Job> actualJobs = jobPersistence.listJobsForConnectionWithStatuses(desiredConnectionId,
          Set.of(ConfigType.SYNC, ConfigType.CHECK_CONNECTION_DESTINATION), Set.of(JobStatus.PENDING, JobStatus.SUCCEEDED));

      final Job expectedDesiredJob1 = createJob(desiredJobId1, SYNC_JOB_CONFIG, JobStatus.SUCCEEDED,
          Lists.newArrayList(createAttempt(0, desiredJobId1, AttemptStatus.SUCCEEDED, LOG_PATH)),
          NOW.getEpochSecond(), desiredConnectionId.toString());
      final Job expectedDesiredJob2 =
          createJob(desiredJobId2, SYNC_JOB_CONFIG, JobStatus.PENDING, Lists.newArrayList(), NOW.getEpochSecond(), desiredConnectionId.toString());
      final Job expectedDesiredJob3 = createJob(desiredJobId3, CHECK_JOB_CONFIG, JobStatus.SUCCEEDED,
          Lists.newArrayList(createAttempt(0, desiredJobId3, AttemptStatus.SUCCEEDED, LOG_PATH)),
          NOW.getEpochSecond(), desiredConnectionId.toString());
      final Job expectedDesiredJob4 =
          createJob(desiredJobId4, CHECK_JOB_CONFIG, JobStatus.PENDING, Lists.newArrayList(), NOW.getEpochSecond(), desiredConnectionId.toString());

      assertEquals(Sets.newHashSet(expectedDesiredJob1, expectedDesiredJob2, expectedDesiredJob3, expectedDesiredJob4), Sets.newHashSet(actualJobs));
    }

  }

  @Nested
  @DisplayName("When resetting job")
  class ResetJob {

    @Test
    @DisplayName("Should reset job and put job in pending state")
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
    @DisplayName("Should not be able to reset a cancelled job")
    void testResetJobCancelled() throws IOException {
      final long jobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();

      jobPersistence.cancelJob(jobId);
      assertDoesNotThrow(() -> jobPersistence.resetJob(jobId));

      final Job updated = jobPersistence.getJob(jobId);
      assertEquals(JobStatus.CANCELLED, updated.getStatus());
    }

  }

  @Nested
  @DisplayName("When purging job history")
  class PurgeJobHistory {

    private Job persistJobForJobHistoryTesting(final String scope, final JobConfig jobConfig, final JobStatus status, final LocalDateTime runDate)
        throws IOException, SQLException {
      final Optional<Long> id = jobDatabase.query(
          ctx -> ctx.fetch(
              "INSERT INTO jobs(config_type, scope, created_at, updated_at, status, config) " +
                  "SELECT CAST(? AS JOB_CONFIG_TYPE), ?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB) " +
                  "RETURNING id ",
              Sqls.toSqlName(jobConfig.getConfigType()),
              scope,
              runDate,
              runDate,
              Sqls.toSqlName(status),
              Jsons.serialize(jobConfig)))
          .stream()
          .findFirst()
          .map(r -> r.getValue("id", Long.class));
      return jobPersistence.getJob(id.get());
    }

    private void persistAttemptForJobHistoryTesting(final Job job, final String logPath, final LocalDateTime runDate, final boolean shouldHaveState)
        throws IOException, SQLException {
      final String attemptOutputWithState = "{\n"
          + "  \"sync\": {\n"
          + "    \"state\": {\n"
          + "      \"state\": {\n"
          + "        \"bookmarks\": {"
          + "}}}}}";
      final String attemptOutputWithoutState = "{\n"
          + "  \"sync\": {\n"
          + "    \"output_catalog\": {"
          + "}}}";
      jobDatabase.query(ctx -> ctx.fetch(
          "INSERT INTO attempts(job_id, attempt_number, log_path, status, created_at, updated_at, output) "
              + "VALUES(?, ?, ?, CAST(? AS ATTEMPT_STATUS), ?, ?, CAST(? as JSONB)) RETURNING attempt_number",
          job.getId(),
          job.getAttemptsCount(),
          logPath,
          Sqls.toSqlName(AttemptStatus.FAILED),
          runDate,
          runDate,
          shouldHaveState ? attemptOutputWithState : attemptOutputWithoutState)
          .stream()
          .findFirst()
          .map(r -> r.get("attempt_number", Integer.class))
          .orElseThrow(() -> new RuntimeException("This should not happen")));
    }

    /**
     * Testing job history deletion is sensitive to exactly how the constants are configured for
     * controlling deletion logic. Thus, the test case injects overrides for those constants, testing a
     * comprehensive set of combinations to make sure that the logic is robust to reasonable
     * configurations. Extreme configurations such as zero-day retention period are not covered.
     *
     * Business rules for deletions. 1. Job must be older than X days or its conn has excessive number
     * of jobs 2. Job cannot be one of the last N jobs on that conn (last N jobs are always kept). 3.
     * Job cannot be holding the most recent saved state (most recent saved state is always kept).
     *
     * Testing Goal: Set up jobs according to the parameters passed in. Then delete according to the
     * rules, and make sure the right number of jobs are left. Against one connection/scope,
     * <ol>
     * <li>Setup: create a history of jobs that goes back many days (but produces no more than one job a
     * day)</li>
     * <li>Setup: the most recent job with state in it should be at least N jobs back</li>
     * <li>Assert: ensure that after purging, there are the right number of jobs left (and at least min
     * recency), including the one with the most recent state.</li>
     * <li>Assert: ensure that after purging, there are the right number of jobs left (and at least min
     * recency), including the X most recent</li>
     * <li>Assert: ensure that after purging, all other job history has been deleted.</li>
     * </ol>
     *
     * @param numJobs How many test jobs to generate; make this enough that all other parameters are
     *        fully included, for predictable results.
     * @param tooManyJobs Takes the place of DefaultJobPersistence.JOB_HISTORY_EXCESSIVE_NUMBER_OF_JOBS
     *        - how many jobs are needed before it ignores date-based age of job when doing deletions.
     * @param ageCutoff Takes the place of DefaultJobPersistence.JOB_HISTORY_MINIMUM_AGE_IN_DAYS -
     *        retention period in days for the most recent jobs; older than this gets deleted.
     * @param recencyCutoff Takes the place of DefaultJobPersistence.JOB_HISTORY_MINIMUM_RECENCY -
     *        retention period in number of jobs; at least this many jobs will be retained after
     *        deletion (provided enough existed in the first place).
     * @param lastStatePosition How far back in the list is the job with the latest saved state. This
     *        can be manipulated to have the saved-state job inside or prior to the retention period.
     * @param expectedAfterPurge How many matching jobs are expected after deletion, given the input
     *        parameters. This was calculated by a human based on understanding the requirements.
     * @param goalOfTestScenario Description of the purpose of that test scenario, so it's easier to
     *        maintain and understand failures.
     *
     */
    @DisplayName("Should purge older job history but maintain certain more recent ones")
    @ParameterizedTest
    // Cols: numJobs, tooManyJobsCutoff, ageCutoff, recencyCutoff, lastSavedStatePosition,
    // expectedAfterPurge, description
    @CsvSource({
      "50,100,10,5,9,10,'Validate age cutoff alone'",
      "50,100,10,5,13,11,'Validate saved state after age cutoff'",
      "50,100,10,15,9,15,'Validate recency cutoff alone'",
      "50,100,10,15,17,16,'Validate saved state after recency cutoff'",
      "50,20,30,10,9,10,'Validate excess jobs cutoff alone'",
      "50,20,30,10,25,11,'Validate saved state after excess jobs cutoff'",
      "50,20,30,20,9,20,'Validate recency cutoff with excess jobs cutoff'",
      "50,20,30,20,25,21,'Validate saved state after recency and excess jobs cutoff but before age'",
      "50,20,30,20,35,21,'Validate saved state after recency and excess jobs cutoff and after age'"
    })
    void testPurgeJobHistory(final int numJobs,
                             final int tooManyJobs,
                             final int ageCutoff,
                             final int recencyCutoff,
                             final int lastStatePosition,
                             final int expectedAfterPurge,
                             final String goalOfTestScenario)
        throws IOException, SQLException {
      final String CURRENT_SCOPE = UUID.randomUUID().toString();

      // Decoys - these jobs will help mess up bad sql queries, even though they shouldn't be deleted.
      final String DECOY_SCOPE = UUID.randomUUID().toString();

      // Reconfigure constants to test various combinations of tuning knobs and make sure all work.
      final DefaultJobPersistence jobPersistence =
          new DefaultJobPersistence(jobDatabase, timeSupplier, ageCutoff, tooManyJobs, recencyCutoff);

      final LocalDateTime fakeNow = LocalDateTime.of(2021, 6, 20, 0, 0);

      // Jobs are created in reverse chronological order; id order is the inverse of old-to-new date
      // order.
      // The most-recent job is in allJobs[0] which means keeping the 10 most recent is [0-9], simplifying
      // testing math as we don't have to care how many jobs total existed and were deleted.
      final List<Job> allJobs = new ArrayList<>();
      final List<Job> decoyJobs = new ArrayList<>();
      for (int i = 0; i < numJobs; i++) {
        allJobs.add(persistJobForJobHistoryTesting(CURRENT_SCOPE, SYNC_JOB_CONFIG, JobStatus.FAILED, fakeNow.minusDays(i)));
        decoyJobs.add(persistJobForJobHistoryTesting(DECOY_SCOPE, SYNC_JOB_CONFIG, JobStatus.FAILED, fakeNow.minusDays(i)));
      }

      // At least one job should have state. Find the desired job and add state to it.
      final Job lastJobWithState = addStateToJob(allJobs.get(lastStatePosition));
      addStateToJob(decoyJobs.get(lastStatePosition - 1));
      addStateToJob(decoyJobs.get(lastStatePosition + 1));

      // An older job with state should also exist, so we ensure we picked the most-recent with queries.
      addStateToJob(allJobs.get(lastStatePosition + 1));

      // sanity check that the attempt does have saved state so the purge history sql detects it correctly
      assertTrue(lastJobWithState.getAttempts().get(0).getOutput() != null,
          goalOfTestScenario + " - missing saved state on job that was supposed to have it.");

      // Execute the job history purge and check what jobs are left.
      ((DefaultJobPersistence) jobPersistence).purgeJobHistory(fakeNow);
      final List<Job> afterPurge = jobPersistence.listJobs(ConfigType.SYNC, CURRENT_SCOPE, 9999, 0);

      // Test - contains expected number of jobs and no more than that
      assertEquals(expectedAfterPurge, afterPurge.size(), goalOfTestScenario + " - Incorrect number of jobs remain after deletion.");

      // Test - most-recent are actually the most recent by date (see above, reverse order)
      for (int i = 0; i < Math.min(ageCutoff, recencyCutoff); i++) {
        assertEquals(allJobs.get(i).getId(), afterPurge.get(i).getId(), goalOfTestScenario + " - Incorrect sort order after deletion.");
      }

      // Test - job with latest state is always kept despite being older than some cutoffs
      assertTrue(afterPurge.contains(lastJobWithState), goalOfTestScenario + " - Missing last job with saved state after deletion.");
    }

    private Job addStateToJob(final Job job) throws IOException, SQLException {
      persistAttemptForJobHistoryTesting(job, LOG_PATH.toString(),
          LocalDateTime.ofEpochSecond(job.getCreatedAtInSecond(), 0, ZoneOffset.UTC), true);
      return jobPersistence.getJob(job.getId()); // reload job to include its attempts
    }

  }

  @Nested
  @DisplayName("When listing job statuses and timestamps with specified connection id and timestamp")
  class ListJobStatusAndTimestampWithConnection {

    @Test
    @DisplayName("Should list only job statuses and timestamps of specified connection id")
    void testConnectionIdFiltering() throws IOException {
      jobPersistence = new DefaultJobPersistence(jobDatabase, timeSupplier, DEFAULT_MINIMUM_AGE_IN_DAYS, DEFAULT_EXCESSIVE_NUMBER_OF_JOBS,
          DEFAULT_MINIMUM_RECENCY_COUNT);

      // create a connection with a non-relevant connection id that should be ignored for the duration of
      // the test
      final long wrongConnectionSyncJobId = jobPersistence.enqueueJob(UUID.randomUUID().toString(), SYNC_JOB_CONFIG).orElseThrow();
      final int wrongSyncJobAttemptNumber0 = jobPersistence.createAttempt(wrongConnectionSyncJobId, LOG_PATH);
      jobPersistence.failAttempt(wrongConnectionSyncJobId, wrongSyncJobAttemptNumber0);
      assertEquals(0, jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, Sets.newHashSet(ConfigType.SYNC), Instant.EPOCH).size());

      // create a connection with relevant connection id
      final long syncJobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      final int syncJobAttemptNumber0 = jobPersistence.createAttempt(syncJobId, LOG_PATH);
      jobPersistence.failAttempt(syncJobId, syncJobAttemptNumber0);

      // check to see current status of only relevantly scoped job
      final List<JobWithStatusAndTimestamp> jobs =
          jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, Sets.newHashSet(ConfigType.SYNC), Instant.EPOCH);
      assertEquals(jobs.size(), 1);
      assertEquals(JobStatus.INCOMPLETE, jobs.get(0).getStatus());
    }

    @Test
    @DisplayName("Should list jobs statuses filtered by different timestamps")
    void testTimestampFiltering() throws IOException {
      jobPersistence = new DefaultJobPersistence(jobDatabase, timeSupplier, DEFAULT_MINIMUM_AGE_IN_DAYS, DEFAULT_EXCESSIVE_NUMBER_OF_JOBS,
          DEFAULT_MINIMUM_RECENCY_COUNT);

      // Create and fail initial job
      final long syncJobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      final int syncJobAttemptNumber0 = jobPersistence.createAttempt(syncJobId, LOG_PATH);
      jobPersistence.failAttempt(syncJobId, syncJobAttemptNumber0);
      jobPersistence.failJob(syncJobId);

      // Check to see current status of all jobs from beginning of time, expecting only 1 job
      final List<JobWithStatusAndTimestamp> initialJobs =
          jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, Sets.newHashSet(ConfigType.SYNC), Instant.EPOCH);
      assertEquals(initialJobs.size(), 1);
      assertEquals(JobStatus.FAILED, initialJobs.get(0).getStatus());

      // Edit time supplier to return later time
      final Instant timeAfterFirstJob = NOW.plusSeconds(60);
      when(timeSupplier.get()).thenReturn(timeAfterFirstJob);

      // Create and succeed second job
      final long newSyncJobId = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      final int newSyncJobAttemptNumber = jobPersistence.createAttempt(newSyncJobId, LOG_PATH);
      jobPersistence.succeedAttempt(newSyncJobId, newSyncJobAttemptNumber);

      // Check to see current status of all jobs from beginning of time, expecting both jobs in createAt
      // descending order (most recent first)
      final List<JobWithStatusAndTimestamp> allQueryJobs =
          jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, Sets.newHashSet(ConfigType.SYNC), Instant.EPOCH);
      assertEquals(2, allQueryJobs.size());
      assertEquals(JobStatus.SUCCEEDED, allQueryJobs.get(0).getStatus());
      assertEquals(JobStatus.FAILED, allQueryJobs.get(1).getStatus());

      // Look up jobs with a timestamp after the first job. Expecting only the second job status
      final List<JobWithStatusAndTimestamp> timestampFilteredJobs =
          jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, Sets.newHashSet(ConfigType.SYNC), timeAfterFirstJob);
      assertEquals(1, timestampFilteredJobs.size());
      assertEquals(JobStatus.SUCCEEDED, timestampFilteredJobs.get(0).getStatus());
      // TODO: issues will be fixed in scope of https://github.com/airbytehq/airbyte/issues/13192
      // assertTrue(timeAfterFirstJob.getEpochSecond() <=
      // timestampFilteredJobs.get(0).getCreatedAtInSecond());
      // assertTrue(timeAfterFirstJob.getEpochSecond() <=
      // timestampFilteredJobs.get(0).getUpdatedAtInSecond());

      // Check to see if timestamp filtering is working by only looking up jobs with timestamp after
      // second job. Expecting no job status output
      final Instant timeAfterSecondJob = timeAfterFirstJob.plusSeconds(60);
      assertEquals(0,
          jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, Sets.newHashSet(ConfigType.SYNC), timeAfterSecondJob).size());
    }

    @Test
    @DisplayName("Should list jobs statuses of differing status types")
    void testMultipleJobStatusTypes() throws IOException {
      final Supplier<Instant> timeSupplier = incrementingSecondSupplier(NOW);
      jobPersistence = new DefaultJobPersistence(jobDatabase, timeSupplier, DEFAULT_MINIMUM_AGE_IN_DAYS, DEFAULT_EXCESSIVE_NUMBER_OF_JOBS,
          DEFAULT_MINIMUM_RECENCY_COUNT);

      // Create and fail initial job
      final long syncJobId1 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      final int syncJobAttemptNumber1 = jobPersistence.createAttempt(syncJobId1, LOG_PATH);
      jobPersistence.failAttempt(syncJobId1, syncJobAttemptNumber1);
      jobPersistence.failJob(syncJobId1);

      // Create and succeed second job
      final long syncJobId2 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      final int syncJobAttemptNumber2 = jobPersistence.createAttempt(syncJobId2, LOG_PATH);
      jobPersistence.succeedAttempt(syncJobId2, syncJobAttemptNumber2);

      // Create and cancel third job
      final long syncJobId3 = jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();
      jobPersistence.createAttempt(syncJobId3, LOG_PATH);
      jobPersistence.cancelJob(syncJobId3);

      // Check to see current status of all jobs from beginning of time, expecting all jobs in createAt
      // descending order (most recent first)
      final List<JobWithStatusAndTimestamp> allJobs =
          jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, Sets.newHashSet(ConfigType.SYNC), Instant.EPOCH);
      assertEquals(3, allJobs.size());
      assertEquals(JobStatus.CANCELLED, allJobs.get(0).getStatus());
      assertEquals(JobStatus.SUCCEEDED, allJobs.get(1).getStatus());
      assertEquals(JobStatus.FAILED, allJobs.get(2).getStatus());
    }

    @Test
    @DisplayName("Should list jobs statuses of differing job config types")
    void testMultipleConfigTypes() throws IOException {
      final Set<ConfigType> configTypes = Sets.newHashSet(ConfigType.GET_SPEC, ConfigType.CHECK_CONNECTION_DESTINATION);
      final Supplier<Instant> timeSupplier = incrementingSecondSupplier(NOW);
      jobPersistence = new DefaultJobPersistence(jobDatabase, timeSupplier, DEFAULT_MINIMUM_AGE_IN_DAYS, DEFAULT_EXCESSIVE_NUMBER_OF_JOBS,
          DEFAULT_MINIMUM_RECENCY_COUNT);

      // pending status
      final long failedSpecJobId = jobPersistence.enqueueJob(SCOPE, CHECK_JOB_CONFIG).orElseThrow();
      jobPersistence.failJob(failedSpecJobId);

      // incomplete status
      final long incompleteSpecJobId = jobPersistence.enqueueJob(SCOPE, SPEC_JOB_CONFIG).orElseThrow();
      final int attemptNumber = jobPersistence.createAttempt(incompleteSpecJobId, LOG_PATH);
      jobPersistence.failAttempt(incompleteSpecJobId, attemptNumber);

      // this job should be ignored since it's not in the configTypes we're querying for
      jobPersistence.enqueueJob(SCOPE, SYNC_JOB_CONFIG).orElseThrow();

      // expect order to be from most recent to least recent
      final List<JobWithStatusAndTimestamp> allJobs =
          jobPersistence.listJobStatusAndTimestampWithConnection(CONNECTION_ID, configTypes, Instant.EPOCH);
      assertEquals(2, allJobs.size());
      assertEquals(JobStatus.INCOMPLETE, allJobs.get(0).getStatus());
      assertEquals(JobStatus.FAILED, allJobs.get(1).getStatus());
    }

  }

}
