/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.AttemptInfoRead;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.LogRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.AttemptStatus;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Optional;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobConverterTest {

  private static final long JOB_ID = 100L;
  private static final long ATTEMPT_ID = 1002L;
  private static final String JOB_CONFIG_ID = "123";
  private static final JobStatus JOB_STATUS = JobStatus.RUNNING;
  private static final AttemptStatus ATTEMPT_STATUS = AttemptStatus.RUNNING;
  private static final JobConfig.ConfigType CONFIG_TYPE = JobConfig.ConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfig JOB_CONFIG = new JobConfig()
      .withConfigType(CONFIG_TYPE)
      .withCheckConnection(new JobCheckConnectionConfig());
  private static final Path LOG_PATH = Path.of("log_path");
  private static final long CREATED_AT = System.currentTimeMillis() / 1000;

  private Job job;

  private static final JobInfoRead JOB_INFO =
      new JobInfoRead()
          .job(new JobRead()
              .id(JOB_ID)
              .configId(JOB_CONFIG_ID)
              .status(io.airbyte.api.model.JobStatus.RUNNING)
              .configType(JobConfigType.CHECK_CONNECTION_SOURCE)
              .createdAt(CREATED_AT)
              .updatedAt(CREATED_AT))
          .attempts(Lists.newArrayList(new AttemptInfoRead()
              .attempt(new AttemptRead()
                  .id(ATTEMPT_ID)
                  .status(io.airbyte.api.model.AttemptStatus.RUNNING)
                  .updatedAt(CREATED_AT)
                  .createdAt(CREATED_AT)
                  .endedAt(CREATED_AT))
              .logs(new LogRead().logLines(new ArrayList<>()))));

  private static final JobWithAttemptsRead JOB_WITH_ATTEMPTS_READ = new JobWithAttemptsRead()
      .job(JOB_INFO.getJob())
      .attempts(JOB_INFO.getAttempts().stream().map(AttemptInfoRead::getAttempt).collect(Collectors.toList()));

  @BeforeEach
  public void setUp() {
    job = mock(Job.class);
    Attempt attempt = mock(Attempt.class);
    when(job.getId()).thenReturn(JOB_ID);
    when(job.getConfigType()).thenReturn(JOB_CONFIG.getConfigType());
    when(job.getScope()).thenReturn(JOB_CONFIG_ID);
    when(job.getConfig()).thenReturn(JOB_CONFIG);
    when(job.getStatus()).thenReturn(JOB_STATUS);
    when(job.getCreatedAtInSecond()).thenReturn(CREATED_AT);
    when(job.getUpdatedAtInSecond()).thenReturn(CREATED_AT);
    when(job.getAttempts()).thenReturn(Lists.newArrayList(attempt));
    when(attempt.getId()).thenReturn(ATTEMPT_ID);
    when(attempt.getStatus()).thenReturn(ATTEMPT_STATUS);
    when(attempt.getLogPath()).thenReturn(LOG_PATH);
    when(attempt.getCreatedAtInSecond()).thenReturn(CREATED_AT);
    when(attempt.getUpdatedAtInSecond()).thenReturn(CREATED_AT);
    when(attempt.getEndedAtInSecond()).thenReturn(Optional.of(CREATED_AT));
  }

  @Test
  public void testGetJobInfoRead() {
    assertEquals(JOB_INFO, JobConverter.getJobInfoRead(job));
  }

  @Test
  public void testGetJobWithAttemptsRead() {
    assertEquals(JOB_WITH_ATTEMPTS_READ, JobConverter.getJobWithAttemptsRead(job));
  }

  @Test
  public void testGetJobRead() {
    final JobWithAttemptsRead jobReadActual = JobConverter.getJobWithAttemptsRead(job);
    assertEquals(JOB_WITH_ATTEMPTS_READ, jobReadActual);
  }

  @Test
  public void testEnumConversion() {
    assertTrue(Enums.isCompatible(JobConfig.ConfigType.class, JobConfigType.class));
    assertTrue(Enums.isCompatible(JobStatus.class, io.airbyte.api.model.JobStatus.class));
    assertTrue(Enums.isCompatible(AttemptStatus.class, io.airbyte.api.model.AttemptStatus.class));
  }

}
