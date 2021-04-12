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

import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.server.converters.ConfigFileArchiver;
import io.airbyte.server.converters.DatabaseArchiver;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Optional;
import java.util.UUID;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ArchiveHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(ArchiveHandler.class);
  private static final String ARCHIVE_FILE_NAME = "airbyte_archive";
  private static final String VERSION_FILE_NAME = "VERSION";

  private final String version;
  private final ConfigRepository configRepository;
  private final ConfigFileArchiver configFileArchiver;
  private final DatabaseArchiver databaseArchiver;
  private final FileTtlManager fileTtlManager;

  public ArchiveHandler(final String version,
                        final ConfigRepository configRepository,
                        final JobPersistence persistence,
                        final FileTtlManager fileTtlManager) {
    this.version = version;
    this.configRepository = configRepository;
    configFileArchiver = new ConfigFileArchiver(configRepository);
    databaseArchiver = new DatabaseArchiver(persistence);
    this.fileTtlManager = fileTtlManager;
  }

  /**
   * Creates an archive tarball file using Gzip compression of internal Airbyte Data and
   *
   * @return that tarball File.
   */
  public File exportData() {
    try {
      final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), ARCHIVE_FILE_NAME);
      final File archive = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz").toFile();
      fileTtlManager.register(archive.toPath());
      try {
        exportVersionFile(tempFolder);
        configFileArchiver.exportConfigsToArchive(tempFolder);
        databaseArchiver.exportDatabaseToArchive(tempFolder);
        Archives.createArchive(tempFolder, archive.toPath());
      } catch (Exception e) {
        LOGGER.error("Export Data failed.");
        FileUtils.deleteQuietly(archive);
        throw new RuntimeException(e);
      } finally {
        FileUtils.deleteDirectory(tempFolder.toFile());
      }
      return archive;
    } catch (IOException e) {
      LOGGER.error("Export Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void exportVersionFile(Path tempFolder) throws IOException {
    final File versionFile = Files.createFile(tempFolder.resolve(VERSION_FILE_NAME)).toFile();
    FileUtils.writeStringToFile(versionFile, version, Charset.defaultCharset());
  }

  /**
   * Extract internal Airbyte data from the @param archive tarball file (using Gzip compression) as
   * produced by {@link #exportData()}. Note that the provided archived file will be deleted.
   *
   * @return a status object describing if import was successful or not.
   */
  public ImportRead importData(File archive) {
    // customerId before import happens.
    final Optional<UUID> previousCustomerIdOptional = getCurrentCustomerId();

    ImportRead result;
    try {
      final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive");
      try {
        Archives.extractArchive(archive.toPath(), tempFolder);
        checkImport(tempFolder);
        databaseArchiver.importDatabaseFromArchive(tempFolder, version);
        configFileArchiver.importConfigsFromArchive(tempFolder, false);
        result = new ImportRead().status(StatusEnum.SUCCEEDED);
      } finally {
        FileUtils.deleteDirectory(tempFolder.toFile());
        FileUtils.deleteQuietly(archive);
      }

      // identify this instance as the new customer id.
      TrackingClientSingleton.get().identify();
      // report that the previous customer id is now superseded by the imported one.
      previousCustomerIdOptional.ifPresent(previousCustomerId -> TrackingClientSingleton.get().alias(previousCustomerId.toString()));
    } catch (IOException | JsonValidationException | ConfigNotFoundException | RuntimeException e) {
      LOGGER.error("Import failed", e);
      result = new ImportRead().status(StatusEnum.FAILED).reason(e.getMessage());
    }

    return result;
  }

  private void checkImport(Path tempFolder) throws IOException, JsonValidationException, ConfigNotFoundException {
    final Path versionFile = tempFolder.resolve(VERSION_FILE_NAME);
    final String importVersion = Files.readString(versionFile, Charset.defaultCharset()).replace("\n", "").strip();
    LOGGER.info(String.format("Checking Airbyte Version to import %s", importVersion));
    if (AirbyteVersion.isCompatible(version, importVersion)) {
      throw new IOException(String.format("Imported VERSION (%s) is incompatible with current Airbyte version (%s).\n" +
          "Please upgrade your Airbyte Archive, see more at https://docs.airbyte.io/tutorials/upgrading-airbyte\n",
          importVersion, version));
    }
    databaseArchiver.checkVersion(version);
    // Check if all files to import are valid and with expected airbyte version
    configFileArchiver.importConfigsFromArchive(tempFolder, true);
  }

  private Optional<UUID> getCurrentCustomerId() {
    try {
      return Optional.of(configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true).getCustomerId());
    } catch (Exception e) {
      // because this is used for tracking we prefer to log instead of killing the import.
      LOGGER.error("failed to fetch current customerId.", e);
      return Optional.empty();
    }
  }

}
