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

import com.google.common.base.Charsets;
import io.dataline.api.model.ConnectionIdRequestBody;
import io.dataline.api.model.JobIdRequestBody;
import io.dataline.api.model.JobInfoRead;
import io.dataline.api.model.JobRead;
import io.dataline.api.model.JobReadList;
import io.dataline.api.model.LogRead;
import io.dataline.scheduler.Job;
import io.dataline.scheduler.JobStatus;
import io.dataline.scheduler.SchedulerPersistence;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.stream.Collectors;
import org.apache.commons.io.input.ReversedLinesFileReader;

public class JobHistoryHandler {
  private static final int LOG_TAIL_SIZE = 10;
  private final SchedulerPersistence schedulerPersistence;

  public JobHistoryHandler(SchedulerPersistence schedulerPersistence) {
    this.schedulerPersistence = schedulerPersistence;
  }

  public JobReadList listJobsFor(ConnectionIdRequestBody connectionIdRequestBody) {
    try {
      String connectionId = connectionIdRequestBody.getConnectionId().toString();

      // todo: use functions for scope scoping
      List<JobRead> jobReads =
          schedulerPersistence.listJobs("connection:" + connectionId).stream()
              .map(JobHistoryHandler::getJobRead)
              .collect(Collectors.toList());

      JobReadList jobReadList = new JobReadList();
      jobReadList.setJobs(jobReads);

      return jobReadList;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  public JobInfoRead getJobInfo(JobIdRequestBody jobIdRequestBody) {
    try {
      Job job = schedulerPersistence.getJob(jobIdRequestBody.getId());

      LogRead logRead = new LogRead();
      logRead.setStdout(getTail(LOG_TAIL_SIZE, job.getStdoutPath()));
      logRead.setStderr(getTail(LOG_TAIL_SIZE, job.getStderrPath()));

      JobInfoRead jobInfo = new JobInfoRead();
      jobInfo.setJob(getJobRead(job));
      jobInfo.setLogs(logRead);

      return jobInfo;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private static List<String> getTail(int numLines, String path) {
    try {
      File file = new File(path);
      ReversedLinesFileReader fileReader = new ReversedLinesFileReader(file, Charsets.UTF_8);
      List<String> lines = new ArrayList<>();

      String line;
      while ((line = fileReader.readLine()) != null && lines.size() < numLines) {
        lines.add(line);
      }

      Collections.reverse(lines);

      return lines;
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  // todo: add test assertion for completeness
  private static JobRead.StatusEnum convertStatus(JobStatus jobStatus) {
    switch (jobStatus) {
      case PENDING:
        return JobRead.StatusEnum.PENDING;
      case RUNNING:
        return JobRead.StatusEnum.RUNNING;
      case FAILED:
        return JobRead.StatusEnum.FAILED;
      case COMPLETED:
        return JobRead.StatusEnum.COMPLETED;
      case CANCELLED:
        return JobRead.StatusEnum.CANCELLED;
      default:
        throw new IllegalStateException("Unexpected value: " + jobStatus);
    }
  }

  private static JobRead getJobRead(Job job) {
    JobRead jobRead = new JobRead();

    jobRead.setId(job.getId());
    jobRead.setScope(job.getScope());
    jobRead.setCreatedAt(job.getCreatedAt());

    if (job.getStartedAt().isPresent()) {
      jobRead.setStartedAt(job.getStartedAt().get());
    }

    jobRead.setUpdatedAt(job.getUpdatedAt());
    jobRead.setStatus(convertStatus(job.getStatus()));

    return jobRead;
  }
}
