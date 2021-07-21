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

package io.airbyte.server.helpers;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.util.concurrent.UncheckedExecutionException;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.FileSystemConfigPersistence;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.UUID;
import java.util.concurrent.ExecutionException;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WorkspaceHelperTest {

  Path tmpDir;
  ConfigRepository configRepository;
  JobPersistence jobPersistence;
  WorkspaceHelper workspaceHelper;

  @BeforeEach
  public void setup() throws IOException {
    tmpDir = Files.createTempDirectory("workspace_helper_test_" + RandomStringUtils.randomAlphabetic(5));

    configRepository = new ConfigRepository(new FileSystemConfigPersistence(tmpDir));
    jobPersistence = mock(JobPersistence.class);

    workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);
  }

  @Test
  public void testObjectsThatDoNotExist() {
    assertThrows(ExecutionException.class, () -> workspaceHelper.getWorkspaceForSourceId(UUID.randomUUID()));
    assertThrows(ExecutionException.class, () -> workspaceHelper.getWorkspaceForDestinationId(UUID.randomUUID()));
    assertThrows(ExecutionException.class, () -> workspaceHelper.getWorkspaceForConnectionId(UUID.randomUUID()));
    assertThrows(ExecutionException.class, () -> workspaceHelper.getWorkspaceForConnection(UUID.randomUUID(), UUID.randomUUID()));
    assertThrows(UncheckedExecutionException.class, () -> workspaceHelper.getWorkspaceForJobId(0L));
    // todo: add operationId check
  }

  @Test
  public void testSource() throws IOException, ExecutionException, JsonValidationException {
    UUID source = UUID.randomUUID();
    UUID workspace = UUID.randomUUID();

    UUID sourceDefinition = UUID.randomUUID();
    configRepository.writeStandardSource(new StandardSourceDefinition().withSourceDefinitionId(sourceDefinition));

    SourceConnection sourceConnection = new SourceConnection()
        .withSourceId(source)
        .withSourceDefinitionId(sourceDefinition)
        .withWorkspaceId(workspace)
        .withConfiguration(Jsons.deserialize("{}"))
        .withName("source")
        .withTombstone(false);

    configRepository.writeSourceConnection(sourceConnection);
    UUID retrievedWorkspace = workspaceHelper.getWorkspaceForSourceId(source);

    assertEquals(workspace, retrievedWorkspace);

    // check that caching is working
    configRepository.writeSourceConnection(sourceConnection.withWorkspaceId(UUID.randomUUID()));
    UUID retrievedWorkspaceAfterUpdate = workspaceHelper.getWorkspaceForSourceId(source);
    assertEquals(workspace, retrievedWorkspaceAfterUpdate);
  }

  @Test
  public void testDestination() throws IOException, ExecutionException, JsonValidationException {
    UUID destination = UUID.randomUUID();
    UUID workspace = UUID.randomUUID();

    UUID destinationDefinition = UUID.randomUUID();
    configRepository.writeStandardDestinationDefinition(new StandardDestinationDefinition().withDestinationDefinitionId(destinationDefinition));

    DestinationConnection destinationConnection = new DestinationConnection()
        .withDestinationId(destination)
        .withDestinationDefinitionId(destinationDefinition)
        .withWorkspaceId(workspace)
        .withConfiguration(Jsons.deserialize("{}"))
        .withName("dest")
        .withTombstone(false);

    configRepository.writeDestinationConnection(destinationConnection);
    UUID retrievedWorkspace = workspaceHelper.getWorkspaceForDestinationId(destination);

    assertEquals(workspace, retrievedWorkspace);

    // check that caching is working
    configRepository.writeDestinationConnection(destinationConnection.withWorkspaceId(UUID.randomUUID()));
    UUID retrievedWorkspaceAfterUpdate = workspaceHelper.getWorkspaceForDestinationId(destination);
    assertEquals(workspace, retrievedWorkspaceAfterUpdate);
  }

  @Test
  public void testConnectionAndJobs() throws IOException, ExecutionException, JsonValidationException {
    UUID workspace = UUID.randomUUID();

    // set up source
    UUID source = UUID.randomUUID();

    UUID sourceDefinition = UUID.randomUUID();
    configRepository.writeStandardSource(new StandardSourceDefinition().withSourceDefinitionId(sourceDefinition));

    SourceConnection sourceConnection = new SourceConnection()
        .withSourceId(source)
        .withSourceDefinitionId(sourceDefinition)
        .withWorkspaceId(workspace)
        .withConfiguration(Jsons.deserialize("{}"))
        .withName("source")
        .withTombstone(false);

    configRepository.writeSourceConnection(sourceConnection);

    // set up destination
    UUID destination = UUID.randomUUID();

    UUID destinationDefinition = UUID.randomUUID();
    configRepository.writeStandardDestinationDefinition(new StandardDestinationDefinition().withDestinationDefinitionId(destinationDefinition));

    DestinationConnection destinationConnection = new DestinationConnection()
        .withDestinationId(destination)
        .withDestinationDefinitionId(destinationDefinition)
        .withWorkspaceId(workspace)
        .withConfiguration(Jsons.deserialize("{}"))
        .withName("dest")
        .withTombstone(false);

    configRepository.writeDestinationConnection(destinationConnection);

    // set up connection
    UUID connection = UUID.randomUUID();
    configRepository.writeStandardSync(new StandardSync().withManual(true).withConnectionId(connection).withSourceId(source)
        .withDestinationId(destination).withCatalog(new ConfiguredAirbyteCatalog().withStreams(new ArrayList<>())));

    // test retrieving by connection id
    UUID retrievedWorkspace = workspaceHelper.getWorkspaceForConnectionId(connection);
    assertEquals(workspace, retrievedWorkspace);

    // test retrieving by source and destination ids
    UUID retrievedWorkspaceBySourceAndDestination = workspaceHelper.getWorkspaceForConnectionId(connection);
    assertEquals(workspace, retrievedWorkspaceBySourceAndDestination);

    // check that caching is working
    UUID newWorkspace = UUID.randomUUID();
    configRepository.writeSourceConnection(sourceConnection.withWorkspaceId(newWorkspace));
    configRepository.writeDestinationConnection(destinationConnection.withWorkspaceId(newWorkspace));
    UUID retrievedWorkspaceAfterUpdate = workspaceHelper.getWorkspaceForDestinationId(destination);
    assertEquals(workspace, retrievedWorkspaceAfterUpdate);

    // test jobs
    long jobId = 123;
    Job job = new Job(
        jobId,
        JobConfig.ConfigType.SYNC,
        connection.toString(),
        new JobConfig().withConfigType(JobConfig.ConfigType.SYNC).withSync(new JobSyncConfig()),
        new ArrayList<>(),
        JobStatus.PENDING,
        System.currentTimeMillis(),
        System.currentTimeMillis(),
        System.currentTimeMillis());
    when(jobPersistence.getJob(jobId)).thenReturn(job);

    UUID jobWorkspace = workspaceHelper.getWorkspaceForJobId(jobId);
    assertEquals(workspace, jobWorkspace);
  }

}
