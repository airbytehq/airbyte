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
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.IOs;
import io.airbyte.scheduler.client.JobMetadatas.AttemptMetadata;
import io.airbyte.scheduler.client.JobMetadatas.JobMetadata;
import java.io.IOException;
import java.util.stream.Collectors;

public class JobMetadataConverter {

  private static final int LOG_TAIL_SIZE = 1000000;

  public static JobInfoRead getJobInfoRead(JobMetadata job) {
    return new JobInfoRead()
        .job(getJobWithAttemptsRead(job).getJob())
        .attempts(job.getAttempts().stream().map(JobMetadataConverter::getAttemptInfoRead).collect(Collectors.toList()));
  }

  public static JobWithAttemptsRead getJobWithAttemptsRead(JobMetadata job) {
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
        .attempts(job.getAttempts().stream().map(JobMetadataConverter::getAttemptRead).collect(Collectors.toList()));
  }

  public static AttemptInfoRead getAttemptInfoRead(AttemptMetadata attempt) {
    return new AttemptInfoRead()
        .attempt(getAttemptRead(attempt))
        .logs(getLogRead(attempt));
  }

  public static AttemptRead getAttemptRead(AttemptMetadata attempt) {
    return new AttemptRead()
        .id(attempt.getId())
        .status(Enums.convertTo(attempt.getStatus(), AttemptStatus.class))
        // .bytesSynced(attempt.getOutput()
        // .map(JobOutput::getSync)
        // .map(StandardSyncOutput::getStandardSyncSummary)
        // .map(StandardSyncSummary::getBytesSynced)
        // .orElse(null))
        // .recordsSynced(attempt.getOutput()
        // .map(JobOutput::getSync)
        // .map(StandardSyncOutput::getStandardSyncSummary)
        // .map(StandardSyncSummary::getRecordsSynced)
        // .orElse(null))
        .createdAt(attempt.getCreatedAtInSecond())
        .updatedAt(attempt.getUpdatedAtInSecond())
        .endedAt(attempt.getEndedAtInSecond().orElse(null));
  }

  public static LogRead getLogRead(AttemptMetadata attempt) {
    try {
      return new LogRead().logLines(IOs.getTail(LOG_TAIL_SIZE, attempt.getLogPath()));
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

}
