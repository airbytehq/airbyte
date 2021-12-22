/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import io.airbyte.api.model.AttemptInfoRead;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.AttemptStatus;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.LogRead;
import io.airbyte.api.model.SynchronousJobRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.client.SynchronousJobMetadata;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.Job;
import java.io.IOException;
import java.nio.file.Path;
import java.util.stream.Collectors;

public class JobConverter {

  private static final int LOG_TAIL_SIZE = 1000000;

  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;

  public JobConverter(final WorkerEnvironment workerEnvironment, final LogConfigs logConfigs) {
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
  }

  public JobInfoRead getJobInfoRead(final Job job) {
    return new JobInfoRead()
        .job(getJobWithAttemptsRead(job).getJob())
        .attempts(job.getAttempts().stream().map(attempt -> getAttemptInfoRead(attempt)).collect(Collectors.toList()));
  }

  public static JobWithAttemptsRead getJobWithAttemptsRead(final Job job) {
    final String configId = job.getScope();
    final JobConfigType configType = Enums.convertTo(job.getConfigType(), JobConfigType.class);

    return new JobWithAttemptsRead()
        .job(new JobRead()
            .id(job.getId())
            .configId(configId)
            .configType(configType)
            .createdAt(job.getCreatedAtInSecond())
            .updatedAt(job.getUpdatedAtInSecond())
            .status(Enums.convertTo(job.getStatus(), JobStatus.class)))
        .attempts(job.getAttempts().stream().map(attempt -> getAttemptRead(attempt)).collect(Collectors.toList()));
  }

  public AttemptInfoRead getAttemptInfoRead(final Attempt attempt) {
    return new AttemptInfoRead()
        .attempt(getAttemptRead(attempt))
        .logs(getLogRead(attempt.getLogPath()));
  }

  public static AttemptRead getAttemptRead(final Attempt attempt) {
    return new AttemptRead()
        .id(attempt.getId())
        .status(Enums.convertTo(attempt.getStatus(), AttemptStatus.class))
        .bytesSynced(attempt.getOutput()
            .map(JobOutput::getSync)
            .map(StandardSyncOutput::getStandardSyncSummary)
            .map(StandardSyncSummary::getBytesSynced)
            .orElse(null))
        .recordsSynced(attempt.getOutput()
            .map(JobOutput::getSync)
            .map(StandardSyncOutput::getStandardSyncSummary)
            .map(StandardSyncSummary::getRecordsSynced)
            .orElse(null))
        .createdAt(attempt.getCreatedAtInSecond())
        .updatedAt(attempt.getUpdatedAtInSecond())
        .endedAt(attempt.getEndedAtInSecond().orElse(null));
  }

  public LogRead getLogRead(final Path logPath) {
    try {
      return new LogRead().logLines(LogClientSingleton.getInstance().getJobLogFile(workerEnvironment, logConfigs, logPath));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  public SynchronousJobRead getSynchronousJobRead(final SynchronousResponse<?> response) {
    return getSynchronousJobRead(response.getMetadata());
  }

  public SynchronousJobRead getSynchronousJobRead(final SynchronousJobMetadata metadata) {
    final JobConfigType configType = Enums.convertTo(metadata.getConfigType(), JobConfigType.class);

    return new SynchronousJobRead()
        .id(metadata.getId())
        .configType(configType)
        .configId(String.valueOf(metadata.getConfigId()))
        .createdAt(metadata.getCreatedAt())
        .endedAt(metadata.getEndedAt())
        .succeeded(metadata.isSucceeded())
        .logs(getLogRead(metadata.getLogPath()));
  }

}
