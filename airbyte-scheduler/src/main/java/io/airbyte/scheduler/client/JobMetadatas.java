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

package io.airbyte.scheduler.client;

import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.AttemptStatus;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import java.nio.file.Path;
import java.util.List;
import java.util.stream.Collectors;

public class JobMetadatas {

  public static class JobMetadata {

    private final long id;
    private final ConfigType configType;
    private final String scope;
    private final JobStatus status;

    private final Long startedAt;
    private final long createdAt;
    private final long updatedAt;

    private final List<AttemptMetadata> attempts;

    public JobMetadata(long id,
                       ConfigType configType,
                       String scope,
                       JobStatus status,
                       Long startedAt,
                       long createdAt,
                       long updatedAt,
                       List<AttemptMetadata> attempts) {
      this.id = id;
      this.configType = configType;
      this.scope = scope;
      this.status = status;
      this.startedAt = startedAt;
      this.createdAt = createdAt;
      this.updatedAt = updatedAt;
      this.attempts = attempts;
    }

    public long getId() {
      return id;
    }

    public ConfigType getConfigType() {
      return configType;
    }

    public String getScope() {
      return scope;
    }

    public JobStatus getStatus() {
      return status;
    }

    public Long getStartedAt() {
      return startedAt;
    }

    public long getCreatedAt() {
      return createdAt;
    }

    public long getUpdatedAt() {
      return updatedAt;
    }

    public List<AttemptMetadata> getAttempts() {
      return attempts;
    }

    @Override
    public String toString() {
      return "JobMetadata{" +
          "id=" + id +
          ", configType=" + configType +
          ", scope='" + scope + '\'' +
          ", status=" + status +
          ", startedAt=" + startedAt +
          ", createdAt=" + createdAt +
          ", updatedAt=" + updatedAt +
          ", attempts=" + attempts +
          '}';
    }

  }

  public static class AttemptMetadata {

    private final long id;
    private final long jobId;
    private final AttemptStatus status;
    private final Path logPath;

    private final long updatedAtInSecond;
    private final long createdAtInSecond;
    private final Long endedAtInSecond;

    public AttemptMetadata(long id,
                           long jobId,
                           AttemptStatus status,
                           Path logPath,
                           long updatedAtInSecond,
                           long createdAtInSecond,
                           Long endedAtInSecond) {
      this.id = id;
      this.jobId = jobId;
      this.status = status;
      this.logPath = logPath;
      this.updatedAtInSecond = updatedAtInSecond;
      this.createdAtInSecond = createdAtInSecond;
      this.endedAtInSecond = endedAtInSecond;
    }

    public long getId() {
      return id;
    }

    public long getJobId() {
      return jobId;
    }

    public AttemptStatus getStatus() {
      return status;
    }

    public Path getLogPath() {
      return logPath;
    }

    public long getUpdatedAtInSecond() {
      return updatedAtInSecond;
    }

    public long getCreatedAtInSecond() {
      return createdAtInSecond;
    }

    public Long getEndedAtInSecond() {
      return endedAtInSecond;
    }

    @Override
    public String toString() {
      return "AttemptMetadata{" +
          "id=" + id +
          ", jobId=" + jobId +
          ", status=" + status +
          ", logPath=" + logPath +
          ", updatedAtInSecond=" + updatedAtInSecond +
          ", createdAtInSecond=" + createdAtInSecond +
          ", endedAtInSecond=" + endedAtInSecond +
          '}';
    }

  }

  public static JobMetadata fromJob(Job job) {
    return new JobMetadata(
        job.getId(),
        job.getConfigType(),
        job.getScope(),
        job.getStatus(),
        job.getStartedAtInSecond().orElse(null),
        job.getCreatedAtInSecond(),
        job.getUpdatedAtInSecond(),
        job.getAttempts().stream().map(JobMetadatas::fromAttempt).collect(Collectors.toList()));
  }

  public static AttemptMetadata fromAttempt(Attempt attempt) {
    return new AttemptMetadata(
        attempt.getId(),
        attempt.getJobId(),
        attempt.getStatus(),
        attempt.getLogPath(),
        attempt.getUpdatedAtInSecond(),
        attempt.getCreatedAtInSecond(),
        attempt.getEndedAtInSecond().orElse(null));
  }

}
