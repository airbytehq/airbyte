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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.io.Resources;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DefaultConfigPersistence;
import io.airbyte.config.persistence.PersistenceConstants;
import io.airbyte.scheduler.persistence.DatabaseSchema;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigDumpImport {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigDumpImport.class);
  private static final String CONFIG_FOLDER_NAME = "airbyte_config";
  private static final String DB_FOLDER_NAME = "airbyte_db";
  private static final String VERSION_FILE_NAME = "VERSION";
  private final ConfigRepository configRepositoryToReadFrom;
  private final ConfigPersistence configPersistenceToWriteTo;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JobPersistence postgresPersistence;
  private final String targetVersion;
  private final String initialVersion;
  private final Path targetRootWithFolder;

  public ConfigDumpImport(Path targetRoot,
                          String targetConfigDirectoryName,
                          String initialVersion,
                          String targetVersion,
                          JobPersistence postgresPersistence,
                          ConfigRepository configRepositoryToReadFrom) {
    this.targetVersion = targetVersion;
    this.initialVersion = initialVersion;
    this.jsonSchemaValidator = new JsonSchemaValidator();
    this.configPersistenceToWriteTo = new DefaultConfigPersistence(targetRoot, jsonSchemaValidator,
        targetConfigDirectoryName);
    this.targetRootWithFolder = targetRoot.resolve(targetConfigDirectoryName);
    this.postgresPersistence = postgresPersistence;
    this.configRepositoryToReadFrom = configRepositoryToReadFrom;
  }

  @VisibleForTesting
  public Optional<UUID> getCurrentCustomerId() {
    try {
      return Optional.of(configRepositoryToReadFrom
          .getStandardWorkspace(PersistenceConstants.DEFAULT_WORKSPACE_ID, true).getCustomerId());
    } catch (Exception e) {
      // because this is used for tracking we prefer to log instead of killing the import.
      LOGGER.error("failed to fetch current customerId.", e);
      return Optional.empty();
    }
  }

  public ImportRead importData(File archive, boolean isUnitTest) {

    final Optional<UUID> previousCustomerIdOptional = getCurrentCustomerId();
    ImportRead result;
    try {
      final Path sourceRoot = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive");
      try {
        // 0. copy seeds
        copySeed(isUnitTest);

        // 1. Unzip source
        Archives.extractArchive(archive.toPath(), sourceRoot);

        // 2. Set DB version
        LOGGER.info("Setting the DB Airbyte version to : " + targetVersion);
        postgresPersistence.setVersion(targetVersion);

        // 3. dry run
        checkImport(sourceRoot);

        // 4. Import Postgres content
        importDatabaseFromArchive(sourceRoot, targetVersion);

        // 5. Import Configs
        importConfigsFromArchive(sourceRoot, false);
        result = new ImportRead().status(StatusEnum.SUCCEEDED);
      } finally {
        FileUtils.deleteDirectory(sourceRoot.toFile());
        FileUtils.deleteQuietly(archive);
      }

      // identify this instance as the new customer id.
      TrackingClientSingleton.get().identify();
      // report that the previous customer id is now superseded by the imported one.
      previousCustomerIdOptional.ifPresent(
          previousCustomerId -> TrackingClientSingleton.get().alias(previousCustomerId.toString()));
    } catch (IOException | JsonValidationException | RuntimeException e) {
      LOGGER.error("Import failed", e);
      result = new ImportRead().status(StatusEnum.FAILED).reason(e.getMessage());
    }

    return result;
  }

  public void copySeed(boolean isUnitTest) throws IOException {
    if (isUnitTest) {
      try {
        LOGGER.info("Running via unit test, trying to find latest seed in resources folder");
        Path path = Path.of(Resources.getResource("config").toURI());
        FileUtils.copyDirectory(path.toFile(), targetRootWithFolder.toFile());
      } catch (URISyntaxException e) {
        throw new RuntimeException(e);
      }
      return;
    }
    Path app = Path.of(System.getProperty("user.dir"));
    FileUtils.copyDirectory(app.resolve("latest_seeds").toFile(), targetRootWithFolder.toFile());
  }

  private void checkImport(Path tempFolder) throws IOException, JsonValidationException {
    final Path versionFile = tempFolder.resolve(VERSION_FILE_NAME);
    final String importVersion = Files.readString(versionFile, Charset.defaultCharset())
        .replace("\n", "").strip();
    LOGGER.info(String.format("Checking Airbyte Version to import %s", importVersion));
    if (!AirbyteVersion.isCompatible(targetVersion, importVersion)) {
      throw new IOException(String
          .format("Imported VERSION (%s) is incompatible with current Airbyte version (%s).\n" +
              "Please upgrade your Airbyte Archive, see more at https://docs.airbyte.io/tutorials/upgrading-airbyte\n",
              importVersion, targetVersion));
    }
    checkDBVersion(targetVersion);
    importConfigsFromArchive(tempFolder, true);
  }

  // Config
  private List<String> listDirectories(Path sourceRoot) throws IOException {
    try (Stream<Path> files = Files.list(sourceRoot.resolve(CONFIG_FOLDER_NAME))) {
      return files.map(c -> c.getFileName().toString())
          .collect(Collectors.toList());
    }
  }

  private void importConfigsFromArchive(final Path sourceRoot, final boolean dryRun)
      throws IOException, JsonValidationException {
    List<String> sourceDefinitionsToMigrate = new ArrayList<>();
    List<String> destinationDefinitionsToMigrate = new ArrayList<>();
    final boolean[] sourceProcessed = {false};
    final boolean[] destinationProcessed = {false};
    List<String> directories = listDirectories(sourceRoot);
    Collections.sort(directories);
    for (String directory : directories) {
      ConfigSchema configSchema = ConfigSchema.valueOf(directory.replace(".yaml", ""));
      readConfigsFromArchive(sourceRoot, configSchema).forEach(config -> {
        try {
          String id = configSchema.getId(config);
          if (configSchema == ConfigSchema.SOURCE_CONNECTION) {
            sourceDefinitionsToMigrate
                .add(((SourceConnection) config).getSourceDefinitionId().toString());
            sourceProcessed[0] = true;
          } else if (configSchema == ConfigSchema.DESTINATION_CONNECTION) {
            destinationDefinitionsToMigrate
                .add(((DestinationConnection) config).getDestinationDefinitionId().toString());
            destinationProcessed[0] = true;
          }

          if (configSchema == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
            if (!sourceProcessed[0]) {
              throw new RuntimeException(
                  "Trying to process source definition without processing sources");
            }

            if (!sourceDefinitionsToMigrate
                .contains(((StandardSourceDefinition) config).getSourceDefinitionId().toString())) {
              return;
            }
          } else if (configSchema == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
            if (!destinationProcessed[0]) {
              throw new RuntimeException(
                  "Trying to process destination definition without processing destinations");
            }

            if (!destinationDefinitionsToMigrate
                .contains(((StandardDestinationDefinition) config).getDestinationDefinitionId()
                    .toString())) {
              return;
            }
          }

          if (!dryRun) {
            configPersistenceToWriteTo.writeConfig(configSchema, id, config);
          }
        } catch (JsonValidationException | IOException e) {
          throw new RuntimeException(e);
        }
      });
    }
  }

  private <T> List<T> readConfigsFromArchive(final Path storageRoot, final ConfigSchema schemaType)
      throws IOException, JsonValidationException {
    final List<T> results = new ArrayList<>();
    final Path configPath = buildConfigPath(storageRoot, schemaType);
    if (configPath.toFile().exists()) {
      final String configStr = Files.readString(configPath);
      final JsonNode node = Yamls.deserialize(configStr);
      final Iterator<JsonNode> it = node.elements();
      while (it.hasNext()) {
        final JsonNode element = it.next();
        final T config = Jsons.object(element, schemaType.getClassName());
        validateJson(config, schemaType);
        results.add(config);
      }
      LOGGER.debug(String.format("Successful read of airbyte config %s from archive", schemaType));
    } else {
      throw new FileNotFoundException(
          String.format("Airbyte Configuration %s was not found in the archive", schemaType));
    }
    return results;
  }

  private <T> void validateJson(final T config, final ConfigSchema configType)
      throws JsonValidationException {
    JsonNode schema = JsonSchemaValidator.getSchema(configType.getFile());
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

  protected static Path buildConfigPath(final Path storageRoot, final ConfigSchema schemaType) {
    return storageRoot.resolve(CONFIG_FOLDER_NAME)
        .resolve(String.format("%s.yaml", schemaType.name()));
  }

  // Postgres Portion
  public void importDatabaseFromArchive(final Path storageRoot, final String airbyteVersion)
      throws IOException {
    try {
      final Map<DatabaseSchema, Stream<JsonNode>> data = new HashMap<>();
      for (DatabaseSchema tableType : DatabaseSchema.values()) {
        final Path tablePath = buildTablePath(storageRoot, tableType.name());
        data.put(tableType, readTableFromArchive(tableType, tablePath));
      }
      postgresPersistence.importDatabase(airbyteVersion, data);
      LOGGER.info("Successful upgrade of airbyte postgres database from archive");
    } catch (Exception e) {
      LOGGER.info("Postgres database version upgrade failed, setting DB version back to initial version");
      postgresPersistence.setVersion(initialVersion);
      throw e;
    }
  }

  protected static Path buildTablePath(final Path storageRoot, final String tableName) {
    return storageRoot
        .resolve(DB_FOLDER_NAME)
        .resolve(String.format("%s.yaml", tableName.toUpperCase()));
  }

  private Stream<JsonNode> readTableFromArchive(final DatabaseSchema tableSchema,
                                                final Path tablePath)
      throws FileNotFoundException {
    final JsonNode schema = tableSchema.toJsonNode();
    if (schema != null) {
      return MoreStreams.toStream(Yamls.deserialize(IOs.readFile(tablePath)).elements())
          .peek(r -> {
            try {
              jsonSchemaValidator.ensure(schema, r);
            } catch (JsonValidationException e) {
              throw new IllegalArgumentException(
                  "Archived Data Schema does not match current Airbyte Data Schemas", e);
            }
          });
    } else {
      throw new FileNotFoundException(String
          .format("Airbyte Database table %s was not found in the archive", tableSchema.name()));
    }
  }

  private void checkDBVersion(final String airbyteVersion) throws IOException {
    final Optional<String> airbyteDatabaseVersion = postgresPersistence.getVersion();
    airbyteDatabaseVersion
        .ifPresent(dbversion -> AirbyteVersion.assertIsCompatible(airbyteVersion, dbversion));
  }

}
