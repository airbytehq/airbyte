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

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.time.Duration;
import java.time.Instant;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerJobClient implements SchedulerJobClient {

  private static final Duration REQUEST_TIMEOUT = Duration.ofMinutes(30);
  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerJobClient.class);

  private final JobPersistence jobPersistence;
  private final JobCreator jobCreator;

  public DefaultSchedulerJobClient(JobPersistence jobPersistence, JobCreator jobCreator) {
    this.jobPersistence = jobPersistence;
    this.jobCreator = jobCreator;
  }

  @Override
  public Job createSourceCheckConnectionJob(SourceConnection source, String dockerImage) throws IOException {
    final long jobId = jobCreator.createSourceCheckConnectionJob(source, dockerImage);
    return waitUntilJobIsTerminalOrTimeout(jobId);
  }

  @Override
  public Job createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImage) throws IOException {
    final long jobId = jobCreator.createDestinationCheckConnectionJob(destination, dockerImage);
    return waitUntilJobIsTerminalOrTimeout(jobId);
  }

  @Override
  public Job createDiscoverSchemaJob(SourceConnection source, String dockerImage) throws IOException {
    final long jobId = jobCreator.createDiscoverSchemaJob(source, dockerImage);
    return waitUntilJobIsTerminalOrTimeout(jobId);
  }

  @Override
  public Job createGetSpecJob(String dockerImage) throws IOException {
    final long jobId = jobCreator.createGetSpecJob(dockerImage);
    return waitUntilJobIsTerminalOrTimeout(jobId);
  }

  @Override
  public Job createOrGetActiveSyncJob(SourceConnection source,
                                      DestinationConnection destination,
                                      StandardSync standardSync,
                                      String sourceDockerImage,
                                      String destinationDockerImage)
      throws IOException {
    final Optional<Long> jobIdOptional = jobCreator.createSyncJob(
        source,
        destination,
        standardSync,
        sourceDockerImage,
        destinationDockerImage);

    long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return jobPersistence.getJob(jobId);
  }

  @Override
  public Job createOrGetActiveResetConnectionJob(DestinationConnection destination,
                                                 StandardSync standardSync,
                                                 String destinationDockerImage)
      throws IOException {
    final Optional<Long> jobIdOptional = jobCreator.createResetConnectionJob(destination, standardSync, destinationDockerImage);

    long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return waitUntilJobIsTerminalOrTimeout(jobId);
  }

  @VisibleForTesting
  Job waitUntilJobIsTerminalOrTimeout(final long jobId) throws IOException {
    Instant timeoutInstant = Instant.now().plus(REQUEST_TIMEOUT);
    LOGGER.info("Waiting for job id: " + jobId);
    while (Instant.now().isBefore(timeoutInstant)) {
      final Job job = jobPersistence.getJob(jobId);

      if (JobStatus.TERMINAL_STATUSES.contains(job.getStatus())) {
        return job;
      }

      try {
        Thread.sleep(1000);
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }

    throw new RuntimeException("Job " + jobId + "  did not complete.");
  }

}
