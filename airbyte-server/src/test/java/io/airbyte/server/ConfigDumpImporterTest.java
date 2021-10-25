/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.AdditionalMatchers.not;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.Status;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.converters.SpecFetcher;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConfigDumpImporterTest {

  public static final String TEST_VERSION = "0.0.1-test-version";

  private ConfigRepository configRepository;
  private JobPersistence jobPersistence;
  private WorkspaceHelper workspaceHelper;
  private ConfigDumpImporter configDumpImporter;
  private ConfigDumpExporter configDumpExporter;

  private UUID workspaceId;
  private StandardSourceDefinition standardSourceDefinition;
  private SourceConnection sourceConnection;
  private StandardDestinationDefinition standardDestinationDefinition;
  private DestinationConnection destinationConnection;
  private StandardSyncOperation operation;
  private StandardSync connection;
  private ConnectorSpecification emptyConnectorSpec;
  private SpecFetcher specFetcher;

  @BeforeEach
  public void setup() throws IOException, JsonValidationException, ConfigNotFoundException {
    configRepository = mock(ConfigRepository.class);
    jobPersistence = mock(JobPersistence.class);
    workspaceHelper = mock(WorkspaceHelper.class);

    specFetcher = mock(SpecFetcher.class);
    emptyConnectorSpec = mock(ConnectorSpecification.class);
    when(emptyConnectorSpec.getConnectionSpecification()).thenReturn(Jsons.emptyObject());
    when(specFetcher.getSpec(any(StandardSourceDefinition.class))).thenReturn(emptyConnectorSpec);
    when(specFetcher.getSpec(any(StandardDestinationDefinition.class))).thenReturn(emptyConnectorSpec);

    configDumpImporter =
        new ConfigDumpImporter(configRepository, jobPersistence, workspaceHelper, mock(JsonSchemaValidator.class), specFetcher, true);
    configDumpExporter = new ConfigDumpExporter(configRepository, jobPersistence, workspaceHelper);

    workspaceId = UUID.randomUUID();
    when(jobPersistence.getVersion()).thenReturn(Optional.of(TEST_VERSION));

    standardSourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withName("test-standard-source")
        .withDockerRepository("test")
        .withDocumentationUrl("http://doc")
        .withIcon("hello")
        .withDockerImageTag("dev")
        .withSpec(new ConnectorSpecification());
    sourceConnection = new SourceConnection()
        .withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .withConfiguration(Jsons.emptyObject())
        .withName("test-source")
        .withTombstone(false)
        .withWorkspaceId(workspaceId);
    when(configRepository.listStandardSourceDefinitions())
        .thenReturn(List.of(standardSourceDefinition));
    when(configRepository.getStandardSourceDefinition(standardSourceDefinition.getSourceDefinitionId()))
        .thenReturn(standardSourceDefinition);
    when(configRepository.getSourceConnection(any()))
        .thenReturn(sourceConnection);

    standardDestinationDefinition = new StandardDestinationDefinition()
        .withDestinationDefinitionId(UUID.randomUUID())
        .withName("test-standard-destination")
        .withDockerRepository("test")
        .withDocumentationUrl("http://doc")
        .withIcon("hello")
        .withDockerImageTag("dev")
        .withSpec(new ConnectorSpecification());
    destinationConnection = new DestinationConnection()
        .withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(standardDestinationDefinition.getDestinationDefinitionId())
        .withConfiguration(Jsons.emptyObject())
        .withName("test-source")
        .withTombstone(false)
        .withWorkspaceId(workspaceId);
    when(configRepository.listStandardDestinationDefinitions())
        .thenReturn(List.of(standardDestinationDefinition));
    when(configRepository.getStandardDestinationDefinition(standardDestinationDefinition.getDestinationDefinitionId()))
        .thenReturn(standardDestinationDefinition);
    when(configRepository.getDestinationConnection(any()))
        .thenReturn(destinationConnection);

    operation = new StandardSyncOperation()
        .withOperationId(UUID.randomUUID())
        .withName("test-operation")
        .withWorkspaceId(workspaceId)
        .withTombstone(false)
        .withOperatorType(OperatorType.DBT);
    when(configRepository.getStandardSyncOperation(any()))
        .thenReturn(operation);

    connection = new StandardSync()
        .withConnectionId(UUID.randomUUID())
        .withSourceId(sourceConnection.getSourceId())
        .withDestinationId(destinationConnection.getDestinationId())
        .withOperationIds(List.of(operation.getOperationId()))
        .withName("test-sync")
        .withStatus(Status.ACTIVE);

    when(workspaceHelper.getWorkspaceForConnection(sourceConnection.getSourceId(), destinationConnection.getDestinationId()))
        .thenReturn(workspaceId);
  }

  @Test
  public void testImportIntoWorkspaceWithConflicts() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listSourceConnectionWithSecrets())
        .thenReturn(List.of(sourceConnection,
            new SourceConnection()
                .withSourceId(UUID.randomUUID())
                .withWorkspaceId(UUID.randomUUID())));
    when(configRepository.listDestinationConnectionWithSecrets())
        .thenReturn(List.of(destinationConnection,
            new DestinationConnection()
                .withDestinationId(UUID.randomUUID())
                .withWorkspaceId(UUID.randomUUID())));
    when(configRepository.listStandardSyncOperations())
        .thenReturn(List.of(operation,
            new StandardSyncOperation()
                .withOperationId(UUID.randomUUID())
                .withWorkspaceId(UUID.randomUUID())));
    when(configRepository.listStandardSyncs())
        .thenReturn(List.of(connection));
    final File archive = configDumpExporter.exportWorkspace(workspaceId);

    final UUID newWorkspaceId = UUID.randomUUID();
    configDumpImporter.importIntoWorkspace(TEST_VERSION, newWorkspaceId, archive);

    verify(configRepository)
        .writeSourceConnection(
            Jsons.clone(sourceConnection).withWorkspaceId(newWorkspaceId).withSourceId(not(eq(sourceConnection.getSourceId()))),
            eq(emptyConnectorSpec));
    verify(configRepository).writeDestinationConnection(
        Jsons.clone(destinationConnection).withWorkspaceId(newWorkspaceId).withDestinationId(not(eq(destinationConnection.getDestinationId()))),
        eq(emptyConnectorSpec));
    verify(configRepository)
        .writeStandardSyncOperation(Jsons.clone(operation).withWorkspaceId(newWorkspaceId).withOperationId(not(eq(operation.getOperationId()))));
    verify(configRepository).writeStandardSync(Jsons.clone(connection).withConnectionId(not(eq(connection.getConnectionId()))));
  }

  @Test
  public void testImportIntoWorkspaceWithoutConflicts() throws JsonValidationException, ConfigNotFoundException, IOException {
    when(configRepository.listSourceConnectionWithSecrets())
        // First called for export
        .thenReturn(List.of(sourceConnection,
            new SourceConnection()
                .withSourceId(UUID.randomUUID())
                .withWorkspaceId(UUID.randomUUID())))
        // then called for import
        .thenReturn(List.of(new SourceConnection()
            .withSourceId(UUID.randomUUID())
            .withWorkspaceId(UUID.randomUUID())));
    when(configRepository.listDestinationConnectionWithSecrets())
        // First called for export
        .thenReturn(List.of(destinationConnection,
            new DestinationConnection()
                .withDestinationId(UUID.randomUUID())
                .withWorkspaceId(UUID.randomUUID())))
        // then called for import
        .thenReturn(List.of(new DestinationConnection()
            .withDestinationId(UUID.randomUUID())
            .withWorkspaceId(UUID.randomUUID())));
    when(configRepository.listStandardSyncOperations())
        // First called for export
        .thenReturn(List.of(operation,
            new StandardSyncOperation()
                .withOperationId(UUID.randomUUID())
                .withWorkspaceId(UUID.randomUUID())))
        // then called for import
        .thenReturn(List.of(new StandardSyncOperation()
            .withOperationId(UUID.randomUUID())
            .withWorkspaceId(UUID.randomUUID())));
    when(configRepository.listStandardSyncs())
        // First called for export
        .thenReturn(List.of(connection))
        // then called for import
        .thenReturn(List.of());
    final File archive = configDumpExporter.exportWorkspace(workspaceId);

    final UUID newWorkspaceId = UUID.randomUUID();
    configDumpImporter.importIntoWorkspace(TEST_VERSION, newWorkspaceId, archive);

    verify(configRepository).writeSourceConnection(
        Jsons.clone(sourceConnection).withWorkspaceId(newWorkspaceId),
        emptyConnectorSpec);
    verify(configRepository).writeDestinationConnection(Jsons.clone(destinationConnection).withWorkspaceId(newWorkspaceId), emptyConnectorSpec);
    verify(configRepository).writeStandardSyncOperation(Jsons.clone(operation).withWorkspaceId(newWorkspaceId));
    verify(configRepository).writeStandardSync(connection);
  }

  @Test
  public void testReplaceDeploymentMetadata() throws Exception {
    final UUID oldDeploymentUuid = UUID.randomUUID();
    final UUID newDeploymentUuid = UUID.randomUUID();

    final JsonNode airbyteVersion = Jsons.deserialize("{\"key\":\"airbyte_version\",\"value\":\"dev\"}");
    final JsonNode serverUuid = Jsons.deserialize("{\"key\":\"server_uuid\",\"value\":\"e895a584-7dbf-48ce-ace6-0bc9ea570c34\"}");
    final JsonNode date = Jsons.deserialize("{\"key\":\"date\",\"value\":\"1956-08-17\"}");
    final JsonNode oldDeploymentId = Jsons.deserialize(
        String.format("{\"key\":\"%s\",\"value\":\"%s\"}", DefaultJobPersistence.DEPLOYMENT_ID_KEY, oldDeploymentUuid));
    final JsonNode newDeploymentId = Jsons.deserialize(
        String.format("{\"key\":\"%s\",\"value\":\"%s\"}", DefaultJobPersistence.DEPLOYMENT_ID_KEY, newDeploymentUuid));

    final JobPersistence jobPersistence = mock(JobPersistence.class);

    // when new deployment id does not exist, the old deployment id is removed
    when(jobPersistence.getDeployment()).thenReturn(Optional.empty());
    final Stream<JsonNode> inputStream1 = Stream.of(airbyteVersion, serverUuid, date, oldDeploymentId);
    final Stream<JsonNode> outputStream1 = ConfigDumpImporter.replaceDeploymentMetadata(jobPersistence, inputStream1);
    final Stream<JsonNode> expectedStream1 = Stream.of(airbyteVersion, serverUuid, date);
    assertEquals(expectedStream1.collect(Collectors.toList()), outputStream1.collect(Collectors.toList()));

    // when new deployment id exists, the old deployment id is replaced with the new one
    when(jobPersistence.getDeployment()).thenReturn(Optional.of(newDeploymentUuid));
    final Stream<JsonNode> inputStream2 = Stream.of(airbyteVersion, serverUuid, date, oldDeploymentId);
    final Stream<JsonNode> outputStream2 = ConfigDumpImporter.replaceDeploymentMetadata(jobPersistence, inputStream2);
    final Stream<JsonNode> expectedStream2 = Stream.of(airbyteVersion, serverUuid, date, newDeploymentId);
    assertEquals(expectedStream2.collect(Collectors.toList()), outputStream2.collect(Collectors.toList()));
  }

}
