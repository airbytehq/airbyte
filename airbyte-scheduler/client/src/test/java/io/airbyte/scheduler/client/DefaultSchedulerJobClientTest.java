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

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.spy;
import static org.mockito.Mockito.when;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class DefaultSchedulerJobClientTest {

  private static final long JOB_ID = 14L;
  private static final String DOCKER_IMAGE = "airbyte/stardock";

  private JobPersistence jobPersistence;
  private JobCreator jobCreator;
  private DefaultSchedulerJobClient client;
  private Job job;

  @BeforeEach
  void setup() {
    jobPersistence = mock(JobPersistence.class);
    jobCreator = mock(JobCreator.class);
    job = mock(Job.class);
    client = spy(new DefaultSchedulerJobClient(jobPersistence, jobCreator));
  }

  @Test
  void testCreateSyncJob() throws IOException {
    final SourceConnection source = mock(SourceConnection.class);
    final DestinationConnection destination = mock(DestinationConnection.class);
    final StandardSync standardSync = mock(StandardSync.class);
    final String destinationDockerImage = "airbyte/spaceport";
    when(jobCreator.createSyncJob(source, destination, standardSync, DOCKER_IMAGE, destinationDockerImage)).thenReturn(Optional.of(JOB_ID));
    when(jobPersistence.getJob(JOB_ID)).thenReturn(job);

    assertEquals(job, client.createOrGetActiveSyncJob(source, destination, standardSync, DOCKER_IMAGE, destinationDockerImage));
  }

  @Test
  void testCreateSyncJobAlreadyExist() throws IOException {
    final SourceConnection source = mock(SourceConnection.class);
    final DestinationConnection destination = mock(DestinationConnection.class);
    final StandardSync standardSync = mock(StandardSync.class);
    final UUID connectionUuid = UUID.randomUUID();
    when(standardSync.getConnectionId()).thenReturn(connectionUuid);
    final String destinationDockerImage = "airbyte/spaceport";
    when(jobCreator.createSyncJob(source, destination, standardSync, DOCKER_IMAGE, destinationDockerImage)).thenReturn(Optional.empty());

    final Job currentJob = mock(Job.class);
    when(currentJob.getId()).thenReturn(42L);
    when(jobPersistence.getLastReplicationJob(connectionUuid)).thenReturn(Optional.of(currentJob));
    when(jobPersistence.getJob(42L)).thenReturn(currentJob);

    assertEquals(currentJob, client.createOrGetActiveSyncJob(source, destination, standardSync, DOCKER_IMAGE, destinationDockerImage));
  }

  @Test
  void testCreateResetConnectionJob() throws IOException {
    final DestinationConnection destination = mock(DestinationConnection.class);
    final StandardSync standardSync = mock(StandardSync.class);
    final String destinationDockerImage = "airbyte/spaceport";
    when(jobCreator.createResetConnectionJob(destination, standardSync, destinationDockerImage)).thenReturn(Optional.of(JOB_ID));
    when(jobPersistence.getJob(JOB_ID)).thenReturn(job);

    assertEquals(job, client.createOrGetActiveResetConnectionJob(destination, standardSync, destinationDockerImage));
  }

  @Test
  void testCreateResetConnectionJobAlreadyExist() throws IOException {
    final DestinationConnection destination = mock(DestinationConnection.class);
    final StandardSync standardSync = mock(StandardSync.class);
    final UUID connectionUuid = UUID.randomUUID();
    when(standardSync.getConnectionId()).thenReturn(connectionUuid);
    final String destinationDockerImage = "airbyte/spaceport";
    when(jobCreator.createResetConnectionJob(destination, standardSync, destinationDockerImage)).thenReturn(Optional.empty());

    final Job currentJob = mock(Job.class);
    when(currentJob.getId()).thenReturn(42L);
    when(jobPersistence.getLastReplicationJob(connectionUuid)).thenReturn(Optional.of(currentJob));
    when(jobPersistence.getJob(42L)).thenReturn(currentJob);

    assertEquals(currentJob, client.createOrGetActiveResetConnectionJob(destination, standardSync, destinationDockerImage));
  }

}
