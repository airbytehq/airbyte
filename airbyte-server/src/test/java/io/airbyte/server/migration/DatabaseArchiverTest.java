/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.migration;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.db.Database;
import io.airbyte.db.instance.jobs.JobsDatabaseSchema;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Set;
import java.util.stream.Collectors;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;

public class DatabaseArchiverTest {

  private static final String TEMP_PREFIX = "testDatabaseArchive";

  private PostgreSQLContainer<?> container;
  private Database jobDatabase;
  private Database configDatabase;
  private DatabaseArchiver databaseArchiver;

  @BeforeEach
  void setUp() throws IOException {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();

    final TestDatabaseProviders databaseProviders = new TestDatabaseProviders(container);
    jobDatabase = databaseProviders.createNewJobsDatabase();
    configDatabase = databaseProviders.createNewConfigsDatabase();
    final JobPersistence persistence = new DefaultJobPersistence(jobDatabase);
    databaseArchiver = new DatabaseArchiver(persistence);
  }

  @AfterEach
  void tearDown() throws Exception {
    jobDatabase.close();
    configDatabase.close();
    container.close();
  }

  @Test
  void testUnknownTableExport() throws Exception {
    // Create a table that is not declared in JobsDatabaseSchema
    jobDatabase.query(ctx -> {
      ctx.fetch("CREATE TABLE id_and_name(id INTEGER, name VARCHAR(200), updated_at DATE);");
      ctx.fetch(
          "INSERT INTO id_and_name (id, name, updated_at) VALUES (1,'picard', '2004-10-19'),  (2, 'crusher', '2005-10-19'), (3, 'vash', '2006-10-19');");
      return null;
    });
    final Path tempFolder = Files.createTempDirectory(TEMP_PREFIX);

    databaseArchiver.exportDatabaseToArchive(tempFolder);

    final Set<String> exportedFiles = Files.walk(tempFolder)
        .map(Path::toString)
        .map(String::toLowerCase)
        .collect(Collectors.toSet());

    assertTrue(exportedFiles.stream().anyMatch(x -> x.contains("jobs")));
    assertFalse(exportedFiles.stream().anyMatch(x -> x.contains("id_and_name")));
  }

  @Test
  void testDatabaseExportImport() throws Exception {
    jobDatabase.query(ctx -> {
      ctx.fetch(
          "INSERT INTO jobs(id, scope, config_type, config, status, created_at, started_at, updated_at) VALUES "
              + "(1,'get_spec_scope', 'get_spec', '{ \"type\" : \"getSpec\" }', 'succeeded', '2004-10-19', null, '2004-10-19'), "
              + "(2,'sync_scope', 'sync', '{ \"job\" : \"sync\" }', 'running', '2005-10-19', null, '2005-10-19'), "
              + "(3,'sync_scope', 'sync', '{ \"job\" : \"sync\" }', 'pending', '2006-10-19', null, '2006-10-19');");
      return null;
    });
    final Path tempFolder = Files.createTempDirectory(TEMP_PREFIX);
    databaseArchiver.exportDatabaseToArchive(tempFolder);
    databaseArchiver.importDatabaseFromArchive(tempFolder, "test");
    // TODO check database state before/after
  }

  @Test
  void testPartialDatabaseImport() throws Exception {
    final Path tempFolder = Files.createTempDirectory(TEMP_PREFIX);
    databaseArchiver.exportDatabaseToArchive(tempFolder);
    Files.delete(DatabaseArchiver.buildTablePath(tempFolder.toRealPath(), JobsDatabaseSchema.ATTEMPTS.name()));
    assertThrows(RuntimeException.class, () -> databaseArchiver.importDatabaseFromArchive(tempFolder, "test"));
  }

}
