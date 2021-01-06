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

import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import java.io.BufferedOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.zip.GZIPOutputStream;
import org.apache.commons.compress.archivers.tar.TarArchiveEntry;
import org.apache.commons.compress.archivers.tar.TarArchiveOutputStream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MigrationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationHandler.class);
  private static final String ARCHIVE_FILE_NAME = "airbyte_config_data.tar.gz";
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
      // TODO deleteOnExit?
      final File archiveFile = tempFolder.resolve(ARCHIVE_FILE_NAME).toFile();
      final TarArchiveOutputStream archive =
          new TarArchiveOutputStream(new GZIPOutputStream(new BufferedOutputStream(new FileOutputStream(archiveFile))));
      exportAirbyteConfig(tempFolder, archive);
      exportAirbyteDatabase(tempFolder, archive);
      exportVersionFile(tempFolder, archive);
      archive.close();
      return archiveFile.toPath();
    } catch (IOException e) {
      LOGGER.error("Export Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void exportAirbyteConfig(Path tempFolder, TarArchiveOutputStream archive) {

  }

  private void exportAirbyteDatabase(Path tempFolder, TarArchiveOutputStream archive) {
    // TODO implement
  }

  private void exportVersionFile(Path tempFolder, TarArchiveOutputStream archive) throws IOException {
    final String currentVersion = configRepository.getAirbyteVersion();
    final File versionFile = Files.createFile(tempFolder.resolve(VERSION_FILE_NAME)).toFile();
    FileUtils.writeStringToFile(versionFile, currentVersion, Charset.defaultCharset());
    compressFile(versionFile, VERSION_FILE_NAME, archive);
  }

  static private void compressFile(final File file, final String filename, final TarArchiveOutputStream archive) throws IOException {
    final TarArchiveEntry tarEntry = new TarArchiveEntry(file, filename);
    archive.putArchiveEntry(tarEntry);
    Files.copy(file.toPath(), archive);
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
