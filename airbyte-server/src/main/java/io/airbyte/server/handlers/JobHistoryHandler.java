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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.LogRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.IOs;
import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.ScopeHelper;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Collectors;

public class JobHistoryHandler {

  private static final int LOG_TAIL_SIZE = 100;
  private final JobPersistence jobPersistence;

  public JobHistoryHandler(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  public JobReadList listJobsFor(JobListRequestBody request) throws IOException {
    final JobConfig.ConfigType configType = Enums.convertTo(request.getConfigType(), JobConfig.ConfigType.class);
    final String configId = request.getConfigId();

    final List<JobRead> jobReads = jobPersistence.listJobs(configType, configId)
        .stream()
        .map(JobHistoryHandler::getJobRead)
        .collect(Collectors.toList());

    return new JobReadList().jobs(jobReads);
  }

  public JobInfoRead getJobInfo(JobIdRequestBody jobIdRequestBody) throws IOException {
    final Job job = jobPersistence.getJob(jobIdRequestBody.getId());

    return new JobInfoRead()
        .job(getJobRead(job))
        .logs(job.getAttempts()
            .stream()
            .sorted(Comparator.comparingLong(Attempt::getCreatedAtInSecond).reversed())
            .map(JobHistoryHandler::getLogRead)
            .findFirst()
            .orElse(null));
  }

  private static LogRead getLogRead(Attempt attempt) {
    try {
      return new LogRead().logLines(IOs.getTail(LOG_TAIL_SIZE, attempt.getLogPath()));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  @VisibleForTesting
  protected static JobRead getJobRead(Job job) {
    final String configId = ScopeHelper.getConfigId(job.getScope());
    final JobConfigType configType = Enums.convertTo(job.getConfig().getConfigType(), JobConfigType.class);

    return new JobRead()
        .id(job.getId())
        .configId(configId)
        .configType(configType)
        .createdAt(job.getCreatedAtInSecond())
        .updatedAt(job.getUpdatedAtInSecond())
        .status(toApiJobStatus(job.getStatus()));
  }

  // todo (cgardens) - temporary to maintain backwards compatibility. will be removed in the next PR.
  private static JobStatus toApiJobStatus(io.airbyte.scheduler.JobStatus jobStatus) {
    switch (jobStatus) {
      case INCOMPLETE -> {
        return JobStatus.FAILED;
      }
      case FAILED, PENDING, RUNNING, CANCELLED -> {
        return Enums.convertTo(jobStatus, JobStatus.class);
      }
      case SUCCEEDED -> {
        return JobStatus.COMPLETED;
      }
      default -> throw new IllegalStateException("Cannot convert job status to api job status: " + jobStatus);
    }
  }

}
