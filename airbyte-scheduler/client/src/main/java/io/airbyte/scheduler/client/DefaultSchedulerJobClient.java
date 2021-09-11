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

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerJobClient implements SchedulerJobClient {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerJobClient.class);

  private final JobPersistence jobPersistence;
  private final JobCreator jobCreator;

  public DefaultSchedulerJobClient(JobPersistence jobPersistence, JobCreator jobCreator) {
    this.jobPersistence = jobPersistence;
    this.jobCreator = jobCreator;
  }

  @Override
  public Job createOrGetActiveSyncJob(SourceConnection source,
                                      DestinationConnection destination,
                                      StandardSync standardSync,
                                      String sourceDockerImage,
                                      String destinationDockerImage,
                                      List<StandardSyncOperation> standardSyncOperations)
      throws IOException {
    final Optional<Long> jobIdOptional = jobCreator.createSyncJob(
        source,
        destination,
        standardSync,
        sourceDockerImage,
        destinationDockerImage,
        standardSyncOperations);

    long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return jobPersistence.getJob(jobId);
  }

  @Override
  public Job createOrGetActiveResetConnectionJob(DestinationConnection destination,
                                                 StandardSync standardSync,
                                                 String destinationDockerImage,
                                                 List<StandardSyncOperation> standardSyncOperations)
      throws IOException {
    final Optional<Long> jobIdOptional =
        jobCreator.createResetConnectionJob(destination, standardSync, destinationDockerImage, standardSyncOperations);

    long jobId = jobIdOptional.isEmpty()
        ? jobPersistence.getLastReplicationJob(standardSync.getConnectionId()).orElseThrow(() -> new RuntimeException("No job available")).getId()
        : jobIdOptional.get();

    return jobPersistence.getJob(jobId);
  }

}
