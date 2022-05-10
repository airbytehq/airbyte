/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.api.model.ImportRequestBody;
import io.airbyte.api.model.UploadRead;
import io.airbyte.api.model.WorkspaceIdRequestBody;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.Notification;
import io.airbyte.config.Notification.NotificationType;
import io.airbyte.config.SlackNotificationConfiguration;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSourceDefinition.SourceType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.init.YamlSeedConfigPersistence;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.NoOpSecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.test.utils.DatabaseConnectionHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.Closeable;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.shaded.com.google.common.collect.ImmutableMap;
import org.testcontainers.shaded.org.apache.commons.io.FileUtils;

public class ArchiveHandlerTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ArchiveHandlerTest.class);

  private static final AirbyteVersion VERSION = new AirbyteVersion("0.6.8");
  private static PostgreSQLContainer<?> container;

  private DataSource dataSource;
  private DSLContext dslContext;
  private Database jobDatabase;
  private Database configDatabase;
  private JobPersistence jobPersistence;
  private SecretsRepositoryReader secretsRepositoryReader;
  private SecretsRepositoryWriter secretsRepositoryWriter;
  private ConfigPersistence configPersistence;
  private ConfigPersistence seedPersistence;
  private JsonSecretsProcessor jsonSecretsProcessor;
  private ConfigRepository configRepository;
  private ArchiveHandler archiveHandler;

  private static class NoOpFileTtlManager extends FileTtlManager {

    public NoOpFileTtlManager() {
      super(1L, TimeUnit.MINUTES, 1L);
    }

    public void register(final Path path) {}

  }

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  @BeforeEach
  public void setup() throws Exception {
    dataSource = DatabaseConnectionHelper.createDataSource(container);
    dslContext = DSLContextFactory.create(dataSource, SQLDialect.POSTGRES);
    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(dataSource, dslContext);
    jobDatabase = databaseProviders.createNewJobsDatabase();
    configDatabase = databaseProviders.createNewConfigsDatabase();
    jobPersistence = new DefaultJobPersistence(jobDatabase);
    seedPersistence = YamlSeedConfigPersistence.getDefault();
    jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .maskSecrets(false)
        .copySecrets(false)
        .build();;
    configPersistence = new DatabaseConfigPersistence(jobDatabase, jsonSecretsProcessor);
    configPersistence.replaceAllConfigs(Collections.emptyMap(), false);
    configPersistence.loadData(seedPersistence);
    configRepository = new ConfigRepository(configPersistence, configDatabase);
    secretsRepositoryReader = new SecretsRepositoryReader(configRepository, new NoOpSecretsHydrator());
    secretsRepositoryWriter = new SecretsRepositoryWriter(configRepository, Optional.empty(), Optional.empty());

    jobPersistence.setVersion(VERSION.serialize());

    archiveHandler = new ArchiveHandler(
        VERSION,
        configRepository,
        secretsRepositoryReader,
        secretsRepositoryWriter,
        jobPersistence,
        YamlSeedConfigPersistence.getDefault(),
        new WorkspaceHelper(configRepository, jobPersistence),
        new NoOpFileTtlManager(),
        true);
  }

  @AfterEach
  void tearDown() throws IOException {
    dslContext.close();
    if (dataSource instanceof Closeable closeable) {
      closeable.close();
    }
  }

  /**
   * After exporting and importing, the configs should remain the same.
   */
  @Test
  void testFullExportImportRoundTrip() throws Exception {
    assertSameConfigDump(seedPersistence.dumpConfigs(), secretsRepositoryReader.dumpConfigsWithSecrets());

    // Export the configs.
    File archive = archiveHandler.exportData();

    // After deleting the configs, the dump becomes empty.
    configPersistence.replaceAllConfigs(Collections.emptyMap(), false);
    assertSameConfigDump(Collections.emptyMap(), secretsRepositoryReader.dumpConfigsWithSecrets());

    // After importing the configs, the dump is restored.
    assertTrue(archive.exists());
    final ImportRead importResult = archiveHandler.importData(archive);
    assertFalse(archive.exists());
    assertEquals(StatusEnum.SUCCEEDED, importResult.getStatus());
    assertSameConfigDump(seedPersistence.dumpConfigs(), secretsRepositoryReader.dumpConfigsWithSecrets());

    // When a connector definition is in use, it will not be updated.
    final UUID sourceS3DefinitionId = UUID.fromString("69589781-7828-43c5-9f63-8925b1c1ccc2");
    final String sourceS3DefinitionVersion = "0.0.0";
    final StandardSourceDefinition sourceS3Definition = seedPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        sourceS3DefinitionId.toString(),
        StandardSourceDefinition.class)
        // This source definition is on an old version
        .withDockerImageTag(sourceS3DefinitionVersion)
        .withTombstone(false);
    final Notification notification = new Notification()
        .withNotificationType(NotificationType.SLACK)
        .withSendOnFailure(true)
        .withSendOnSuccess(true)
        .withSlackConfiguration(new SlackNotificationConfiguration().withWebhook("webhook-url"));
    final StandardWorkspace standardWorkspace = new StandardWorkspace()
        .withWorkspaceId(UUID.randomUUID())
        .withCustomerId(UUID.randomUUID())
        .withName("test-workspace")
        .withSlug("random-string")
        .withEmail("abc@xyz.com")
        .withInitialSetupComplete(true)
        .withAnonymousDataCollection(true)
        .withNews(true)
        .withSecurityUpdates(true)
        .withDisplaySetupWizard(true)
        .withTombstone(false)
        .withNotifications(Collections.singletonList(notification))
        .withFirstCompletedSync(true)
        .withFeedbackDone(true);
    final SourceConnection sourceConnection = new SourceConnection()
        .withSourceDefinitionId(sourceS3DefinitionId)
        .withSourceId(UUID.randomUUID())
        .withWorkspaceId(standardWorkspace.getWorkspaceId())
        .withName("Test source")
        .withConfiguration(Jsons.deserialize("{}"))
        .withTombstone(false);

    // Write source connection and an old source definition.
    configPersistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, standardWorkspace.getWorkspaceId().toString(), standardWorkspace);
    configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, sourceConnection.getSourceId().toString(), sourceConnection);
    configPersistence.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceS3DefinitionId.toString(), sourceS3Definition);

    // Export, wipe, and import the configs.
    archive = archiveHandler.exportData();
    configPersistence.replaceAllConfigs(Collections.emptyMap(), false);
    archiveHandler.importData(archive);

    // The version has not changed.
    final StandardSourceDefinition actualS3Definition = configPersistence.getConfig(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        sourceS3DefinitionId.toString(),
        StandardSourceDefinition.class);
    assertEquals(sourceS3DefinitionVersion, actualS3Definition.getDockerImageTag());
  }

  @Test
  void testLightWeightExportImportRoundTrip() throws Exception {
    assertSameConfigDump(seedPersistence.dumpConfigs(), secretsRepositoryReader.dumpConfigsWithSecrets());

    // Insert some workspace data
    final UUID workspaceId = UUID.randomUUID();
    setupTestData(workspaceId);
    final Map<String, Stream<JsonNode>> workspaceDump = secretsRepositoryReader.dumpConfigsWithSecrets();

    // Insert some other workspace data
    setupTestData(UUID.randomUUID());

    // Export the first workspace configs
    File archive = archiveHandler.exportWorkspace(new WorkspaceIdRequestBody().workspaceId(workspaceId));
    final File secondArchive = Files.createTempFile("tests", "archive").toFile();
    FileUtils.copyFile(archive, secondArchive);

    // After deleting all the configs, the dump becomes empty.
    configPersistence.replaceAllConfigs(Collections.emptyMap(), false);
    assertSameConfigDump(Collections.emptyMap(), secretsRepositoryReader.dumpConfigsWithSecrets());

    // Restore default seed data
    configPersistence.loadData(seedPersistence);
    assertSameConfigDump(seedPersistence.dumpConfigs(), secretsRepositoryReader.dumpConfigsWithSecrets());

    setupWorkspaceData(workspaceId);

    // After importing the configs, the first workspace is restored.
    assertTrue(archive.exists());
    UploadRead uploadRead = archiveHandler.uploadArchiveResource(archive);
    assertFalse(archive.exists());
    assertEquals(UploadRead.StatusEnum.SUCCEEDED, uploadRead.getStatus());
    ImportRead importResult = archiveHandler.importIntoWorkspace(new ImportRequestBody()
        .resourceId(uploadRead.getResourceId())
        .workspaceId(workspaceId));
    assertEquals(StatusEnum.SUCCEEDED, importResult.getStatus());
    assertSameConfigDump(workspaceDump, secretsRepositoryReader.dumpConfigsWithSecrets());

    // we modify first workspace
    setupTestData(workspaceId);
    final Map<String, Stream<JsonNode>> secondWorkspaceDump = secretsRepositoryReader.dumpConfigsWithSecrets();

    final UUID secondWorkspaceId = UUID.randomUUID();
    setupWorkspaceData(secondWorkspaceId);

    // the archive is importing again in another workspace
    final UploadRead secondUploadRead = archiveHandler.uploadArchiveResource(secondArchive);
    assertEquals(UploadRead.StatusEnum.SUCCEEDED, secondUploadRead.getStatus());
    final ImportRead secondImportResult = archiveHandler.importIntoWorkspace(new ImportRequestBody()
        .resourceId(secondUploadRead.getResourceId())
        .workspaceId(secondWorkspaceId));
    assertEquals(StatusEnum.SUCCEEDED, secondImportResult.getStatus());

    final UUID secondSourceId = secretsRepositoryReader.listSourceConnectionWithSecrets()
        .stream()
        .filter(sourceConnection -> secondWorkspaceId.equals(sourceConnection.getWorkspaceId()))
        .map(SourceConnection::getSourceId)
        .collect(Collectors.toList()).get(0);

    final StandardSourceDefinition standardSourceDefinition = new StandardSourceDefinition()
        .withSourceDefinitionId(UUID.randomUUID())
        .withSourceType(SourceType.API)
        .withName("random-source-1")
        .withDockerImageTag("tag-1")
        .withDockerRepository("repository-1")
        .withDocumentationUrl("documentation-url-1")
        .withIcon("icon-1")
        .withSpec(new ConnectorSpecification())
        .withTombstone(false);

    final SourceConnection sourceConnection = new SourceConnection()
        .withWorkspaceId(secondWorkspaceId)
        .withSourceId(secondSourceId)
        .withName("Some new names")
        .withSourceDefinitionId(standardSourceDefinition.getSourceDefinitionId())
        .withTombstone(false)
        .withConfiguration(Jsons.emptyObject());

    final ConnectorSpecification emptyConnectorSpec = mock(ConnectorSpecification.class);
    when(emptyConnectorSpec.getConnectionSpecification()).thenReturn(Jsons.emptyObject());

    configRepository.writeStandardSourceDefinition(standardSourceDefinition);
    secretsRepositoryWriter.writeSourceConnection(sourceConnection, emptyConnectorSpec);

    // check that first workspace is unchanged even though modifications were made to second workspace
    // (that contains similar connections from importing the same archive)
    archive = archiveHandler.exportWorkspace(new WorkspaceIdRequestBody().workspaceId(workspaceId));
    configPersistence.replaceAllConfigs(Collections.emptyMap(), false);
    configPersistence.loadData(seedPersistence);
    setupWorkspaceData(workspaceId);
    uploadRead = archiveHandler.uploadArchiveResource(archive);
    assertEquals(UploadRead.StatusEnum.SUCCEEDED, uploadRead.getStatus());
    importResult = archiveHandler.importIntoWorkspace(new ImportRequestBody()
        .resourceId(uploadRead.getResourceId())
        .workspaceId(workspaceId));
    assertEquals(StatusEnum.SUCCEEDED, importResult.getStatus());
    assertSameConfigDump(secondWorkspaceDump, secretsRepositoryReader.dumpConfigsWithSecrets());
  }

  private void setupWorkspaceData(final UUID workspaceId) throws IOException, JsonValidationException {
    configPersistence.writeConfig(ConfigSchema.STANDARD_WORKSPACE, workspaceId.toString(), new StandardWorkspace()
        .withWorkspaceId(workspaceId)
        .withName("test-workspace")
        .withSlug(workspaceId.toString())
        .withInitialSetupComplete(false)
        .withTombstone(false));
  }

  private void setupTestData(final UUID workspaceId) throws JsonValidationException, IOException {
    // Fill up with some configurations
    setupWorkspaceData(workspaceId);
    final UUID sourceid = UUID.randomUUID();
    configPersistence.writeConfig(ConfigSchema.SOURCE_CONNECTION, sourceid.toString(), new SourceConnection()
        .withSourceId(sourceid)
        .withWorkspaceId(workspaceId)
        .withSourceDefinitionId(UUID.fromString("ef69ef6e-aa7f-4af1-a01d-ef775033524e")) // GitHub source definition
        .withName("test-source")
        .withConfiguration(Jsons.jsonNode(ImmutableMap.of("start_date", "2021-03-01T00:00:00Z", "repository", "airbytehq/airbyte")))
        .withTombstone(false));
    final UUID destinationId = UUID.randomUUID();
    configPersistence.writeConfig(ConfigSchema.DESTINATION_CONNECTION, destinationId.toString(), new DestinationConnection()
        .withDestinationId(destinationId)
        .withWorkspaceId(workspaceId)
        .withDestinationDefinitionId(UUID.fromString("079d5540-f236-4294-ba7c-ade8fd918496")) // BigQuery destination definition
        .withName("test-destination")
        .withConfiguration(Jsons.jsonNode(ImmutableMap.of("project_id", "project", "dataset_id", "dataset")))
        .withTombstone(false));
  }

  private void assertSameConfigDump(final Map<String, Stream<JsonNode>> expected, final Map<String, Stream<JsonNode>> actual) {
    assertEquals(expected.keySet(), actual.keySet(),
        String.format("The expected (%s) vs actual (%s) streams does not match", expected.size(), actual.size()));
    for (final String stream : expected.keySet()) {
      LOGGER.info("Checking stream {}", stream);
      // assertEquals cannot correctly check the equality of two maps with stream values,
      // so streams are converted to sets before being compared.
      final Set<JsonNode> expectedRecords = expected.get(stream).collect(Collectors.toSet());
      final Set<JsonNode> actualRecords = actual.get(stream).collect(Collectors.toSet());
      for (final var expectedRecord : expectedRecords) {
        assertTrue(
            actualRecords.contains(expectedRecord),
            String.format(
                "\n Expected record was not found:\n%s\n Actual records were:\n%s\n",
                expectedRecord,
                Strings.join(actualRecords, "\n")));
      }
      assertEquals(expectedRecords.size(), actualRecords.size(),
          String.format(
              "The expected vs actual records does not match:\n expected records:\n%s\n actual records\n%s\n",
              Strings.join(expectedRecords, "\n"),
              Strings.join(actualRecords, "\n")));
    }
  }

}
