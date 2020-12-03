package io.airbyte.server.converters;

import io.airbyte.api.model.AttemptInfoRead;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.AttemptStatus;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobIdRequestBody;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobStatus;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.LogRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.IOs;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.ScopeHelper;
import io.airbyte.server.handlers.JobHistoryHandler;
import java.io.IOException;
import java.util.stream.Collectors;

public class JobConverter {
  private static final int LOG_TAIL_SIZE = 1000;
  public static JobInfoRead  getJobInfo(Job job) throws IOException {
    return new JobInfoRead()
        .job(getJobWithAttemptsRead(job).getJob())
        .attempts(job.getAttempts().stream().map(JobConverter::getAttemptInfoRead).collect(Collectors.toList()));
  }

  public static JobWithAttemptsRead getJobWithAttemptsRead(Job job) {
    final String configId = ScopeHelper.getConfigId(job.getScope());
    final JobConfigType configType = Enums.convertTo(job.getConfig().getConfigType(), JobConfigType.class);

    return new JobWithAttemptsRead()
        .job(new JobRead()
            .id(job.getId())
            .configId(configId)
            .configType(configType)
            .createdAt(job.getCreatedAtInSecond())
            .updatedAt(job.getUpdatedAtInSecond())
            .status(Enums.convertTo(job.getStatus(), JobStatus.class)))
        .attempts(job.getAttempts().stream().map(JobConverter::getAttemptRead).collect(Collectors.toList()));
  }

  public static AttemptInfoRead getAttemptInfoRead(Attempt attempt) {
    return new AttemptInfoRead()
        .attempt(getAttemptRead(attempt))
        .logs(getLogRead(attempt));
  }

  public static AttemptRead getAttemptRead(Attempt attempt) {
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

  public static LogRead getLogRead(Attempt attempt) {
    try {
      return new LogRead().logLines(IOs.getTail(LOG_TAIL_SIZE, attempt.getLogPath()));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

}
