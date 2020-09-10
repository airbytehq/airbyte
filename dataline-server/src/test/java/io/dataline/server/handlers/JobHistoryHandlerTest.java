/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.server.handlers;

import com.google.common.collect.Iterables;
import io.dataline.api.model.JobConfigType;
import io.dataline.api.model.JobIdRequestBody;
import io.dataline.api.model.JobInfoRead;
import io.dataline.api.model.JobListRequestBody;
import io.dataline.api.model.JobRead;
import io.dataline.api.model.JobReadList;
import io.dataline.api.model.LogRead;
import io.dataline.config.JobCheckConnectionConfig;
import io.dataline.config.JobConfig;
import io.dataline.scheduler.Job;
import io.dataline.scheduler.JobStatus;
import io.dataline.scheduler.ScopeHelper;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Writer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

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
  private static final String STDOUT_PATH = "stdout-path";
  private static final String STDERR_PATH = "stderr-path";
  private static final long CREATED_AT = System.currentTimeMillis() / 1000;

  private static final Job JOB = new Job(
      JOB_ID,
      SCOPE,
      JOB_STATUS,
      JOB_CONFIG,
      null,
      STDOUT_PATH,
      STDERR_PATH,
      CREATED_AT,
      null,
      CREATED_AT);

  private static final JobInfoRead JOB_INFO =
      new JobInfoRead()
          .job(
              new JobRead()
                  .id(JOB_ID)
                  .configId(JOB_CONFIG_ID)
                  .status(JobRead.StatusEnum.PENDING)
                  .configType(JobConfigType.CHECK_CONNECTION_SOURCE)
                  .createdAt(CREATED_AT)
                  .startedAt(null)
                  .updatedAt(CREATED_AT))
          .logs(
              new LogRead()
                  .stdout(new ArrayList<>())
                  .stderr(new ArrayList<>()));

  private SchedulerPersistence schedulerPersistence;
  private JobHistoryHandler jobHistoryHandler;

  @BeforeEach
  public void setUp() {
    schedulerPersistence = mock(SchedulerPersistence.class);
    jobHistoryHandler = new JobHistoryHandler(schedulerPersistence);
  }

  @Test
  public void testListJobsFor() throws IOException {
    when(schedulerPersistence.listJobs(CONFIG_TYPE, JOB_CONFIG_ID)).thenReturn(Collections.singletonList(JOB));

    JobListRequestBody requestBody = new JobListRequestBody().configType(CONFIG_TYPE_FOR_API).configId(JOB_CONFIG_ID);
    JobReadList jobReadList = jobHistoryHandler.listJobsFor(requestBody);

    JobReadList expectedJobReadList = new JobReadList().jobs(Collections.singletonList(JOB_INFO.getJob()));

    assertEquals(expectedJobReadList, jobReadList);
  }

  @Test
  public void testGetJobInfo() throws IOException {
    when(schedulerPersistence.getJob(JOB_ID)).thenReturn(JOB);

    JobIdRequestBody requestBody = new JobIdRequestBody().id(JOB_ID);
    JobInfoRead jobInfoActual = jobHistoryHandler.getJobInfo(requestBody);

    assertEquals(JOB_INFO, jobInfoActual);
  }

  @Test
  public void testGetJobRead() {
    JobRead jobReadActual = JobHistoryHandler.getJobRead(JOB);
    assertEquals(JOB_INFO.getJob(), jobReadActual);
  }

  @Test
  public void testGetTailDoesNotExist() throws IOException {
    List<String> tail = JobHistoryHandler.getTail(100, RandomStringUtils.random(100));
    assertEquals(Collections.emptyList(), tail);
  }

  @Test
  public void testGetTailExists() throws IOException {
    Path stdoutFile = Files.createTempFile("job-history-handler-test", "stdout");

    List<String> head = List.of(
        "line1",
        "line2",
        "line3",
        "line4");

    List<String> expectedTail = List.of(
        "line5",
        "line6",
        "line7",
        "line8");

    Writer writer = new BufferedWriter(new FileWriter(stdoutFile.toString(), true));

    for (String line : Iterables.concat(head, expectedTail)) {
      writer.write(line + "\n");
    }

    writer.close();

    List<String> tail = JobHistoryHandler.getTail(expectedTail.size(), stdoutFile.toString());
    assertEquals(expectedTail, tail);
  }

}
