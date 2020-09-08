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
import io.dataline.api.model.JobConfigType;
import io.dataline.api.model.JobIdRequestBody;
import io.dataline.api.model.JobInfoRead;
import io.dataline.api.model.JobListRequestBody;
import io.dataline.api.model.JobRead;
import io.dataline.api.model.JobReadList;
import io.dataline.api.model.LogRead;
import io.dataline.commons.enums.Enums;
import io.dataline.config.JobConfig;
import io.dataline.scheduler.Job;
import io.dataline.scheduler.ScopeHelper;
import io.dataline.scheduler.persistence.SchedulerPersistence;
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

  public JobReadList listJobsFor(JobListRequestBody request) throws IOException {
    JobConfig.ConfigType configType = Enums.convertTo(request.getConfigType(), JobConfig.ConfigType.class);
    String configId = request.getConfigId();

    // todo: use functions for scope scoping
    List<JobRead> jobReads = schedulerPersistence.listJobs(configType, configId)
        .stream()
        .map(JobHistoryHandler::getJobRead)
        .collect(Collectors.toList());

    return new JobReadList().jobs(jobReads);
  }

  public JobInfoRead getJobInfo(JobIdRequestBody jobIdRequestBody) throws IOException {
    Job job = schedulerPersistence.getJob(jobIdRequestBody.getId());

    LogRead logRead = new LogRead()
        .stdout(getTail(LOG_TAIL_SIZE, job.getStdoutPath()))
        .stderr(getTail(LOG_TAIL_SIZE, job.getStderrPath()));

    return new JobInfoRead()
        .job(getJobRead(job))
        .logs(logRead);
  }

  private static List<String> getTail(int numLines, String path) throws IOException {
    File file = new File(path);
    try (ReversedLinesFileReader fileReader = new ReversedLinesFileReader(file, Charsets.UTF_8)) {
      List<String> lines = new ArrayList<>();

      String line;
      while ((line = fileReader.readLine()) != null && lines.size() < numLines) {
        lines.add(line);
      }

      Collections.reverse(lines);

      return lines;
    }
  }

  private static JobRead getJobRead(Job job) {
    String configId = ScopeHelper.getConfigId(job.getScope());
    JobConfigType configType = Enums.convertTo(job.getConfig().getConfigType(), JobConfigType.class);

    JobRead jobRead = new JobRead();

    jobRead.setId(job.getId());
    jobRead.setConfigId(configId);
    jobRead.setConfigType(configType);
    jobRead.setCreatedAt(job.getCreatedAt());

    if (job.getStartedAt().isPresent()) {
      jobRead.setStartedAt(job.getStartedAt().get());
    }

    jobRead.setUpdatedAt(job.getUpdatedAt());
    jobRead.setStatus(Enums.convertTo(job.getStatus(), JobRead.StatusEnum.class));

    return jobRead;
  }

}
