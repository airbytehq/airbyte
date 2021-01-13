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

import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.db.Database;
import io.airbyte.server.converters.ConfigFileArchiver;
import io.airbyte.server.converters.DatabaseArchiver;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ArchiveHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(ArchiveHandler.class);
  private static final String ARCHIVE_FILE_NAME = "airbyte_archive";
  private static final String VERSION_FILE_NAME = "VERSION";

  private final String version;
  private final ConfigRepository configRepository;
  private final Database database;

  public ArchiveHandler(final String version, final ConfigRepository configRepository, final Database database) {
    this.version = version;
    this.configRepository = configRepository;
    this.database = database;
  }

  public File exportData() {
    try {
      final Path tempFolder = Files.createTempDirectory(ARCHIVE_FILE_NAME);
      final File archive = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz").toFile();
      archive.deleteOnExit();
      try {
        exportVersionFile(tempFolder);
        exportAirbyteConfig(tempFolder);
        exportAirbyteDatabase(tempFolder);
        Archives.createArchive(tempFolder, archive.toPath());
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

  private void exportAirbyteConfig(Path tempFolder) {
    LOGGER.info("Exporting Airbyte Configs");
    final ConfigFileArchiver configFileArchiver = new ConfigFileArchiver(tempFolder);
    Exceptions.toRuntime(() -> {
      final StandardWorkspace standardWorkspace = configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID);
      if (standardWorkspace != null)
        configFileArchiver.writeConfigsToArchive(ConfigSchema.STANDARD_WORKSPACE, List.of(standardWorkspace));
      configFileArchiver.writeConfigsToArchive(ConfigSchema.STANDARD_SOURCE_DEFINITION, configRepository.listStandardSources());
      configFileArchiver.writeConfigsToArchive(ConfigSchema.STANDARD_DESTINATION_DEFINITION, configRepository.listStandardDestinationDefinitions());
      configFileArchiver.writeConfigsToArchive(ConfigSchema.SOURCE_CONNECTION, configRepository.listSourceConnection());
      configFileArchiver.writeConfigsToArchive(ConfigSchema.DESTINATION_CONNECTION, configRepository.listDestinationConnection());
      final List<StandardSync> standardSyncs = configRepository.listStandardSyncs();
      configFileArchiver.writeConfigsToArchive(ConfigSchema.STANDARD_SYNC, standardSyncs);
      final List<StandardSyncSchedule> standardSchedules = standardSyncs
          .stream()
          .map(config -> Exceptions.toRuntime(() -> configRepository.getStandardSyncSchedule(config.getConnectionId())))
          .filter(Objects::nonNull)
          .collect(Collectors.toList());
      configFileArchiver.writeConfigsToArchive(ConfigSchema.STANDARD_SYNC_SCHEDULE, standardSchedules);
    });
  }

  private void exportAirbyteDatabase(Path tempFolder) {
    LOGGER.info("Exporting Airbyte Database");
    final DatabaseArchiver databaseArchiver = new DatabaseArchiver(database, tempFolder);
    Exceptions.toRuntime(databaseArchiver::writeDatabaseToArchive);
  }

  public ImportRead importData(File archive) {
    ImportRead result;
    try {
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      try {
        Archives.extractArchive(archive.toPath(), tempFolder);
        checkImport(tempFolder);
        checkAndImportAirbyteDatabase(tempFolder);
        importAirbyteConfig(tempFolder, false);
        result = new ImportRead().status(StatusEnum.SUCCEEDED);
      } finally {
        FileUtils.deleteDirectory(tempFolder.toFile());
        FileUtils.deleteQuietly(archive);
      }
    } catch (IOException | JsonValidationException e) {
      LOGGER.error("Import Data failed.");
      throw new RuntimeException(e);
    }
    return result;
  }

  private void checkImport(Path tempFolder) throws IOException, JsonValidationException {
    final Path versionFile = tempFolder.resolve(VERSION_FILE_NAME);
    final String importVersion = Files.readString(versionFile, Charset.defaultCharset());
    LOGGER.info(String.format("Checking Airbyte Version to import %s", importVersion));
    if (!importVersion.equals(version)) {
      throw new IOException(String.format("Version in VERSION file (%s) does not match current Airbyte version (%s)", importVersion, version));
    }
    // Check if all files to import are valid and with expected airbyte version
    importAirbyteConfig(tempFolder, true);
  }

  private void checkAndImportAirbyteDatabase(final Path tempFolder) throws IOException, JsonValidationException {
    final DatabaseArchiver databaseArchiver = new DatabaseArchiver(database, tempFolder);
    final String tempSchema = databaseArchiver.readDatabaseFromArchive();
    if (databaseArchiver.checkDatabase(tempSchema)) {
      databaseArchiver.commitDatabase(tempSchema);
    }
    databaseArchiver.dropSchema(tempSchema);
  }

  private void importAirbyteConfig(Path tempFolder, boolean dryRun) throws IOException, JsonValidationException {
    final ConfigFileArchiver configFileArchiver = new ConfigFileArchiver(tempFolder);
    if (dryRun) {
      configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class);
      configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
      configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
      configFileArchiver.readConfigsFromArchive(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
      configFileArchiver.readConfigsFromArchive(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
      configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_SYNC, StandardSync.class);
      configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_SYNC_SCHEDULE, StandardSyncSchedule.class);
    } else {
      Exceptions.toRuntime(() -> {
        configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardWorkspace(config)));
        configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSource(config)));
        configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardDestinationDefinition(config)));
        configFileArchiver.readConfigsFromArchive(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeSourceConnection(config)));
        configFileArchiver.readConfigsFromArchive(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeDestinationConnection(config)));
        configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_SYNC, StandardSync.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSync(config)));
        configFileArchiver.readConfigsFromArchive(ConfigSchema.STANDARD_SYNC_SCHEDULE, StandardSyncSchedule.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSchedule(config)));
      });
    }
  }

}
