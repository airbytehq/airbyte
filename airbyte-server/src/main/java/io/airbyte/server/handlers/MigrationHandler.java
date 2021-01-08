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

import io.airbyte.commons.io.ArchiveHelper;
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
import io.airbyte.server.converters.ConfigConverter;
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

public class MigrationHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(MigrationHandler.class);
  private static final String ARCHIVE_FILE_NAME = "airbyte_config_data";
  private static final String VERSION_FILE_NAME = "VERSION";

  private final String version;
  private final ConfigRepository configRepository;

  public MigrationHandler(final String version, final ConfigRepository configRepository) {
    this.version = version;
    this.configRepository = configRepository;
  }

  public Path exportData() {
    try {
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      final Path archive = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz");;
      archive.toFile().deleteOnExit();
      try {
        exportVersionFile(tempFolder);
        exportAirbyteConfig(tempFolder);
        exportAirbyteDatabase(tempFolder);
        ArchiveHelper.createArchive(tempFolder, archive);
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
    final ConfigConverter configConverter = new ConfigConverter(version, tempFolder);
    Exceptions.toRuntime(() -> {
      configConverter.writeConfigList(ConfigSchema.STANDARD_WORKSPACE,
          List.of(configRepository.getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID)));
      configConverter.writeConfigList(ConfigSchema.STANDARD_SOURCE_DEFINITION, configRepository.listStandardSources());
      configConverter.writeConfigList(ConfigSchema.STANDARD_DESTINATION_DEFINITION, configRepository.listStandardDestinationDefinitions());
      configConverter.writeConfigList(ConfigSchema.SOURCE_CONNECTION, configRepository.listSourceConnection());
      configConverter.writeConfigList(ConfigSchema.DESTINATION_CONNECTION, configRepository.listDestinationConnection());
      final List<StandardSync> standardSyncs = configRepository.listStandardSyncs();
      configConverter.writeConfigList(ConfigSchema.STANDARD_SYNC, standardSyncs);
      final List<StandardSyncSchedule> standardSchedules = standardSyncs
          .stream()
          .map(config -> Exceptions.toRuntime(() -> configRepository.getStandardSyncSchedule(config.getConnectionId())))
          .filter(Objects::nonNull)
          .collect(Collectors.toList());
      configConverter.writeConfigList(ConfigSchema.STANDARD_SYNC_SCHEDULE, standardSchedules);
    });
  }

  private void exportAirbyteDatabase(Path tempFolder) {
    LOGGER.info("Exporting Airbyte Database");
    // TODO implement
  }

  public void importData(Path archive) {
    try {
      final Path tempFolder = Files.createTempDirectory("airbyte_archive");
      try {
        ArchiveHelper.openArchive(tempFolder, archive);
        checkImport(tempFolder);
        importAirbyteConfig(tempFolder, false);
        importAirbyteDatabase(tempFolder, false);
      } finally {
        FileUtils.deleteDirectory(tempFolder.toFile());
      }
    } catch (IOException e) {
      LOGGER.error("Import Data failed.");
      throw new RuntimeException(e);
    }
  }

  private void checkImport(Path tempFolder) throws IOException {
    final Path versionFile = tempFolder.resolve(VERSION_FILE_NAME);
    final String importVersion = Files.readString(versionFile, Charset.defaultCharset());
    LOGGER.info(String.format("Checking Airbyte Version to import %s", importVersion));
    if (!importVersion.equals(version)) {
      throw new IOException(String.format("Version in VERSION file (%s) does not match current Airbyte version (%s)", importVersion, version));
    }
    // Check if all files to import are valid and with expected airbyte version
    importAirbyteConfig(tempFolder, true);
    importAirbyteDatabase(tempFolder, true);
  }

  private void importAirbyteConfig(Path tempFolder, boolean dryRun) throws IOException {
    final ConfigConverter configConverter = new ConfigConverter(version, tempFolder);
    if (dryRun) {
      configConverter.readConfigList(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class);
      configConverter.readConfigList(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
      configConverter.readConfigList(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
      configConverter.readConfigList(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
      configConverter.readConfigList(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
      configConverter.readConfigList(ConfigSchema.STANDARD_SYNC, StandardSync.class);
      configConverter.readConfigList(ConfigSchema.STANDARD_SYNC_SCHEDULE, StandardSyncSchedule.class);
    } else {
      Exceptions.toRuntime(() -> {
        configConverter.readConfigList(ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardWorkspace(config)));
        configConverter.readConfigList(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSource(config)));
        configConverter.readConfigList(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardDestinationDefinition(config)));
        configConverter.readConfigList(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeSourceConnection(config)));
        configConverter.readConfigList(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeDestinationConnection(config)));
        configConverter.readConfigList(ConfigSchema.STANDARD_SYNC, StandardSync.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSync(config)));
        configConverter.readConfigList(ConfigSchema.STANDARD_SYNC_SCHEDULE, StandardSyncSchedule.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSchedule(config)));
      });
    }
  }

  private void importAirbyteDatabase(Path tempFolder, boolean dryRun) {
    // TODO implement
  }

}
