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

import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobConfig;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.JobConverter;
import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

public class JobHistoryHandler {

  private final JobPersistence jobPersistence;

  public JobHistoryHandler(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  public JobReadList listJobsFor(JobListRequestBody request) throws IOException {
    final JobConfig.ConfigType configType = Enums.convertTo(request.getConfigType(), JobConfig.ConfigType.class);
    final String configId = request.getConfigId();

    final List<JobWithAttemptsRead> jobReads = jobPersistence.listJobs(configType, configId)
        .stream()
        .map(JobConverter::getJobWithAttemptsRead)
        .collect(Collectors.toList());

    return new JobReadList().jobs(jobReads);
  }

  public JobInfoRead getJobInfo(JobIdRequestBody jobIdRequestBody) throws IOException {
    final Job job = jobPersistence.getJob(jobIdRequestBody.getId());

    return JobConverter.getJobInfoRead(job);
  }

}
