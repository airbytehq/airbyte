/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableList;
import io.airbyte.api.model.generated.AttemptInfoRead;
import io.airbyte.api.model.generated.AttemptNormalizationStatusRead;
import io.airbyte.api.model.generated.AttemptNormalizationStatusReadList;
import io.airbyte.api.model.generated.AttemptRead;
import io.airbyte.api.model.generated.AttemptStreamStats;
import io.airbyte.api.model.generated.ConnectionRead;
import io.airbyte.api.model.generated.DestinationIdRequestBody;
import io.airbyte.api.model.generated.DestinationRead;
import io.airbyte.api.model.generated.JobConfigType;
import io.airbyte.api.model.generated.JobDebugInfoRead;
import io.airbyte.api.model.generated.JobDebugRead;
import io.airbyte.api.model.generated.JobIdRequestBody;
import io.airbyte.api.model.generated.JobInfoLightRead;
import io.airbyte.api.model.generated.JobInfoRead;
import io.airbyte.api.model.generated.JobListRequestBody;
import io.airbyte.api.model.generated.JobRead;
import io.airbyte.api.model.generated.JobReadList;
import io.airbyte.api.model.generated.JobWithAttemptsRead;
import io.airbyte.api.model.generated.LogRead;
import io.airbyte.api.model.generated.Pagination;
import io.airbyte.api.model.generated.SourceIdRequestBody;
import io.airbyte.api.model.generated.SourceRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.server.converters.JobConverter;
import io.airbyte.commons.server.helpers.ConnectionHelpers;
import io.airbyte.commons.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.commons.server.helpers.DestinationHelpers;
import io.airbyte.commons.server.helpers.SourceDefinitionHelpers;
import io.airbyte.commons.server.helpers.SourceHelpers;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StreamSyncStats;
import io.airbyte.config.SyncStats;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.JobPersistence.AttemptStats;
import io.airbyte.persistence.job.JobPersistence.JobAttemptPair;
import io.airbyte.persistence.job.models.Attempt;
import io.airbyte.persistence.job.models.AttemptNormalizationStatus;
import io.airbyte.persistence.job.models.AttemptStatus;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobStatus;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

@DisplayName("Job History Handler")
class JobHistoryHandlerTest {

  private static final long JOB_ID = 100L;
  private static final int ATTEMPT_NUMBER = 0;
  private static final String JOB_CONFIG_ID = "ef296385-6796-413f-ac1b-49c4caba3f2b";
  private static final JobStatus JOB_STATUS = JobStatus.SUCCEEDED;
  private static final JobConfig.ConfigType CONFIG_TYPE = JobConfig.ConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfigType CONFIG_TYPE_FOR_API = JobConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfig JOB_CONFIG = new JobConfig()
      .withConfigType(CONFIG_TYPE)
      .withCheckConnection(new JobCheckConnectionConfig());
  private static final Path LOG_PATH = Path.of("log_path");
  private static final LogRead EMPTY_LOG_READ = new LogRead().logLines(new ArrayList<>());
  private static final long CREATED_AT = System.currentTimeMillis() / 1000;

  private static final AttemptStats ATTEMPT_STATS = new AttemptStats(new SyncStats().withBytesEmitted(10L).withRecordsEmitted(10L),
      List.of(
          new StreamSyncStats().withStreamNamespace("ns1").withStreamName("stream1")
              .withStats(new SyncStats().withRecordsEmitted(5L).withBytesEmitted(5L)),
          new StreamSyncStats().withStreamName("stream2")
              .withStats(new SyncStats().withRecordsEmitted(5L).withBytesEmitted(5L))));

  private static final io.airbyte.api.model.generated.AttemptStats ATTEMPT_STATS_API = new io.airbyte.api.model.generated.AttemptStats()
      .bytesEmitted(10L).recordsEmitted(10L);

  private static final List<AttemptStreamStats> ATTEMPT_STREAM_STATS = List.of(
      new AttemptStreamStats().streamNamespace("ns1").streamName("stream1")
          .stats(new io.airbyte.api.model.generated.AttemptStats().recordsEmitted(5L).bytesEmitted(5L)),
      new AttemptStreamStats().streamName("stream2").stats(new io.airbyte.api.model.generated.AttemptStats().recordsEmitted(5L).bytesEmitted(5L)));

  private ConnectionsHandler connectionsHandler;
  private SourceHandler sourceHandler;
  private DestinationHandler destinationHandler;
  private Job testJob;
  private Attempt testJobAttempt;
  private JobPersistence jobPersistence;
  private JobHistoryHandler jobHistoryHandler;

  private static JobRead toJobInfo(final Job job) {
    return new JobRead().id(job.getId())
        .configId(job.getScope())
        .status(Enums.convertTo(job.getStatus(), io.airbyte.api.model.generated.JobStatus.class))
        .configType(Enums.convertTo(job.getConfigType(), io.airbyte.api.model.generated.JobConfigType.class))
        .createdAt(job.getCreatedAtInSecond())
        .updatedAt(job.getUpdatedAtInSecond());

  }

  private static JobDebugRead toDebugJobInfo(final Job job) {
    return new JobDebugRead().id(job.getId())
        .configId(job.getScope())
        .status(Enums.convertTo(job.getStatus(), io.airbyte.api.model.generated.JobStatus.class))
        .configType(Enums.convertTo(job.getConfigType(), io.airbyte.api.model.generated.JobConfigType.class))
        .sourceDefinition(null)
        .destinationDefinition(null);

  }

  private static List<AttemptInfoRead> toAttemptInfoList(final List<Attempt> attempts) {
    final List<AttemptRead> attemptReads = attempts.stream().map(JobHistoryHandlerTest::toAttemptRead).collect(Collectors.toList());

    final Function<AttemptRead, AttemptInfoRead> toAttemptInfoRead = (AttemptRead a) -> new AttemptInfoRead().attempt(a).logs(EMPTY_LOG_READ);
    return attemptReads.stream().map(toAttemptInfoRead).collect(Collectors.toList());
  }

  private static AttemptRead toAttemptRead(final Attempt a) {
    return new AttemptRead()
        .id((long) a.getAttemptNumber())
        .status(Enums.convertTo(a.getStatus(), io.airbyte.api.model.generated.AttemptStatus.class))
        .createdAt(a.getCreatedAtInSecond())
        .updatedAt(a.getUpdatedAtInSecond())
        .endedAt(a.getEndedAtInSecond().orElse(null));
  }

  private static Attempt createAttempt(final long jobId, final long timestamps, final AttemptStatus status) {
    return new Attempt(ATTEMPT_NUMBER, jobId, LOG_PATH, null, status, null, null, timestamps, timestamps, timestamps);
  }

  @BeforeEach
  void setUp() {
    testJobAttempt = createAttempt(JOB_ID, CREATED_AT, AttemptStatus.SUCCEEDED);
    testJob = new Job(JOB_ID, JOB_CONFIG.getConfigType(), JOB_CONFIG_ID, JOB_CONFIG, ImmutableList.of(testJobAttempt), JOB_STATUS, null, CREATED_AT,
        CREATED_AT);

    connectionsHandler = mock(ConnectionsHandler.class);
    sourceHandler = mock(SourceHandler.class);
    destinationHandler = mock(DestinationHandler.class);
    jobPersistence = mock(JobPersistence.class);
    final SourceDefinitionsHandler sourceDefinitionsHandler = mock(SourceDefinitionsHandler.class);
    final DestinationDefinitionsHandler destinationDefinitionsHandler = mock(DestinationDefinitionsHandler.class);
    final AirbyteVersion airbyteVersion = mock(AirbyteVersion.class);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence, WorkerEnvironment.DOCKER, LogConfigs.EMPTY, connectionsHandler, sourceHandler,
        sourceDefinitionsHandler, destinationHandler, destinationDefinitionsHandler, airbyteVersion);
  }

  @Nested
  @DisplayName("When listing jobs")
  class ListJobs {

    @Test
    @DisplayName("Should return jobs with/without attempts in descending order")
    void testListJobs() throws IOException {
      final var successfulJob = testJob;
      final int pagesize = 25;
      final int rowOffset = 0;

      final var jobId2 = JOB_ID + 100;
      final var createdAt2 = CREATED_AT + 1000;
      final var latestJobNoAttempt =
          new Job(jobId2, JOB_CONFIG.getConfigType(), JOB_CONFIG_ID, JOB_CONFIG, Collections.emptyList(), JobStatus.PENDING,
              null, createdAt2, createdAt2);

      when(jobPersistence.listJobs(Set.of(Enums.convertTo(CONFIG_TYPE_FOR_API, ConfigType.class)), JOB_CONFIG_ID, pagesize, rowOffset))
          .thenReturn(List.of(latestJobNoAttempt, successfulJob));
      when(jobPersistence.getJobCount(Set.of(Enums.convertTo(CONFIG_TYPE_FOR_API, ConfigType.class)), JOB_CONFIG_ID)).thenReturn(2L);
      when(jobPersistence.getAttemptStats(List.of(200L, 100L))).thenReturn(Map.of(
          new JobAttemptPair(100, 0), ATTEMPT_STATS,
          new JobAttemptPair(jobId2, 0), ATTEMPT_STATS));

      final var requestBody = new JobListRequestBody()
          .configTypes(Collections.singletonList(CONFIG_TYPE_FOR_API))
          .configId(JOB_CONFIG_ID)
          .pagination(new Pagination().pageSize(pagesize).rowOffset(rowOffset));
      final var jobReadList = jobHistoryHandler.listJobsFor(requestBody);

      final var expAttemptRead = toAttemptRead(testJobAttempt).totalStats(ATTEMPT_STATS_API).streamStats(ATTEMPT_STREAM_STATS);
      final var successfulJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(successfulJob)).attempts(ImmutableList.of(expAttemptRead));
      final var latestJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(latestJobNoAttempt)).attempts(Collections.emptyList());
      final JobReadList expectedJobReadList =
          new JobReadList().jobs(List.of(latestJobWithAttemptRead, successfulJobWithAttemptRead)).totalJobCount(2L);

      assertEquals(expectedJobReadList, jobReadList);
    }

    @Test
    @DisplayName("Should return jobs in descending order regardless of type")
    void testListJobsFor() throws IOException {
      final var firstJob = testJob;
      final int pagesize = 25;
      final int rowOffset = 0;

      final var secondJobId = JOB_ID + 100;
      final var createdAt2 = CREATED_AT + 1000;
      final var secondJobAttempt = createAttempt(secondJobId, createdAt2, AttemptStatus.SUCCEEDED);
      final var secondJob = new Job(secondJobId, ConfigType.DISCOVER_SCHEMA, JOB_CONFIG_ID, JOB_CONFIG, ImmutableList.of(secondJobAttempt),
          JobStatus.SUCCEEDED, null, createdAt2, createdAt2);

      final Set<ConfigType> configTypes = Set.of(
          Enums.convertTo(CONFIG_TYPE_FOR_API, ConfigType.class),
          Enums.convertTo(JobConfigType.SYNC, ConfigType.class),
          Enums.convertTo(JobConfigType.DISCOVER_SCHEMA, ConfigType.class));

      final var latestJobId = secondJobId + 100;
      final var createdAt3 = createdAt2 + 1000;
      final var latestJob =
          new Job(latestJobId, ConfigType.SYNC, JOB_CONFIG_ID, JOB_CONFIG, Collections.emptyList(), JobStatus.PENDING, null, createdAt3, createdAt3);

      when(jobPersistence.listJobs(configTypes, JOB_CONFIG_ID, pagesize, rowOffset)).thenReturn(List.of(latestJob, secondJob, firstJob));
      when(jobPersistence.getJobCount(configTypes, JOB_CONFIG_ID)).thenReturn(3L);
      when(jobPersistence.getAttemptStats(List.of(300L, 200L, 100L))).thenReturn(Map.of(
          new JobAttemptPair(100, 0), ATTEMPT_STATS,
          new JobAttemptPair(secondJobId, 0), ATTEMPT_STATS,
          new JobAttemptPair(latestJobId, 0), ATTEMPT_STATS));

      final JobListRequestBody requestBody = new JobListRequestBody()
          .configTypes(List.of(CONFIG_TYPE_FOR_API, JobConfigType.SYNC, JobConfigType.DISCOVER_SCHEMA))
          .configId(JOB_CONFIG_ID)
          .pagination(new Pagination().pageSize(pagesize).rowOffset(rowOffset));
      final JobReadList jobReadList = jobHistoryHandler.listJobsFor(requestBody);

      final var firstJobWithAttemptRead =
          new JobWithAttemptsRead().job(toJobInfo(firstJob))
              .attempts(ImmutableList.of(toAttemptRead(testJobAttempt).totalStats(ATTEMPT_STATS_API).streamStats(ATTEMPT_STREAM_STATS)));
      final var secondJobWithAttemptRead =
          new JobWithAttemptsRead().job(toJobInfo(secondJob))
              .attempts(ImmutableList.of(toAttemptRead(secondJobAttempt).totalStats(ATTEMPT_STATS_API).streamStats(ATTEMPT_STREAM_STATS)));
      final var latestJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(latestJob)).attempts(Collections.emptyList());
      final JobReadList expectedJobReadList =
          new JobReadList().jobs(List.of(latestJobWithAttemptRead, secondJobWithAttemptRead, firstJobWithAttemptRead)).totalJobCount(3L);

      assertEquals(expectedJobReadList, jobReadList);
    }

    @Test
    @DisplayName("Should return jobs including specified job id")
    void testListJobsIncludingJobId() throws IOException {
      final var successfulJob = testJob;
      final int pagesize = 25;
      final int rowOffset = 0;

      final var jobId2 = JOB_ID + 100;
      final var createdAt2 = CREATED_AT + 1000;
      final var latestJobNoAttempt =
          new Job(jobId2, JOB_CONFIG.getConfigType(), JOB_CONFIG_ID, JOB_CONFIG, Collections.emptyList(), JobStatus.PENDING,
              null, createdAt2, createdAt2);

      when(jobPersistence.listJobsIncludingId(Set.of(Enums.convertTo(CONFIG_TYPE_FOR_API, ConfigType.class)), JOB_CONFIG_ID, jobId2, pagesize))
          .thenReturn(List.of(latestJobNoAttempt, successfulJob));
      when(jobPersistence.getJobCount(Set.of(Enums.convertTo(CONFIG_TYPE_FOR_API, ConfigType.class)), JOB_CONFIG_ID)).thenReturn(2L);
      when(jobPersistence.getAttemptStats(List.of(200L, 100L))).thenReturn(Map.of(
          new JobAttemptPair(100, 0), ATTEMPT_STATS,
          new JobAttemptPair(jobId2, 0), ATTEMPT_STATS));

      final var requestBody = new JobListRequestBody()
          .configTypes(Collections.singletonList(CONFIG_TYPE_FOR_API))
          .configId(JOB_CONFIG_ID)
          .includingJobId(jobId2)
          .pagination(new Pagination().pageSize(pagesize).rowOffset(rowOffset));
      final var jobReadList = jobHistoryHandler.listJobsFor(requestBody);

      final var successfulJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(successfulJob)).attempts(ImmutableList.of(toAttemptRead(
          testJobAttempt).totalStats(ATTEMPT_STATS_API).streamStats(ATTEMPT_STREAM_STATS)));
      final var latestJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(latestJobNoAttempt)).attempts(Collections.emptyList());
      final JobReadList expectedJobReadList =
          new JobReadList().jobs(List.of(latestJobWithAttemptRead, successfulJobWithAttemptRead)).totalJobCount(2L);

      assertEquals(expectedJobReadList, jobReadList);
    }

  }

  @Test
  @DisplayName("Should return the right job info")
  void testGetJobInfo() throws IOException {
    when(jobPersistence.getJob(JOB_ID)).thenReturn(testJob);

    final JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    final JobInfoRead jobInfoActual = jobHistoryHandler.getJobInfo(requestBody);

    final JobInfoRead exp = new JobInfoRead().job(toJobInfo(testJob)).attempts(toAttemptInfoList(ImmutableList.of(testJobAttempt)));

    assertEquals(exp, jobInfoActual);
  }

  @Test
  @DisplayName("Should return the right job info without attempt information")
  void testGetJobInfoLight() throws IOException {
    when(jobPersistence.getJob(JOB_ID)).thenReturn(testJob);

    final JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    final JobInfoLightRead jobInfoLightActual = jobHistoryHandler.getJobInfoLight(requestBody);

    final JobInfoLightRead exp = new JobInfoLightRead().job(toJobInfo(testJob));

    assertEquals(exp, jobInfoLightActual);
  }

  @Test
  @DisplayName("Should return the right info to debug this job")
  void testGetDebugJobInfo() throws IOException, JsonValidationException, ConfigNotFoundException, URISyntaxException {
    final StandardSourceDefinition standardSourceDefinition = SourceDefinitionHelpers.generateSourceDefinition();
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    final SourceRead sourceRead = SourceHelpers.getSourceRead(source, standardSourceDefinition);

    final StandardDestinationDefinition standardDestinationDefinition = DestinationDefinitionHelpers.generateDestination();
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    final DestinationRead destinationRead = DestinationHelpers.getDestinationRead(destination, standardDestinationDefinition);

    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(source.getSourceId());
    final ConnectionRead connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);
    when(connectionsHandler.getConnection(UUID.fromString(testJob.getScope()))).thenReturn(connectionRead);

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody();
    sourceIdRequestBody.setSourceId(connectionRead.getSourceId());
    when(sourceHandler.getSource(sourceIdRequestBody)).thenReturn(sourceRead);

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody();
    destinationIdRequestBody.setDestinationId(connectionRead.getDestinationId());
    when(destinationHandler.getDestination(destinationIdRequestBody)).thenReturn(destinationRead);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(testJob);
    when(jobPersistence.getAttemptStats(anyLong(), anyInt())).thenReturn(ATTEMPT_STATS);

    final JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    final JobDebugInfoRead jobDebugInfoActual = jobHistoryHandler.getJobDebugInfo(requestBody);
    final List<AttemptInfoRead> attemptInfoReads = toAttemptInfoList(ImmutableList.of(testJobAttempt));
    attemptInfoReads.forEach(read -> read.getAttempt().totalStats(ATTEMPT_STATS_API).streamStats(ATTEMPT_STREAM_STATS));
    final JobDebugInfoRead exp = new JobDebugInfoRead().job(toDebugJobInfo(testJob)).attempts(attemptInfoReads);

    assertEquals(exp, jobDebugInfoActual);
  }

  @Test
  @DisplayName("Should return the latest running sync job")
  void testGetLatestRunningSyncJob() throws IOException {
    final var connectionId = UUID.randomUUID();

    final var olderRunningJobId = JOB_ID + 100;
    final var olderRunningCreatedAt = CREATED_AT + 1000;
    final var olderRunningJobAttempt = createAttempt(olderRunningJobId, olderRunningCreatedAt, AttemptStatus.RUNNING);
    final var olderRunningJob = new Job(olderRunningJobId, ConfigType.SYNC, JOB_CONFIG_ID,
        JOB_CONFIG, ImmutableList.of(olderRunningJobAttempt),
        JobStatus.RUNNING, null, olderRunningCreatedAt, olderRunningCreatedAt);

    // expect that we return the newer of the two running jobs. this should not happen in the real
    // world but might as
    // well test that we handle it properly.
    final var newerRunningJobId = JOB_ID + 200;
    final var newerRunningCreatedAt = CREATED_AT + 2000;
    final var newerRunningJobAttempt = createAttempt(newerRunningJobId, newerRunningCreatedAt, AttemptStatus.RUNNING);
    final var newerRunningJob = new Job(newerRunningJobId, ConfigType.SYNC, JOB_CONFIG_ID,
        JOB_CONFIG, ImmutableList.of(newerRunningJobAttempt),
        JobStatus.RUNNING, null, newerRunningCreatedAt, newerRunningCreatedAt);

    when(jobPersistence.listJobsForConnectionWithStatuses(
        connectionId,
        Collections.singleton(ConfigType.SYNC),
        JobStatus.NON_TERMINAL_STATUSES)).thenReturn(List.of(newerRunningJob, olderRunningJob));

    final Optional<JobRead> expectedJob = Optional.of(JobConverter.getJobRead(newerRunningJob));
    final Optional<JobRead> actualJob = jobHistoryHandler.getLatestRunningSyncJob(connectionId);

    assertEquals(expectedJob, actualJob);
  }

  @Test
  @DisplayName("Should return an empty optional if no running sync job")
  void testGetLatestRunningSyncJobWhenNone() throws IOException {
    final var connectionId = UUID.randomUUID();

    when(jobPersistence.listJobsForConnectionWithStatuses(
        connectionId,
        Collections.singleton(ConfigType.SYNC),
        JobStatus.NON_TERMINAL_STATUSES)).thenReturn(Collections.emptyList());

    final Optional<JobRead> actual = jobHistoryHandler.getLatestRunningSyncJob(connectionId);

    assertTrue(actual.isEmpty());
  }

  @Test
  @DisplayName("Should return the latest sync job")
  void testGetLatestSyncJob() throws IOException {
    final var connectionId = UUID.randomUUID();

    // expect the newest job overall to be returned, even if it is failed
    final var newerFailedJobId = JOB_ID + 200;
    final var newerFailedCreatedAt = CREATED_AT + 2000;
    final var newerFailedJobAttempt = createAttempt(newerFailedJobId, newerFailedCreatedAt, AttemptStatus.FAILED);
    final var newerFailedJob = new Job(newerFailedJobId, ConfigType.SYNC, JOB_CONFIG_ID,
        JOB_CONFIG, ImmutableList.of(newerFailedJobAttempt),
        JobStatus.RUNNING, null, newerFailedCreatedAt, newerFailedCreatedAt);

    when(jobPersistence.getLastSyncJob(connectionId)).thenReturn(Optional.of(newerFailedJob));

    final Optional<JobRead> expectedJob = Optional.of(JobConverter.getJobRead(newerFailedJob));
    final Optional<JobRead> actualJob = jobHistoryHandler.getLatestSyncJob(connectionId);

    assertEquals(expectedJob, actualJob);
  }

  @Test
  @DisplayName("Should have compatible config enums")
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(JobConfig.ConfigType.class, JobConfigType.class));
  }

  @Test
  @DisplayName("Should return attempt normalization info for the job")
  void testGetAttemptNormalizationStatuses() throws IOException {

    final AttemptNormalizationStatus databaseReadResult = new AttemptNormalizationStatus(1, Optional.of(10L), /* hasNormalizationFailed= */ false);

    when(jobPersistence.getAttemptNormalizationStatusesForJob(JOB_ID)).thenReturn(List.of(databaseReadResult));

    final AttemptNormalizationStatusReadList expectedStatus = new AttemptNormalizationStatusReadList().attemptNormalizationStatuses(
        List.of(new AttemptNormalizationStatusRead().attemptNumber(1).hasRecordsCommitted(true).hasNormalizationFailed(false).recordsCommitted(10L)));

    assertEquals(expectedStatus, jobHistoryHandler.getAttemptNormalizationStatuses(new JobIdRequestBody().id(JOB_ID)));

  }

}
