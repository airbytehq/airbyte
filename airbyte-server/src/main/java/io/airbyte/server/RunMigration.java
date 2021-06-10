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

package io.airbyte.server;

import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.migrate.MigrateConfig;
import io.airbyte.migrate.MigrationRunner;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.handlers.ArchiveHandler;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RunMigration implements Runnable, AutoCloseable {

  private static final Logger LOGGER = LoggerFactory.getLogger(RunMigration.class);
  private final ArchiveHandler importArchiveHandler;
  private final JobPersistence jobPersistence;
  private final String targetVersion;
  private final String initialVersion;
  private boolean isSuccessful;
  private boolean dbVersionChanged;
  private final ConfigDumpExport configDumpExport;
  private final List<File> filesToBeCleanedUp = new ArrayList<>();

  public RunMigration(String initialVersion,
                      Path exportConfigRoot,
                      ArchiveHandler importArchiveHandler,
                      JobPersistence jobPersistence,
                      String targetVersion) {
    this.initialVersion = initialVersion;
    this.jobPersistence = jobPersistence;
    this.targetVersion = targetVersion;
    this.configDumpExport = new ConfigDumpExport(exportConfigRoot, jobPersistence, initialVersion);
    this.importArchiveHandler = importArchiveHandler;

    this.isSuccessful = false;
    this.dbVersionChanged = false;
  }

  @Override
  public void run() {
    try {
      // Export data
      File exportData = configDumpExport.dump();
      filesToBeCleanedUp.add(exportData);

      // Define output target
      final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive_output");
      final File output = Files.createTempFile(tempFolder, "airbyte_archive_output", ".tar.gz")
          .toFile();
      filesToBeCleanedUp.add(output);
      filesToBeCleanedUp.add(tempFolder.toFile());

      // Run Migration
      MigrateConfig migrateConfig = new MigrateConfig(exportData.toPath(), output.toPath(),
          targetVersion);
      MigrationRunner.run(migrateConfig);

      // Update DB version
      LOGGER.info("Setting the DB Airbyte version to : " + targetVersion);
      jobPersistence.setVersion(targetVersion);
      dbVersionChanged = true;

      // Import data
      ImportRead importRead = importArchiveHandler.importData(output);
      if (importRead.getStatus() == StatusEnum.FAILED) {
        throw new RuntimeException("Automatic migration failed : " + importRead.getReason());
      }

      isSuccessful = true;
      configDumpExport.deleteOrphanDirectories();
    } catch (IOException e) {
      throw new RuntimeException("Automatic migration failed", e);
    }
  }

  @Override
  public void close() throws IOException {
    if (!isSuccessful && dbVersionChanged) {
      LOGGER.warn("Automatic Migration not successful, setting the DB Airbyte version back to : "
          + initialVersion);
      jobPersistence.setVersion(initialVersion);
    }
    for (File file : filesToBeCleanedUp) {
      if (!FileUtils.deleteQuietly(file)) {
        LOGGER.warn("Could not delete file/directory : " + file.toString());
      }
    }
  }

}
