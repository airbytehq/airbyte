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
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.LogRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.ScopeHelper;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class JobHistoryHandlerTest {

  private static final long JOB_ID = 100;
  private static final String SCOPE = "sync:123";
  private static final String JOB_CONFIG_ID = ScopeHelper.getConfigId(SCOPE);
  private static final JobStatus JOB_STATUS = JobStatus.PENDING;
  private static final JobConfig.ConfigType CONFIG_TYPE = JobConfig.ConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfigType CONFIG_TYPE_FOR_API = JobConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfig JOB_CONFIG = new JobConfig()
      .withConfigType(CONFIG_TYPE)
      .withCheckConnection(new JobCheckConnectionConfig());
  private static final String LOG_PATH = "log_path";
  private static final long CREATED_AT = System.currentTimeMillis() / 1000;

  private Job job;

  private static final JobInfoRead JOB_INFO =
      new JobInfoRead()
          .job(new JobRead()
              .id(JOB_ID)
              .configId(JOB_CONFIG_ID)
              .status(io.airbyte.api.model.JobStatus.PENDING)
              .configType(JobConfigType.CHECK_CONNECTION_SOURCE)
              .createdAt(CREATED_AT)
              .updatedAt(CREATED_AT))
          .logs(new LogRead().logLines(new ArrayList<>()));

  private JobPersistence jobPersistence;
  private JobHistoryHandler jobHistoryHandler;

  @BeforeEach
  public void setUp() {
    job = mock(Job.class);
    final Attempt attempt = mock(Attempt.class);
    when(job.getId()).thenReturn(JOB_ID);
    when(job.getScope()).thenReturn(SCOPE);
    when(job.getConfig()).thenReturn(JOB_CONFIG);
    when(job.getStatus()).thenReturn(JOB_STATUS);
    when(job.getAttempts()).thenReturn(Lists.newArrayList(attempt));
    when(attempt.getLogPath()).thenReturn(Path.of(LOG_PATH));
    when(job.getCreatedAtInSecond()).thenReturn(CREATED_AT);
    when(job.getUpdatedAtInSecond()).thenReturn(CREATED_AT);

    jobPersistence = mock(JobPersistence.class);
    jobHistoryHandler = new JobHistoryHandler(jobPersistence);
  }

  @Test
  public void testListJobsFor() throws IOException {
    when(jobPersistence.listJobs(CONFIG_TYPE, JOB_CONFIG_ID)).thenReturn(Collections.singletonList(job));

    JobListRequestBody requestBody = new JobListRequestBody().configType(CONFIG_TYPE_FOR_API).configId(JOB_CONFIG_ID);
    JobReadList jobReadList = jobHistoryHandler.listJobsFor(requestBody);

    JobReadList expectedJobReadList = new JobReadList().jobs(Collections.singletonList(JOB_INFO.getJob()));

    assertEquals(expectedJobReadList, jobReadList);
  }

  @Test
  public void testGetJobInfo() throws IOException {
    when(jobPersistence.getJob(JOB_ID)).thenReturn(job);

    JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    JobInfoRead jobInfoActual = jobHistoryHandler.getJobInfo(requestBody);

    assertEquals(JOB_INFO, jobInfoActual);
  }

  @Test
  public void testGetJobRead() {
    JobRead jobReadActual = JobHistoryHandler.getJobRead(job);
    assertEquals(JOB_INFO.getJob(), jobReadActual);
  }

  @Test
  public void testEnumConversion() {
    assertTrue(Enums.isCompatible(JobConfig.ConfigType.class, JobConfigType.class));
    // todo (cgardens) - bring back in next PR.
    // assertTrue(Enums.isCompatible(JobStatus.class, io.airbyte.api.model.JobStatus.class));
    // assertTrue(Enums.isCompatible(AttemptStatus.class, io.airbyte.api.model.AttemptStatus.class));
  }

}
