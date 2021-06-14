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
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.google.common.io.Resources;
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DefaultConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.RunMigration;
import io.airbyte.server.converters.DatabaseArchiver;
import io.airbyte.server.handlers.ArchiveHandler;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.concurrent.TimeUnit;
import org.apache.commons.io.FileUtils;
import org.jetbrains.annotations.NotNull;
import org.junit.After;
import org.junit.jupiter.api.Test;

public class RunMigrationTest {

  private static final String INITIAL_VERSION = "0.17.0-alpha";
  private static final String TARGET_VERSION = "0.24.3-alpha";
  private final List<File> resourceToBeCleanedUp = new ArrayList<>();

  @After
  public void cleanup() {
    for (File file : resourceToBeCleanedUp) {
      FileUtils.deleteQuietly(file);
    }
  }

  @Test
  public void testRunMigration() {
    try (StubAirbyteDB stubAirbyteDB = new StubAirbyteDB()) {
      final File file = Path
          .of(Resources.getResource("migration/03a4c904-c91d-447f-ab59-27a43b52c2fd.gz").toURI())
          .toFile();

      Path exportConfigRoot = Path.of(Resources.getResource("migration/dummy_data").toURI());
      JobPersistence jobPersistence = getJobPersistence(stubAirbyteDB.getDatabase(), file,
          INITIAL_VERSION);
      assertDatabaseVersion(jobPersistence, INITIAL_VERSION);

      Path importRoot = getImportRoot();
      assertPreMigrationConfigs(importRoot);

      ArchiveHandler importArchiveHandler = new ArchiveHandler(TARGET_VERSION,
          new ConfigRepository(new DefaultConfigPersistence(importRoot)), jobPersistence,
          new FileTtlManager(10, TimeUnit.MINUTES, 10));

      runMigration(jobPersistence, exportConfigRoot, importArchiveHandler);

      assertDatabaseVersion(jobPersistence, TARGET_VERSION);
      assertPostMigrationConfigs(importRoot);

    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void assertDatabaseVersion(JobPersistence jobPersistence, String version)
      throws IOException {
    Optional<String> versionFromDb = jobPersistence.getVersion();
    assertTrue(versionFromDb.isPresent());
    assertEquals(versionFromDb.get(), version);
  }

  private void assertPostMigrationConfigs(Path importRoot)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    ConfigRepository configRepository = new ConfigRepository(
        new DefaultConfigPersistence(importRoot));
    assertEquals(configRepository.listStandardSyncs().size(), 2);
    assertEquals(configRepository.listDestinationConnection().size(), 2);
    assertEquals(configRepository.listSourceConnection().size(), 1);
    assertEquals(configRepository.listStandardWorkspaces(true).size(), 1);
  }

  private void assertPreMigrationConfigs(Path importRoot)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    ConfigRepository configRepository = new ConfigRepository(
        new DefaultConfigPersistence(importRoot));
    assertEquals(configRepository.listStandardSyncs().size(), 0);
    assertEquals(configRepository.listDestinationConnection().size(), 0);
    assertEquals(configRepository.listSourceConnection().size(), 0);
    // since we write dummy data in import
    assertEquals(configRepository.listStandardWorkspaces(true).size(), 1);
  }

  private void runMigration(JobPersistence jobPersistence,
                            Path exportConfigRoot,
                            ArchiveHandler importArchiveHandler)
      throws IOException {
    try (RunMigration runMigration = new RunMigration(
        INITIAL_VERSION,
        exportConfigRoot,
        importArchiveHandler,
        jobPersistence,
        TARGET_VERSION)) {

      runMigration.run();
    }
  }

  @NotNull
  private Path getImportRoot() throws IOException {
    final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), "final_config");
    Path standard_workspace = tempFolder.resolve("config").resolve("STANDARD_WORKSPACE")
        .resolve("5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6.json");
    Files.createDirectories(standard_workspace.getParent());
    Files.writeString(standard_workspace,
        "{\"workspaceId\":\"5ae6b09b-fdec-41af-aaf7-7d94cfc33ef6\",\"customerId\":\"17f90b72-5ae4-40b7-bc49-d6c2943aea57\",\"name\":\"default\",\"slug\":\"default\",\"initialSetupComplete\":true,\"anonymousDataCollection\":false,\"news\":false,\"securityUpdates\":false,\"displaySetupWizard\":false}");
    resourceToBeCleanedUp.add(tempFolder.toFile());
    return tempFolder;
  }

  private JobPersistence getJobPersistence(Database database,
                                           File file,
                                           String version)
      throws IOException {
    DefaultJobPersistence jobPersistence = new DefaultJobPersistence(database);
    final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), "db_init");
    resourceToBeCleanedUp.add(tempFolder.toFile());

    Archives.extractArchive(file.toPath(), tempFolder);
    DatabaseArchiver databaseArchiver = new DatabaseArchiver(jobPersistence);
    databaseArchiver.importDatabaseFromArchive(tempFolder, version);
    return jobPersistence;
  }

}
