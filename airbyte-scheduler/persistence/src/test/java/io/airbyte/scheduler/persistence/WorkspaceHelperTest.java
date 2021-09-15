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

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.FileSystemConfigPersistence;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.UUID;
import org.apache.commons.lang3.RandomStringUtils;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class WorkspaceHelperTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID SOURCE_DEFINITION_ID = UUID.randomUUID();
  private static final UUID SOURCE_ID = UUID.randomUUID();
  private static final UUID DEST_DEFINITION_ID = UUID.randomUUID();
  private static final UUID DEST_ID = UUID.randomUUID();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final UUID OPERATION_ID = UUID.randomUUID();
  private static final StandardSourceDefinition SOURCE_DEF = new StandardSourceDefinition().withSourceDefinitionId(SOURCE_DEFINITION_ID);
  private static final SourceConnection SOURCE = new SourceConnection()
      .withSourceId(SOURCE_ID)
      .withSourceDefinitionId(SOURCE_DEFINITION_ID)
      .withWorkspaceId(WORKSPACE_ID)
      .withConfiguration(Jsons.deserialize("{}"))
      .withName("source")
      .withTombstone(false);
  private static final StandardDestinationDefinition DEST_DEF = new StandardDestinationDefinition().withDestinationDefinitionId(DEST_DEFINITION_ID);
  private static final DestinationConnection DEST = new DestinationConnection()
      .withDestinationId(DEST_ID)
      .withDestinationDefinitionId(DEST_DEFINITION_ID)
      .withWorkspaceId(WORKSPACE_ID)
      .withConfiguration(Jsons.deserialize("{}"))
      .withName("dest")
      .withTombstone(false);
  private static final StandardSync CONNECTION = new StandardSync()
      .withConnectionId(CONNECTION_ID)
      .withSourceId(SOURCE_ID)
      .withDestinationId(DEST_ID).withCatalog(new ConfiguredAirbyteCatalog().withStreams(new ArrayList<>()))
      .withManual(true);
  private static final StandardSyncOperation OPERATION = new StandardSyncOperation()
      .withOperationId(OPERATION_ID)
      .withWorkspaceId(WORKSPACE_ID)
      .withName("the new normal")
      .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC))
      .withTombstone(false);

  Path tmpDir;
  ConfigRepository configRepository;
  JobPersistence jobPersistence;
  WorkspaceHelper workspaceHelper;
  ConnectorSpecification emptyConnectorSpec;

  @BeforeEach
  public void setup() throws IOException {
    tmpDir = Files.createTempDirectory("workspace_helper_test_" + RandomStringUtils.randomAlphabetic(5));

    configRepository = new ConfigRepository(new FileSystemConfigPersistence(tmpDir));
    jobPersistence = mock(JobPersistence.class);

    workspaceHelper = new WorkspaceHelper(configRepository, jobPersistence);

    emptyConnectorSpec = mock(ConnectorSpecification.class);
    when(emptyConnectorSpec.getConnectionSpecification()).thenReturn(Jsons.emptyObject());
  }

  @Test
  public void testMissingObjectsRuntimeException() {
    assertThrows(RuntimeException.class, () -> workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(UUID.randomUUID()));
    assertThrows(RuntimeException.class, () -> workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(UUID.randomUUID()));
    assertThrows(RuntimeException.class, () -> workspaceHelper.getWorkspaceForConnectionIdIgnoreExceptions(UUID.randomUUID()));
    assertThrows(RuntimeException.class, () -> workspaceHelper.getWorkspaceForConnectionIgnoreExceptions(UUID.randomUUID(), UUID.randomUUID()));
    assertThrows(RuntimeException.class, () -> workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(UUID.randomUUID()));
    assertThrows(RuntimeException.class, () -> workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(0L));
  }

  @Test
  public void testMissingObjectsProperException() {
    assertThrows(ConfigNotFoundException.class, () -> workspaceHelper.getWorkspaceForSourceId(UUID.randomUUID()));
    assertThrows(ConfigNotFoundException.class, () -> workspaceHelper.getWorkspaceForDestinationId(UUID.randomUUID()));
    assertThrows(ConfigNotFoundException.class, () -> workspaceHelper.getWorkspaceForConnectionId(UUID.randomUUID()));
    assertThrows(ConfigNotFoundException.class, () -> workspaceHelper.getWorkspaceForConnection(UUID.randomUUID(), UUID.randomUUID()));
    assertThrows(ConfigNotFoundException.class, () -> workspaceHelper.getWorkspaceForOperationId(UUID.randomUUID()));
    assertThrows(ConfigNotFoundException.class, () -> workspaceHelper.getWorkspaceForJobId(0L));
  }

  @Test
  public void testSource() throws IOException, JsonValidationException {
    configRepository.writeStandardSource(SOURCE_DEF);
    configRepository.writeSourceConnection(SOURCE, emptyConnectorSpec);

    final UUID retrievedWorkspace = workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(SOURCE_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspace);

    // check that caching is working
    configRepository.writeSourceConnection(Jsons.clone(SOURCE).withWorkspaceId(UUID.randomUUID()), emptyConnectorSpec);
    final UUID retrievedWorkspaceAfterUpdate = workspaceHelper.getWorkspaceForSourceIdIgnoreExceptions(SOURCE_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspaceAfterUpdate);
  }

  @Test
  public void testDestination() throws IOException, JsonValidationException {
    configRepository.writeStandardDestinationDefinition(DEST_DEF);
    configRepository.writeDestinationConnection(DEST, emptyConnectorSpec);

    final UUID retrievedWorkspace = workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(DEST_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspace);

    // check that caching is working
    configRepository.writeDestinationConnection(Jsons.clone(DEST).withWorkspaceId(UUID.randomUUID()), emptyConnectorSpec);
    final UUID retrievedWorkspaceAfterUpdate = workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(DEST_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspaceAfterUpdate);
  }

  @Test
  public void testConnection() throws IOException, JsonValidationException {
    configRepository.writeStandardSource(SOURCE_DEF);
    configRepository.writeSourceConnection(SOURCE, emptyConnectorSpec);
    configRepository.writeStandardDestinationDefinition(DEST_DEF);
    configRepository.writeDestinationConnection(DEST, emptyConnectorSpec);

    // set up connection
    configRepository.writeStandardSync(CONNECTION);

    // test retrieving by connection id
    final UUID retrievedWorkspace = workspaceHelper.getWorkspaceForConnectionIdIgnoreExceptions(CONNECTION_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspace);

    // test retrieving by source and destination ids
    final UUID retrievedWorkspaceBySourceAndDestination = workspaceHelper.getWorkspaceForConnectionIdIgnoreExceptions(CONNECTION_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspaceBySourceAndDestination);

    // check that caching is working
    final UUID newWorkspace = UUID.randomUUID();
    configRepository.writeSourceConnection(Jsons.clone(SOURCE).withWorkspaceId(newWorkspace), emptyConnectorSpec);
    configRepository.writeDestinationConnection(Jsons.clone(DEST).withWorkspaceId(newWorkspace), emptyConnectorSpec);
    final UUID retrievedWorkspaceAfterUpdate = workspaceHelper.getWorkspaceForDestinationIdIgnoreExceptions(DEST_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspaceAfterUpdate);
  }

  @Test
  public void testOperation() throws IOException, JsonValidationException {
    configRepository.writeStandardSyncOperation(OPERATION);

    // test retrieving by connection id
    final UUID retrievedWorkspace = workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(OPERATION_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspace);

    // check that caching is working
    configRepository.writeStandardSyncOperation(Jsons.clone(OPERATION).withWorkspaceId(UUID.randomUUID()));
    final UUID retrievedWorkspaceAfterUpdate = workspaceHelper.getWorkspaceForOperationIdIgnoreExceptions(OPERATION_ID);
    assertEquals(WORKSPACE_ID, retrievedWorkspaceAfterUpdate);
  }

  @Test
  public void testConnectionAndJobs() throws IOException, JsonValidationException {
    configRepository.writeStandardSource(SOURCE_DEF);
    configRepository.writeSourceConnection(SOURCE, emptyConnectorSpec);
    configRepository.writeStandardDestinationDefinition(DEST_DEF);
    configRepository.writeDestinationConnection(DEST, emptyConnectorSpec);
    configRepository.writeStandardSync(CONNECTION);

    // test jobs
    final long jobId = 123;
    final Job job = new Job(
        jobId,
        JobConfig.ConfigType.SYNC,
        CONNECTION_ID.toString(),
        new JobConfig().withConfigType(JobConfig.ConfigType.SYNC).withSync(new JobSyncConfig()),
        new ArrayList<>(),
        JobStatus.PENDING,
        System.currentTimeMillis(),
        System.currentTimeMillis(),
        System.currentTimeMillis());
    when(jobPersistence.getJob(jobId)).thenReturn(job);

    final UUID jobWorkspace = workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(jobId);
    assertEquals(WORKSPACE_ID, jobWorkspace);
  }

}
