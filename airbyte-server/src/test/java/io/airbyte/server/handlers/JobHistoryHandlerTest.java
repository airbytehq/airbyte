/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.ImmutableList;
import io.airbyte.api.model.AttemptInfoRead;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.LogRead;
import io.airbyte.api.model.Pagination;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.AttemptStatus;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

@DisplayName("Job History Handler")
public class JobHistoryHandlerTest {

  private static final long JOB_ID = 100L;
  private static final long ATTEMPT_ID = 1002L;
  private static final String JOB_CONFIG_ID = "123";
  private static final JobStatus JOB_STATUS = JobStatus.SUCCEEDED;
  private static final JobConfig.ConfigType CONFIG_TYPE = JobConfig.ConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfigType CONFIG_TYPE_FOR_API = JobConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfig JOB_CONFIG = new JobConfig()
      .withConfigType(CONFIG_TYPE)
      .withCheckConnection(new JobCheckConnectionConfig());
  private static final Path LOG_PATH = Path.of("log_path");
  private static final LogRead EMPTY_LOG_READ = new LogRead().logLines(new ArrayList<>());
  private static final long CREATED_AT = System.currentTimeMillis() / 1000;

  private Job testJob;
  private Attempt testJobAttempt;
  private JobPersistence jobPersistence;
  private JobHistoryHandler jobHistoryHandler;

  private static JobRead toJobInfo(Job job) {
    return new JobRead().id(job.getId())
        .configId(job.getScope())
        .status(Enums.convertTo(job.getStatus(), io.airbyte.api.model.JobStatus.class))
        .configType(Enums.convertTo(job.getConfigType(), io.airbyte.api.model.JobConfigType.class))
        .createdAt(job.getCreatedAtInSecond())
        .updatedAt(job.getUpdatedAtInSecond());

  }

  private static List<AttemptInfoRead> toAttemptInfoList(List<Attempt> attempts) {
    final List<AttemptRead> attemptReads = attempts.stream().map(JobHistoryHandlerTest::toAttemptRead).collect(Collectors.toList());

    final Function<AttemptRead, AttemptInfoRead> toAttemptInfoRead = (AttemptRead a) -> new AttemptInfoRead().attempt(a).logs(EMPTY_LOG_READ);
    return attemptReads.stream().map(toAttemptInfoRead).collect(Collectors.toList());
  }

  private static AttemptRead toAttemptRead(Attempt a) {
    return new AttemptRead()
        .id(a.getId())
        .status(Enums.convertTo(a.getStatus(), io.airbyte.api.model.AttemptStatus.class))
        .createdAt(a.getCreatedAtInSecond())
        .updatedAt(a.getUpdatedAtInSecond())
        .endedAt(a.getEndedAtInSecond().orElse(null));
  }

  private static Attempt createSuccessfulAttempt(long jobId, long timestamps) {
    return new Attempt(ATTEMPT_ID, jobId, LOG_PATH, null, AttemptStatus.SUCCEEDED, timestamps, timestamps, timestamps);
  }

  @BeforeEach
  public void setUp() {
    testJobAttempt = createSuccessfulAttempt(JOB_ID, CREATED_AT);
    testJob = new Job(JOB_ID, JOB_CONFIG.getConfigType(), JOB_CONFIG_ID, JOB_CONFIG, ImmutableList.of(testJobAttempt), JOB_STATUS, null, CREATED_AT,
        CREATED_AT);

    jobPersistence = mock(JobPersistence.class);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence);
  }

  @Nested
  @DisplayName("When listing jobs")
  class ListJobs {

    @Test
    @DisplayName("Should return jobs with/without attempts in descending order")
    public void testListJobs() throws IOException {
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
    public void testListJobsFor() throws IOException {
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
  public void testGetJobInfo() throws IOException {
    when(jobPersistence.getJob(JOB_ID)).thenReturn(testJob);

    final JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    final JobInfoRead jobInfoActual = jobHistoryHandler.getJobInfo(requestBody);

    final JobInfoRead exp = new JobInfoRead().job(toJobInfo(testJob)).attempts(toAttemptInfoList(ImmutableList.of(testJobAttempt)));

    assertEquals(exp, jobInfoActual);
  }

  @Test
  @DisplayName("Should have compatible config enums")
  public void testEnumConversion() {
    assertTrue(Enums.isCompatible(JobConfig.ConfigType.class, JobConfigType.class));
  }

}
