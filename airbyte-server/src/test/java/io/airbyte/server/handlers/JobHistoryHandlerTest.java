/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableList;
import io.airbyte.api.model.generated.*;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.*;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.AttemptStatus;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.helpers.ConnectionHelpers;
import io.airbyte.server.helpers.DestinationDefinitionHelpers;
import io.airbyte.server.helpers.DestinationHelpers;
import io.airbyte.server.helpers.SourceDefinitionHelpers;
import io.airbyte.server.helpers.SourceHelpers;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Path;
import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

@DisplayName("Job History Handler")
class JobHistoryHandlerTest {

  private static final long JOB_ID = 100L;
  private static final long ATTEMPT_ID = 1002L;
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

  private SourceRead sourceRead;
  private ConnectionRead connectionRead;
  private DestinationRead destinationRead;
  private ConnectionsHandler connectionsHandler;
  private SourceHandler sourceHandler;
  private DestinationHandler destinationHandler;
  private SourceDefinitionsHandler sourceDefinitionsHandler;
  private DestinationDefinitionsHandler destinationDefinitionsHandler;
  private StandardDestinationDefinition standardDestinationDefinition;
  private StandardSourceDefinition standardSourceDefinition;
  private AirbyteVersion airbyteVersion;
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
        .id(a.getId())
        .status(Enums.convertTo(a.getStatus(), io.airbyte.api.model.generated.AttemptStatus.class))
        .createdAt(a.getCreatedAtInSecond())
        .updatedAt(a.getUpdatedAtInSecond())
        .endedAt(a.getEndedAtInSecond().orElse(null));
  }

  private static Attempt createSuccessfulAttempt(final long jobId, final long timestamps) {
    return new Attempt(ATTEMPT_ID, jobId, LOG_PATH, null, AttemptStatus.SUCCEEDED, null, timestamps, timestamps, timestamps);
  }

  @BeforeEach
  void setUp() throws IOException, JsonValidationException, ConfigNotFoundException {
    testJobAttempt = createSuccessfulAttempt(JOB_ID, CREATED_AT);
    testJob = new Job(JOB_ID, JOB_CONFIG.getConfigType(), JOB_CONFIG_ID, JOB_CONFIG, ImmutableList.of(testJobAttempt), JOB_STATUS, null, CREATED_AT,
        CREATED_AT);

    connectionsHandler = mock(ConnectionsHandler.class);
    sourceHandler = mock(SourceHandler.class);
    sourceDefinitionsHandler = mock(SourceDefinitionsHandler.class);
    destinationHandler = mock(DestinationHandler.class);
    destinationDefinitionsHandler = mock(DestinationDefinitionsHandler.class);
    airbyteVersion = mock(AirbyteVersion.class);
    jobPersistence = mock(JobPersistence.class);
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

      final var requestBody = new JobListRequestBody()
          .configTypes(Collections.singletonList(CONFIG_TYPE_FOR_API))
          .configId(JOB_CONFIG_ID)
          .pagination(new Pagination().pageSize(pagesize).rowOffset(rowOffset));
      final var jobReadList = jobHistoryHandler.listJobsFor(requestBody);

      final var successfulJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(successfulJob)).attempts(ImmutableList.of(toAttemptRead(
          testJobAttempt)));
      final var latestJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(latestJobNoAttempt)).attempts(Collections.emptyList());
      final JobReadList expectedJobReadList = new JobReadList().jobs(List.of(latestJobWithAttemptRead, successfulJobWithAttemptRead));

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
      final var secondJobAttempt = createSuccessfulAttempt(secondJobId, createdAt2);
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

      final JobListRequestBody requestBody = new JobListRequestBody()
          .configTypes(List.of(CONFIG_TYPE_FOR_API, JobConfigType.SYNC, JobConfigType.DISCOVER_SCHEMA))
          .configId(JOB_CONFIG_ID)
          .pagination(new Pagination().pageSize(pagesize).rowOffset(rowOffset));
      final JobReadList jobReadList = jobHistoryHandler.listJobsFor(requestBody);

      final var firstJobWithAttemptRead =
          new JobWithAttemptsRead().job(toJobInfo(firstJob)).attempts(ImmutableList.of(toAttemptRead(testJobAttempt)));
      final var secondJobWithAttemptRead =
          new JobWithAttemptsRead().job(toJobInfo(secondJob)).attempts(ImmutableList.of(toAttemptRead(secondJobAttempt)));
      final var latestJobWithAttemptRead = new JobWithAttemptsRead().job(toJobInfo(latestJob)).attempts(Collections.emptyList());
      final JobReadList expectedJobReadList =
          new JobReadList().jobs(List.of(latestJobWithAttemptRead, secondJobWithAttemptRead, firstJobWithAttemptRead));

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
  @DisplayName("Should return the right info to debug this job")
  void testGetDebugJobInfo() throws IOException, JsonValidationException, ConfigNotFoundException, URISyntaxException {
    standardSourceDefinition = SourceDefinitionHelpers.generateSourceDefinition();
    final SourceConnection source = SourceHelpers.generateSource(UUID.randomUUID());
    sourceRead = SourceHelpers.getSourceRead(source, standardSourceDefinition);

    standardDestinationDefinition = DestinationDefinitionHelpers.generateDestination();
    final DestinationConnection destination = DestinationHelpers.generateDestination(UUID.randomUUID());
    destinationRead = DestinationHelpers.getDestinationRead(destination, standardDestinationDefinition);

    final StandardSync standardSync = ConnectionHelpers.generateSyncWithSourceId(source.getSourceId());
    connectionRead = ConnectionHelpers.generateExpectedConnectionRead(standardSync);
    when(connectionsHandler.getConnection(UUID.fromString(testJob.getScope()))).thenReturn(connectionRead);

    final SourceIdRequestBody sourceIdRequestBody = new SourceIdRequestBody();
    sourceIdRequestBody.setSourceId(connectionRead.getSourceId());
    when(sourceHandler.getSource(sourceIdRequestBody)).thenReturn(sourceRead);

    final DestinationIdRequestBody destinationIdRequestBody = new DestinationIdRequestBody();
    destinationIdRequestBody.setDestinationId(connectionRead.getDestinationId());
    when(destinationHandler.getDestination(destinationIdRequestBody)).thenReturn(destinationRead);
    when(jobPersistence.getJob(JOB_ID)).thenReturn(testJob);

    final JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    final JobDebugInfoRead jobDebugInfoActual = jobHistoryHandler.getJobDebugInfo(requestBody);
    final JobDebugInfoRead exp = new JobDebugInfoRead().job(toDebugJobInfo(testJob)).attempts(toAttemptInfoList(ImmutableList.of(testJobAttempt)));

    assertEquals(exp, jobDebugInfoActual);
  }

  @Test
  @DisplayName("Should have compatible config enums")
  void testEnumConversion() {
    assertTrue(Enums.isCompatible(JobConfig.ConfigType.class, JobConfigType.class));
  }

}
