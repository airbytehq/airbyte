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

package io.airbyte.scheduler.persistence;

import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.JobConfig;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardSync;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface SchedulerPersistence {

  long createSourceCheckConnectionJob(SourceConnectionImplementation sourceImplementation, String dockerImage) throws IOException;

  long createDestinationCheckConnectionJob(DestinationConnectionImplementation destinationImplementation, String dockerImage) throws IOException;

  long createDiscoverSchemaJob(SourceConnectionImplementation sourceImplementation, String dockerImage) throws IOException;

  long createGetSpecJob(String integrationImage) throws IOException;

  long createSyncJob(SourceConnectionImplementation sourceImplementation,
                     DestinationConnectionImplementation destinationImplementation,
                     StandardSync standardSync,
                     String sourceDockerImage,
                     String destinationDockerImage)
      throws IOException;

  Job getJob(long jobId) throws IOException;

  void updateStatus(long jobId, JobStatus status) throws IOException;

  void updateLogPath(long jobId, Path logPath) throws IOException;

  void incrementAttempts(long jobId) throws IOException;

  <T> void writeOutput(long jobId, T output) throws IOException;

  /**
   * @param configType - type of config, e.g. sync
   * @param configId - id of that config
   * @return lists job in descending order by created_at
   * @throws IOException - what you do when you IO
   */
  List<Job> listJobs(JobConfig.ConfigType configType, String configId) throws IOException;

  List<Job> listJobsWithStatus(JobConfig.ConfigType configType, JobStatus status) throws IOException;

  Optional<Job> getLastSyncJob(UUID connectionId) throws IOException;

  Optional<Job> getOldestPendingJob() throws IOException;

}
