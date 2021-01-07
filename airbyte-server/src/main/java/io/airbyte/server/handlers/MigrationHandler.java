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

import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.server.converters.ConfigConverter;
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
import java.util.List;
import java.util.stream.Collectors;
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

  public MigrationHandler(final ConfigRepository configRepository) {
    this.configRepository = configRepository;
  }

  public Path exportData() {
    try {
      // Create temp folder where to export data
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      Path archive;
      try {
        exportAirbyteConfig(tempFolder);
        exportAirbyteDatabase(tempFolder);
        exportVersionFile(tempFolder);
        final Path archiveFile = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz");
        archiveFile.toFile().deleteOnExit();
        archive = createArchive(tempFolder, archiveFile);
      } finally {
        FileUtils.deleteDirectory(tempFolder.toFile());
      }
      return archive;
    } catch (IOException e) {
      LOGGER.error("Export Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void exportAirbyteConfig(Path tempFolder) {
    LOGGER.info(String.format("Exporting Airbyte Configs to %s", tempFolder));
    final ConfigConverter configConverter = new ConfigConverter(tempFolder, configRepository.getAirbyteVersion());
    Exceptions.toRuntime(() -> {
      configConverter.writeConfig(ConfigSchema.STANDARD_WORKSPACE, configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID));
      configConverter.writeConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, configRepository.listStandardSources());
      configConverter.writeConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, configRepository.listStandardDestinationDefinitions());
      configConverter.writeConfig(ConfigSchema.SOURCE_CONNECTION, configRepository.listSourceConnection());
      configConverter.writeConfig(ConfigSchema.DESTINATION_CONNECTION, configRepository.listDestinationConnection());
      final List<StandardSync> standardSyncs = configRepository.listStandardSyncs();
      configConverter.writeConfig(ConfigSchema.STANDARD_SYNC, standardSyncs);
      final List<StandardSyncSchedule> standardSchedules = standardSyncs
          .stream()
          .map(config -> Exceptions.toRuntime(() -> configRepository.getStandardSyncSchedule(config.getConnectionId())))
          .collect(Collectors.toList());
      configConverter.writeConfig(ConfigSchema.STANDARD_SYNC_SCHEDULE, standardSchedules);
    });
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

  static private Path createArchive(final Path tempFolder, final Path archiveFile) throws IOException {
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
