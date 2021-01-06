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

package io.airbyte.server.handlers;

import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DefaultConfigPersistence;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.FileVisitResult;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.SimpleFileVisitor;
import java.nio.file.attribute.BasicFileAttributes;
import java.util.zip.GZIPOutputStream;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MigrationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationHandler.class);
  private static final String ARCHIVE_FILE_NAME = "airbyte_config_data";
  private static final String VERSION_FILE_NAME = "VERSION";

  private final ConfigRepository configRepository;
  private final JobPersistence jobPersistence;

  public MigrationHandler(final ConfigRepository configRepository, final JobPersistence jobPersistence) {
    this.configRepository = configRepository;
    this.jobPersistence = jobPersistence;
  }

  public Path exportData() {
    try {
      // Create temp folder where to export data
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      FileUtils.forceDeleteOnExit(tempFolder.toFile());
      exportAirbyteConfig(tempFolder);
      exportAirbyteDatabase(tempFolder);
      exportVersionFile(tempFolder);
      final Path archive = createArchive(tempFolder);
      FileUtils.deleteDirectory(tempFolder.toFile());
      return archive;
    } catch (IOException e) {
      LOGGER.error("Export Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void exportAirbyteConfig(Path tempFolder) {
    LOGGER.info(String.format("Exporting Airbyte Configs to %s", tempFolder));

    // TODO Change persistence to YAML persistence instead of Default
    final ConfigPersistence persistence = new DefaultConfigPersistence(tempFolder, configRepository.getAirbyteVersion());
    final ConfigRepository tmpConfigRepository = new ConfigRepository(persistence);

    try {
      tmpConfigRepository.writeStandardWorkspace(configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID));
      configRepository.listStandardSources()
          .forEach(config -> {
            try {
              tmpConfigRepository.writeStandardSource(config);
            } catch (IOException | JsonValidationException e) {
              throw new RuntimeException(e);
            }
          });
      configRepository.listStandardDestinationDefinitions()
          .forEach(config -> {
            try {
              tmpConfigRepository.writeStandardDestinationDefinition(config);
            } catch (IOException | JsonValidationException e) {
              throw new RuntimeException(e);
            }
          });
      configRepository.listSourceConnection()
          .forEach(config -> {
            try {
              tmpConfigRepository.writeSourceConnection(config);
            } catch (IOException | JsonValidationException e) {
              throw new RuntimeException(e);
            }
          });
      configRepository.listDestinationConnection()
          .forEach(config -> {
            try {
              tmpConfigRepository.writeDestinationConnection(config);
            } catch (IOException | JsonValidationException e) {
              throw new RuntimeException(e);
            }
          });
      configRepository.listStandardSyncs()
          .forEach(config -> {
            try {
              tmpConfigRepository.writeStandardSync(config);
              tmpConfigRepository.writeStandardSchedule(configRepository.getStandardSyncSchedule(config.getConnectionId()));
            } catch (IOException | JsonValidationException | ConfigNotFoundException e) {
              throw new RuntimeException(e);
            }
          });
    } catch (IOException | JsonValidationException | ConfigNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

  private void exportAirbyteDatabase(Path tempFolder) {
    LOGGER.info(String.format("Exporting Airbyte Database to %s", tempFolder));
    // TODO implement
  }

  private void exportVersionFile(Path tempFolder) throws IOException {
    LOGGER.info(String.format("Exporting Airbyte Version to %s", tempFolder));
    final String currentVersion = configRepository.getAirbyteVersion();
    final File versionFile = Files.createFile(tempFolder.resolve(VERSION_FILE_NAME)).toFile();
    FileUtils.writeStringToFile(versionFile, currentVersion, Charset.defaultCharset());
  }

  private Path createArchive(Path tempFolder) throws IOException {
    final Path archiveFile = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz");
    archiveFile.toFile().deleteOnExit();
    LOGGER.info(String.format("Creating archive file in %s from %s", archiveFile, tempFolder));
    final TarArchiveOutputStream archive =
        new TarArchiveOutputStream(new GZIPOutputStream(new BufferedOutputStream(new FileOutputStream(archiveFile.toFile()))));
    Files.walkFileTree(tempFolder, new SimpleFileVisitor<>() {

      @Override
      public FileVisitResult visitFile(Path file, BasicFileAttributes attributes) {
        // only copy files, no symbolic links
        if (attributes.isSymbolicLink()) {
          return FileVisitResult.CONTINUE;
        }
        Path targetFile = tempFolder.relativize(file);
        try {
          compressFile(file, targetFile, archive);
        } catch (IOException e) {
          LOGGER.error(String.format("Failed to archive file %s: %s", file, e));
          throw new RuntimeException(e);
        }
        return FileVisitResult.CONTINUE;
      }

      @Override
      public FileVisitResult visitFileFailed(Path file, IOException exc) {
        LOGGER.error(String.format("Failed to include file %s in archive", file));
        return FileVisitResult.CONTINUE;
      }

    });
    archive.close();
    return archiveFile;
  }

  static private void compressFile(final Path file, final Path filename, final TarArchiveOutputStream archive) throws IOException {
    final TarArchiveEntry tarEntry = new TarArchiveEntry(file.toFile(), filename.toString());
    archive.putArchiveEntry(tarEntry);
    Files.copy(file, archive);
    archive.closeArchiveEntry();
  }

  public void importData(Path archive) {
    try {
      // Create temp folder where to extract archive
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      FileUtils.forceDeleteOnExit(tempFolder.toFile());
      // TODO Extract tarball to temp folder
      final String currentVersion = configRepository.getAirbyteVersion();
      // TODO Check VERSION file against currentVersion
      importAirbyteConfig(tempFolder);
      importAirbyteDatabase(tempFolder);
      FileUtils.deleteDirectory(tempFolder.toFile());
    } catch (IOException e) {
      LOGGER.error("Import Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void importAirbyteConfig(Path inputFolder) {
    // TODO implement
  }

  private void importAirbyteDatabase(Path inputFolder) {
    // TODO implement
  }

}
