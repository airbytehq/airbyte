/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import com.google.common.base.Preconditions;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobListRequestBody;
import io.airbyte.api.model.JobReadList;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.JobConverter;
import java.io.IOException;
import java.util.List;
import java.util.Set;
import java.util.stream.Collectors;

public class JobHistoryHandler {

  public static final int DEFAULT_PAGE_SIZE = 200;
  private final JobPersistence jobPersistence;

  public JobHistoryHandler(JobPersistence jobPersistence) {
    this.jobPersistence = jobPersistence;
  }

  @SuppressWarnings("UnstableApiUsage")
  public JobReadList listJobsFor(JobListRequestBody request) throws IOException {
    Preconditions.checkNotNull(request.getConfigTypes(), "configType cannot be null.");
    Preconditions.checkState(!request.getConfigTypes().isEmpty(), "Must include at least one configType.");

    final Set<ConfigType> configTypes = request.getConfigTypes()
        .stream()
        .map(type -> Enums.convertTo(type, JobConfig.ConfigType.class))
        .collect(Collectors.toSet());
    final String configId = request.getConfigId();

    final List<JobWithAttemptsRead> jobReads = jobPersistence.listJobs(configTypes,
        configId,
        (request.getPagination() != null && request.getPagination().getPageSize() != null) ? request.getPagination().getPageSize()
            : DEFAULT_PAGE_SIZE,
        (request.getPagination() != null && request.getPagination().getRowOffset() != null) ? request.getPagination().getRowOffset() : 0)
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
