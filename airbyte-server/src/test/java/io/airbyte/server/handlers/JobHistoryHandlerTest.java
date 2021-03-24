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

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
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
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.AttemptStatus;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Optional;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class JobHistoryHandlerTest {

  private static final long JOB_ID = 100L;
  private static final long ATTEMPT_ID = 1002L;
  private static final String JOB_CONFIG_ID = "123";
  private static final JobStatus JOB_STATUS = JobStatus.RUNNING;
  private static final AttemptStatus ATTEMPT_STATUS = AttemptStatus.RUNNING;
  private static final JobConfig.ConfigType CONFIG_TYPE = JobConfig.ConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfigType CONFIG_TYPE_FOR_API = JobConfigType.CHECK_CONNECTION_SOURCE;
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

  private JobPersistence jobPersistence;
  private JobHistoryHandler jobHistoryHandler;

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

    jobPersistence = mock(JobPersistence.class);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence);
  }

  @Test
  public void testListJobsFor() throws IOException {
    when(jobPersistence.listJobs(CONFIG_TYPE, JOB_CONFIG_ID)).thenReturn(Collections.singletonList(job));

    final JobListRequestBody requestBody = new JobListRequestBody()
        .configTypes(Collections.singletonList(CONFIG_TYPE_FOR_API))
        .configId(JOB_CONFIG_ID);
    final JobReadList jobReadList = jobHistoryHandler.listJobsFor(requestBody);

    final JobReadList expectedJobReadList = new JobReadList().jobs(Collections.singletonList(JOB_WITH_ATTEMPTS_READ));

    assertEquals(expectedJobReadList, jobReadList);
  }

  @Test
  public void testGetJobInfo() throws IOException {
    when(jobPersistence.getJob(JOB_ID)).thenReturn(job);

    final JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    final JobInfoRead jobInfoActual = jobHistoryHandler.getJobInfo(requestBody);

    assertEquals(JOB_INFO, jobInfoActual);
  }

  @Test
  public void testEnumConversion() {
    assertTrue(Enums.isCompatible(JobConfig.ConfigType.class, JobConfigType.class));
  }

}
