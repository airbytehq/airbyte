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

package io.airbyte.server.migration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;

import com.google.common.io.Resources;
import io.airbyte.commons.io.Archives;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.FileSystemConfigPersistence;
import io.airbyte.config.persistence.YamlSeedConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.migrate.Migrations;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.RunMigration;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.jetbrains.annotations.NotNull;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class RunMigrationTest {

  private static final String INITIAL_VERSION = "0.17.0-alpha";
  private static final String TARGET_VERSION = Migrations.MIGRATIONS.get(Migrations.MIGRATIONS.size() - 1).getVersion();
  private static final String DEPRECATED_SOURCE_DEFINITION_NOT_BEING_USED = "d2147be5-fa36-4936-977e-f031affa5895";
  private static final String DEPRECATED_SOURCE_DEFINITION_BEING_USED = "4eb22946-2a79-4d20-a3e6-effd234613c3";
  private List<File> resourceToBeCleanedUp;

  @BeforeEach
  public void setup() {
    resourceToBeCleanedUp = new ArrayList<>();
  }

  @AfterEach
  public void cleanup() throws IOException {
    for (final File file : resourceToBeCleanedUp) {
      if (file.exists()) {
        if (file.isDirectory()) {
          FileUtils.deleteDirectory(file);
        } else {
          Files.delete(file.toPath());
        }
      }
    }
  }

  @SuppressWarnings("UnstableApiUsage")
  @Test
  public void testRunMigration() throws Exception {
    try (final StubAirbyteDB stubAirbyteDB = new StubAirbyteDB()) {
      final File file = Path
          .of(Resources.getResource("migration/03a4c904-c91d-447f-ab59-27a43b52c2fd.gz").toURI())
          .toFile();

      final Path dummyDataSource = Path.of(Resources.getResource("migration/dummy_data").toURI());

      final Path configRoot = Files.createTempDirectory(Path.of("/tmp"), "dummy_data");
      FileUtils.copyDirectory(dummyDataSource.toFile(), configRoot.toFile());
      resourceToBeCleanedUp.add(configRoot.toFile());
      final JobPersistence jobPersistence = getJobPersistence(stubAirbyteDB.getDatabase(), file, INITIAL_VERSION);
      assertPreMigrationConfigs(configRoot, jobPersistence);

      runMigration(jobPersistence, configRoot);

      assertDatabaseVersion(jobPersistence, TARGET_VERSION);
      assertPostMigrationConfigs(configRoot);
      FileUtils.deleteDirectory(configRoot.toFile());
    }
  }

  private void assertPreMigrationConfigs(Path configRoot, JobPersistence jobPersistence) throws Exception {
    assertDatabaseVersion(jobPersistence, INITIAL_VERSION);
    ConfigRepository configRepository = new ConfigRepository(FileSystemConfigPersistence.createWithValidation(configRoot));
    Map<String, StandardSourceDefinition> sourceDefinitionsBeforeMigration = configRepository.listStandardSources().stream()
        .collect(Collectors.toMap(c -> c.getSourceDefinitionId().toString(), c -> c));
    assertTrue(sourceDefinitionsBeforeMigration.containsKey(DEPRECATED_SOURCE_DEFINITION_NOT_BEING_USED));
    assertTrue(sourceDefinitionsBeforeMigration.containsKey(DEPRECATED_SOURCE_DEFINITION_BEING_USED));
  }

  private void assertDatabaseVersion(JobPersistence jobPersistence, String version) throws IOException {
    final Optional<String> versionFromDb = jobPersistence.getVersion();
    assertTrue(versionFromDb.isPresent());
    assertEquals(versionFromDb.get(), version);
  }

  private void assertPostMigrationConfigs(Path importRoot) throws Exception {
    final ConfigRepository configRepository = new ConfigRepository(FileSystemConfigPersistence.createWithValidation(importRoot));
    final UUID workspaceId = configRepository.listStandardWorkspaces(true).get(0).getWorkspaceId();
    // originally the default workspace started with a hardcoded id. the migration in version 0.29.0
    // took that id and randomized it. we want to check that the id is now NOT that hardcoded id and
    // that all related resources use the updated workspaceId as well.
    assertNotEquals(UUID.fromString("5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6"), workspaceId);
    final StandardSyncOperation standardSyncOperation = assertSyncOperations(configRepository);
    assertStandardSyncs(configRepository, standardSyncOperation);
    assertWorkspace(configRepository, workspaceId);
    assertSources(configRepository, workspaceId);
    assertDestinations(configRepository, workspaceId);
    assertSourceDefinitions(configRepository);
    assertDestinationDefinitions(configRepository);
  }

  private void assertSourceDefinitions(ConfigRepository configRepository) throws JsonValidationException, IOException {
    final Map<String, StandardSourceDefinition> sourceDefinitions = configRepository.listStandardSources()
        .stream()
        .collect(Collectors.toMap(c -> c.getSourceDefinitionId().toString(), c -> c));
    assertTrue(sourceDefinitions.size() >= 59);
    // the definition is not present in latest seeds so it should be deleted
    assertFalse(sourceDefinitions.containsKey(DEPRECATED_SOURCE_DEFINITION_NOT_BEING_USED));
    // the definition is not present in latest seeds but it was being used as a connection so it should
    // not be deleted
    assertTrue(sourceDefinitions.containsKey(DEPRECATED_SOURCE_DEFINITION_BEING_USED));

    final StandardSourceDefinition mysqlDefinition = sourceDefinitions.get("435bb9a5-7887-4809-aa58-28c27df0d7ad");
    assertEquals("0.2.0", mysqlDefinition.getDockerImageTag());
    assertEquals("MySQL", mysqlDefinition.getName());

    final StandardSourceDefinition postgresDefinition = sourceDefinitions.get("decd338e-5647-4c0b-adf4-da0e75f5a750");
    String[] tagBrokenAsArray = postgresDefinition.getDockerImageTag().replace(".", ",").split(",");
    assertEquals(3, tagBrokenAsArray.length);
    assertTrue(Integer.parseInt(tagBrokenAsArray[0]) >= 0);
    assertTrue(Integer.parseInt(tagBrokenAsArray[1]) >= 3);
    assertTrue(Integer.parseInt(tagBrokenAsArray[2]) >= 4);
    assertTrue(postgresDefinition.getName().contains("Postgres"));
  }

  private void assertDestinationDefinitions(ConfigRepository configRepository) throws JsonValidationException, IOException {
    final Map<String, StandardDestinationDefinition> sourceDefinitions = configRepository.listStandardDestinationDefinitions()
        .stream()
        .collect(Collectors.toMap(c -> c.getDestinationDefinitionId().toString(), c -> c));
    assertTrue(sourceDefinitions.size() >= 11);

    final StandardDestinationDefinition postgresDefinition = sourceDefinitions.get("25c5221d-dce2-4163-ade9-739ef790f503");
    assertEquals("0.2.0", postgresDefinition.getDockerImageTag());
    assertEquals(postgresDefinition.getName(), "Postgres");

    final StandardDestinationDefinition localCsvDefinition = sourceDefinitions.get("8be1cf83-fde1-477f-a4ad-318d23c9f3c6");
    assertTrue(localCsvDefinition.getName().contains("Local CSV"));
    assertEquals("0.2.0", localCsvDefinition.getDockerImageTag());

    final StandardDestinationDefinition snowflakeDefinition = sourceDefinitions.get("424892c4-daac-4491-b35d-c6688ba547ba");
    String[] tagBrokenAsArray = snowflakeDefinition.getDockerImageTag().replace(".", ",").split(",");
    assertEquals(3, tagBrokenAsArray.length);
    assertTrue(Integer.parseInt(tagBrokenAsArray[0]) >= 0);
    assertTrue(Integer.parseInt(tagBrokenAsArray[1]) >= 3);
    assertTrue(Integer.parseInt(tagBrokenAsArray[2]) >= 9);
    assertTrue(snowflakeDefinition.getName().contains("Snowflake"));
  }

  private void assertStandardSyncs(ConfigRepository configRepository,
                                   StandardSyncOperation standardSyncOperation)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final List<StandardSync> standardSyncs = configRepository.listStandardSyncs();
    assertEquals(standardSyncs.size(), 2);
    for (StandardSync standardSync : standardSyncs) {
      if (standardSync.getConnectionId().toString().equals("a294256f-1abe-4837-925f-91602c7207b4")) {
        assertEquals(standardSync.getPrefix(), "");
        assertEquals(standardSync.getSourceId().toString(), "28ffee2b-372a-4f72-9b95-8ed56a8b99c5");
        assertEquals(standardSync.getDestinationId().toString(), "4e00862d-5484-4f50-9860-f3bbb4317397");
        assertEquals(standardSync.getOperationIds().size(), 1);
        assertEquals(standardSync.getOperationIds().get(0).toString(), standardSyncOperation.getOperationId().toString());
        assertEquals(standardSync.getName(), "default");
        assertEquals(standardSync.getStatus().value(), "active");
        assertNull(standardSync.getSchedule());
        assertTrue(standardSync.getManual());
      } else if (standardSync.getConnectionId().toString().equals("49dae3f0-158b-4737-b6e4-0eed77d4b74e")) {
        assertEquals(standardSync.getPrefix(), "");
        assertEquals(standardSync.getSourceId().toString(), "28ffee2b-372a-4f72-9b95-8ed56a8b99c5");
        assertEquals(standardSync.getDestinationId().toString(), "5434615d-a3b7-4351-bc6b-a9a695555a30");
        assertEquals(standardSync.getOperationIds().size(), 0);
        assertEquals(standardSync.getName(), "default");
        assertEquals(standardSync.getStatus().value(), "active");
        assertNull(standardSync.getSchedule());
        assertTrue(standardSync.getManual());
      } else {
        fail("Unknown sync " + standardSync.getConnectionId().toString());
      }
    }
  }

  @NotNull
  private StandardSyncOperation assertSyncOperations(ConfigRepository configRepository) throws IOException, JsonValidationException {
    final List<StandardSyncOperation> standardSyncOperations = configRepository.listStandardSyncOperations();
    assertEquals(standardSyncOperations.size(), 1);
    final StandardSyncOperation standardSyncOperation = standardSyncOperations.get(0);
    assertEquals(standardSyncOperation.getName(), "default-normalization");
    assertEquals(standardSyncOperation.getOperatorType(), OperatorType.NORMALIZATION);
    assertEquals(standardSyncOperation.getOperatorNormalization().getOption(), Option.BASIC);
    assertNull(standardSyncOperation.getOperatorDbt());
    assertFalse(standardSyncOperation.getTombstone());
    return standardSyncOperation;
  }

  private void assertSources(ConfigRepository configRepository, UUID workspaceId) throws JsonValidationException, IOException {
    final Map<String, SourceConnection> sources = configRepository.listSourceConnection()
        .stream()
        .collect(Collectors.toMap(sourceConnection -> sourceConnection.getSourceId().toString(), sourceConnection -> sourceConnection));
    assertEquals(sources.size(), 2);
    final SourceConnection mysqlConnection = sources.get("28ffee2b-372a-4f72-9b95-8ed56a8b99c5");
    assertEquals("MySQL localhost", mysqlConnection.getName());
    assertEquals("435bb9a5-7887-4809-aa58-28c27df0d7ad", mysqlConnection.getSourceDefinitionId().toString());
    assertEquals(workspaceId, mysqlConnection.getWorkspaceId());
    assertEquals("28ffee2b-372a-4f72-9b95-8ed56a8b99c5", mysqlConnection.getSourceId().toString());
    assertEquals("root", mysqlConnection.getConfiguration().get("username").asText());
    assertEquals("password", mysqlConnection.getConfiguration().get("password").asText());
    assertEquals("localhost_test", mysqlConnection.getConfiguration().get("database").asText());
    assertEquals(3306, mysqlConnection.getConfiguration().get("port").asInt());
    assertEquals("host.docker.internal", mysqlConnection.getConfiguration().get("host").asText());
    assertTrue(sources.containsKey("e48cae1a-1f5c-42cc-9ec1-a44ff7fb4969"));

  }

  private void assertWorkspace(ConfigRepository configRepository, UUID workspaceId) throws JsonValidationException, IOException {
    final List<StandardWorkspace> standardWorkspaces = configRepository.listStandardWorkspaces(true);
    assertEquals(1, standardWorkspaces.size());
    final StandardWorkspace workspace = standardWorkspaces.get(0);
    assertEquals(workspaceId, workspace.getWorkspaceId());
    assertEquals("17f90b72-5ae4-40b7-bc49-d6c2943aea57", workspace.getCustomerId().toString());
    assertEquals("default", workspace.getName());
    assertEquals("default", workspace.getSlug());
    assertEquals(true, workspace.getInitialSetupComplete());
    assertEquals(false, workspace.getAnonymousDataCollection());
    assertEquals(false, workspace.getNews());
    assertEquals(false, workspace.getSecurityUpdates());
    assertEquals(false, workspace.getDisplaySetupWizard());
  }

  private void assertDestinations(ConfigRepository configRepository, UUID workspaceId) throws JsonValidationException, IOException {
    final List<DestinationConnection> destinationConnections = configRepository.listDestinationConnection();
    assertEquals(destinationConnections.size(), 2);
    for (final DestinationConnection destination : destinationConnections) {
      if (destination.getDestinationId().toString().equals("4e00862d-5484-4f50-9860-f3bbb4317397")) {
        assertEquals("Postgres Docker", destination.getName());
        assertEquals("25c5221d-dce2-4163-ade9-739ef790f503", destination.getDestinationDefinitionId().toString());
        assertEquals(workspaceId, destination.getWorkspaceId());
        assertEquals("postgres", destination.getConfiguration().get("username").asText());
        assertEquals("password", destination.getConfiguration().get("password").asText());
        assertEquals("postgres", destination.getConfiguration().get("database").asText());
        assertEquals("public", destination.getConfiguration().get("schema").asText());
        assertEquals(3000, destination.getConfiguration().get("port").asInt());
        assertEquals("localhost", destination.getConfiguration().get("host").asText());
        assertNull(destination.getConfiguration().get("basic_normalization"));
      } else if (destination.getDestinationId().toString().equals("5434615d-a3b7-4351-bc6b-a9a695555a30")) {
        assertEquals("CSV", destination.getName());
        assertEquals("8be1cf83-fde1-477f-a4ad-318d23c9f3c6", destination.getDestinationDefinitionId().toString());
        assertEquals(workspaceId, destination.getWorkspaceId());
        assertEquals("csv_data", destination.getConfiguration().get("destination_path").asText());
      } else {
        fail("Unknown destination found with destination id : " + destination.getDestinationId().toString());
      }
    }
  }

  private void runMigration(JobPersistence jobPersistence, Path configRoot) throws Exception {
    try (final RunMigration runMigration = new RunMigration(
        jobPersistence,
        new ConfigRepository(FileSystemConfigPersistence.createWithValidation(configRoot)),
        TARGET_VERSION,
        YamlSeedConfigPersistence.get())) {
      runMigration.run();
    }
  }

  @SuppressWarnings("SameParameterValue")
  private JobPersistence getJobPersistence(Database database, File file, String version) throws IOException {
    final DefaultJobPersistence jobPersistence = new DefaultJobPersistence(database);
    final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), "db_init");
    resourceToBeCleanedUp.add(tempFolder.toFile());

    Archives.extractArchive(file.toPath(), tempFolder);
    final DatabaseArchiver databaseArchiver = new DatabaseArchiver(jobPersistence);
    databaseArchiver.importDatabaseFromArchive(tempFolder, version);
    return jobPersistence;
  }

}
