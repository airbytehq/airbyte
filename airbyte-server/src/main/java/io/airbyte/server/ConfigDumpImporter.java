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
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Streams;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.ImportRead;
import io.airbyte.api.model.ImportRead.StatusEnum;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.MoreStreams;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.instance.jobs.JobsDatabaseSchema;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Optional;
import java.util.Set;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigDumpImporter {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigDumpImporter.class);
  private static final String CONFIG_FOLDER_NAME = "airbyte_config";
  private static final String DB_FOLDER_NAME = "airbyte_db";
  private static final String VERSION_FILE_NAME = "VERSION";
  private final ConfigRepository configRepository;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JobPersistence postgresPersistence;

  public ConfigDumpImporter(ConfigRepository configRepository, JobPersistence postgresPersistence) {
    this(configRepository, postgresPersistence, new JsonSchemaValidator());
  }

  @VisibleForTesting
  public ConfigDumpImporter(ConfigRepository configRepository, JobPersistence postgresPersistence, JsonSchemaValidator jsonSchemaValidator) {
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.postgresPersistence = postgresPersistence;
    this.configRepository = configRepository;
  }

  public ImportRead importDataWithSeed(String targetVersion, File archive, ConfigPersistence seedPersistence) {
    ImportRead result;
    try {
      final Path sourceRoot = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive");
      try {
        // 1. Unzip source
        Archives.extractArchive(archive.toPath(), sourceRoot);

        // 2. dry run
        try {
          checkImport(targetVersion, sourceRoot, seedPersistence);
        } catch (Exception e) {
          LOGGER.error("Dry run failed.", e);
          throw e;
        }

        // 3. Import Postgres content
        importDatabaseFromArchive(sourceRoot, targetVersion);

        // 4. Import Configs
        importConfigsFromArchive(sourceRoot, seedPersistence, false);

        // 5. Set DB version
        LOGGER.info("Setting the DB Airbyte version to : " + targetVersion);
        postgresPersistence.setVersion(targetVersion);

        // 6. check db version
        checkDBVersion(targetVersion);
        result = new ImportRead().status(StatusEnum.SUCCEEDED);
      } finally {
        FileUtils.deleteDirectory(sourceRoot.toFile());
        FileUtils.deleteQuietly(archive);
      }

      // identify this instance as the new customer id.
      configRepository.listStandardWorkspaces(true).forEach(workspace -> TrackingClientSingleton.get().identify(workspace.getWorkspaceId()));
    } catch (IOException | JsonValidationException | RuntimeException e) {
      LOGGER.error("Import failed", e);
      result = new ImportRead().status(StatusEnum.FAILED).reason(e.getMessage());
    }

    return result;
  }

  private void checkImport(String targetVersion, Path tempFolder, ConfigPersistence seedPersistence) throws IOException, JsonValidationException {
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
    importConfigsFromArchive(tempFolder, seedPersistence, true);
  }

  // Config
  private List<String> listDirectories(Path sourceRoot) throws IOException {
    try (Stream<Path> files = Files.list(sourceRoot.resolve(CONFIG_FOLDER_NAME))) {
      return files.map(c -> c.getFileName().toString())
          .collect(Collectors.toList());
    }
  }

  private <T> void importConfigsFromArchive(final Path sourceRoot, ConfigPersistence seedPersistence, final boolean dryRun)
      throws IOException, JsonValidationException {
    final Set<String> sourceDefinitionsInUse = new HashSet<>();
    final Set<String> destinationDefinitionsInUse = new HashSet<>();
    final boolean[] sourceProcessed = {false};
    final boolean[] destinationProcessed = {false};
    final List<String> directories = listDirectories(sourceRoot);
    // We sort the directories cause we want to process SOURCE_CONNECTION before
    // STANDARD_SOURCE_DEFINITION and DESTINATION_CONNECTION before STANDARD_DESTINATION_DEFINITION
    // so that we can identify which definitions should not be upgraded to the latest version
    Collections.sort(directories);
    final Map<AirbyteConfig, Stream<T>> data = new LinkedHashMap<>();

    final Map<ConfigSchema, Map<String, T>> seeds = getSeeds(seedPersistence);

    for (final String directory : directories) {
      final Optional<ConfigSchema> configSchemaOptional = Enums.toEnum(directory.replace(".yaml", ""), ConfigSchema.class);

      if (configSchemaOptional.isEmpty()) {
        continue;
      }

      final ConfigSchema configSchema = configSchemaOptional.get();
      Stream<T> configs = readConfigsFromArchive(sourceRoot, configSchema);

      // If there is no source or destination connection, mark them as processed respectively.
      if (configSchema == ConfigSchema.STANDARD_SOURCE_DEFINITION && !data.containsKey(ConfigSchema.SOURCE_CONNECTION)) {
        sourceProcessed[0] = true;
      } else if (configSchema == ConfigSchema.STANDARD_DESTINATION_DEFINITION && !data.containsKey(ConfigSchema.DESTINATION_CONNECTION)) {
        destinationProcessed[0] = true;
      }

      configs = streamWithAdditionalOperation(
          sourceDefinitionsInUse,
          destinationDefinitionsInUse,
          sourceProcessed,
          destinationProcessed,
          configSchema,
          configs,
          seeds);
      data.put(configSchema, configs);
    }
    configRepository.replaceAllConfigs(data, dryRun);
  }

  /**
   * Convert config dumps from {@link ConfigPersistence#dumpConfigs} to the desired format.
   */
  @SuppressWarnings("unchecked")
  private static <T> Map<ConfigSchema, Map<String, T>> getSeeds(ConfigPersistence configSeedPersistence) throws IOException {
    Map<ConfigSchema, Map<String, T>> allData = new HashMap<>(2);
    for (Map.Entry<String, Stream<JsonNode>> configStream : configSeedPersistence.dumpConfigs().entrySet()) {
      ConfigSchema configSchema = ConfigSchema.valueOf(configStream.getKey());
      Map<String, T> configSeeds = configStream.getValue()
          .map(node -> Jsons.object(node, configSchema.getClassName()))
          .collect(Collectors.toMap(
              configSchema::getId,
              object -> (T) object));
      allData.put(configSchema, configSeeds);
    }
    return allData;
  }

  private <T> Stream<T> streamWithAdditionalOperation(Set<String> sourceDefinitionsInUse,
                                                      Set<String> destinationDefinitionsInUse,
                                                      boolean[] sourceProcessed,
                                                      boolean[] destinationProcessed,
                                                      ConfigSchema configSchema,
                                                      Stream<T> configs,
                                                      Map<ConfigSchema, Map<String, T>> latestSeeds) {
    if (configSchema == ConfigSchema.SOURCE_CONNECTION) {
      sourceProcessed[0] = true;
      configs = configs.peek(config -> sourceDefinitionsInUse.add(((SourceConnection) config).getSourceDefinitionId().toString()));
    } else if (configSchema == ConfigSchema.DESTINATION_CONNECTION) {
      destinationProcessed[0] = true;
      configs = configs.peek(config -> destinationDefinitionsInUse.add(((DestinationConnection) config).getDestinationDefinitionId().toString()));
    } else if (configSchema == ConfigSchema.STANDARD_SOURCE_DEFINITION) {
      Map<String, T> sourceDefinitionSeeds = latestSeeds.get(configSchema);
      configs = getDefinitionStream(sourceDefinitionsInUse, sourceProcessed[0], configSchema, configs, sourceDefinitionSeeds);
    } else if (configSchema == ConfigSchema.STANDARD_DESTINATION_DEFINITION) {
      Map<String, T> destinationDefinitionSeeds = latestSeeds.get(configSchema);
      configs = getDefinitionStream(destinationDefinitionsInUse, destinationProcessed[0], configSchema, configs, destinationDefinitionSeeds);
    }
    return configs;
  }

  /**
   * This method combines the latest definitions with existing ones. If a connector is being used by
   * user, it will continue to be at the same version, otherwise it will be migrated to the latest
   * version
   */
  private <T> Stream<T> getDefinitionStream(Set<String> definitionsInUse,
                                            boolean definitionsPopulated,
                                            ConfigSchema configSchema,
                                            Stream<T> currentDefinitions,
                                            Map<String, T> latestDefinitions) {
    if (!definitionsPopulated) {
      throw new RuntimeException("Trying to process " + configSchema + " without populating the definitions in use");
    }

    return Streams.concat(
        // Keep all the definitions in use
        currentDefinitions.filter(c -> definitionsInUse.contains(configSchema.getId(c))),
        // Upgrade all the definitions not in use
        latestDefinitions.entrySet().stream().filter(c -> !definitionsInUse.contains(c.getKey())).map(Entry::getValue));
  }

  private <T> Stream<T> readConfigsFromArchive(final Path storageRoot, final ConfigSchema schemaType)
      throws IOException {

    final Path configPath = buildConfigPath(storageRoot, schemaType);
    if (configPath.toFile().exists()) {
      final String configStr = Files.readString(configPath);
      final JsonNode node = Yamls.deserialize(configStr);
      return StreamSupport
          .stream(Spliterators.spliteratorUnknownSize(node.elements(), Spliterator.ORDERED), false)
          .map(element -> {
            final T config = Jsons.object(element, schemaType.getClassName());
            try {
              validateJson(config, schemaType);
              return config;
            } catch (JsonValidationException e) {
              throw new RuntimeException(e);
            }
          });

    } else {
      throw new FileNotFoundException(
          String.format("Airbyte Configuration %s was not found in the archive", schemaType));
    }
  }

  private <T> void validateJson(final T config, final ConfigSchema configType) throws JsonValidationException {
    JsonNode schema = JsonSchemaValidator.getSchema(configType.getConfigSchemaFile());
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

  protected static Path buildConfigPath(final Path storageRoot, final ConfigSchema schemaType) {
    return storageRoot.resolve(CONFIG_FOLDER_NAME)
        .resolve(String.format("%s.yaml", schemaType.name()));
  }

  // Postgres Portion
  public void importDatabaseFromArchive(final Path storageRoot, final String airbyteVersion) throws IOException {
    try {
      final Map<JobsDatabaseSchema, Stream<JsonNode>> data = new HashMap<>();
      for (JobsDatabaseSchema tableType : JobsDatabaseSchema.values()) {
        final Path tablePath = buildTablePath(storageRoot, tableType.name());
        Stream<JsonNode> tableStream = readTableFromArchive(tableType, tablePath);

        if (tableType == JobsDatabaseSchema.AIRBYTE_METADATA) {
          tableStream = replaceDeploymentMetadata(postgresPersistence, tableStream);
        }

        data.put(tableType, tableStream);
      }
      postgresPersistence.importDatabase(airbyteVersion, data);
      LOGGER.info("Successful upgrade of airbyte postgres database from archive");
    } catch (Exception e) {
      LOGGER.warn("Postgres database version upgrade failed, reverting to state previous to migration.");
      throw e;
    }
  }

  /**
   * The deployment concept is specific to the environment that Airbyte is running in (not the data
   * being imported). Thus, if there is a deployment in the imported data, we filter it out. In
   * addition, before running the import, we look up the current deployment id, and make sure that
   * that id is inserted when we run the import.
   *
   * @param postgresPersistence - database that we are importing into.
   * @param metadataTableStream - stream of records to be imported into the metadata table.
   * @return modified stream with old deployment id removed and correct deployment id inserted.
   * @throws IOException - you never know when you IO.
   */
  static Stream<JsonNode> replaceDeploymentMetadata(JobPersistence postgresPersistence,
                                                    Stream<JsonNode> metadataTableStream)
      throws IOException {
    // filter out the deployment record from the import data, if it exists.
    Stream<JsonNode> stream = metadataTableStream
        .filter(record -> !record.get(DefaultJobPersistence.METADATA_KEY_COL).asText().equals(DefaultJobPersistence.DEPLOYMENT_ID_KEY));

    // insert the current deployment id, if it exists.
    final Optional<UUID> deploymentOptional = postgresPersistence.getDeployment();
    if (deploymentOptional.isPresent()) {
      final JsonNode deploymentRecord = Jsons.jsonNode(ImmutableMap.<String, String>builder()
          .put(DefaultJobPersistence.METADATA_KEY_COL, DefaultJobPersistence.DEPLOYMENT_ID_KEY)
          .put(DefaultJobPersistence.METADATA_VAL_COL, deploymentOptional.get().toString())
          .build());
      stream = Streams.concat(stream, Stream.of(deploymentRecord));
    }
    return stream;
  }

  protected static Path buildTablePath(final Path storageRoot, final String tableName) {
    return storageRoot
        .resolve(DB_FOLDER_NAME)
        .resolve(String.format("%s.yaml", tableName.toUpperCase()));
  }

  private Stream<JsonNode> readTableFromArchive(final JobsDatabaseSchema tableSchema,
                                                final Path tablePath)
      throws FileNotFoundException {
    final JsonNode schema = tableSchema.getTableDefinition();
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
