/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Streams;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.model.generated.UploadRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.server.errors.IdNotFoundKnownException;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.Spliterator;
import java.util.Spliterators;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import java.util.stream.StreamSupport;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@SuppressWarnings("PMD.AvoidReassigningLoopVariables")
public class ConfigDumpImporter {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigDumpImporter.class);
  private static final String CONFIG_FOLDER_NAME = "airbyte_config";
  private static final String VERSION_FILE_NAME = "VERSION";
  private static final Path TMP_AIRBYTE_STAGED_RESOURCES = Path.of("/tmp/airbyte_staged_resources");

  private final ConfigRepository configRepository;
  private final SecretsRepositoryWriter secretsRepositoryWriter;
  private final WorkspaceHelper workspaceHelper;
  private final JsonSchemaValidator jsonSchemaValidator;
  private final JobPersistence jobPersistence;
  private final boolean importDefinitions;

  public ConfigDumpImporter(final ConfigRepository configRepository,
                            final SecretsRepositoryWriter secretsRepositoryWriter,
                            final JobPersistence jobPersistence,
                            final WorkspaceHelper workspaceHelper,
                            final boolean importDefinitions) {
    this(configRepository, secretsRepositoryWriter, jobPersistence, workspaceHelper, new JsonSchemaValidator(), importDefinitions);
  }

  @VisibleForTesting
  public ConfigDumpImporter(final ConfigRepository configRepository,
                            final SecretsRepositoryWriter secretsRepositoryWriter,
                            final JobPersistence jobPersistence,
                            final WorkspaceHelper workspaceHelper,
                            final JsonSchemaValidator jsonSchemaValidator,
                            final boolean importDefinitions) {
    this.jsonSchemaValidator = jsonSchemaValidator;
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.secretsRepositoryWriter = secretsRepositoryWriter;
    this.workspaceHelper = workspaceHelper;
    this.importDefinitions = importDefinitions;
  }

  /**
   * Re-initialize the staged resource folder that contains uploaded artifacts when importing
   * workspaces. This is because they need to be done in two steps (two API endpoints), upload
   * resource first then import. When server starts, we flush the content of this folder, deleting
   * previously staged resources that were not imported yet.
   */
  public static void initStagedResourceFolder() {
    try {
      final File stagedResourceRoot = TMP_AIRBYTE_STAGED_RESOURCES.toFile();
      if (stagedResourceRoot.exists()) {
        FileUtils.forceDelete(stagedResourceRoot);
      }
      FileUtils.forceMkdir(stagedResourceRoot);
      FileUtils.forceDeleteOnExit(stagedResourceRoot);
    } catch (final IOException e) {
      throw new RuntimeException("Failed to create staging resource folder", e);
    }
  }

  public void importDataWithSeed(final AirbyteVersion targetVersion, final File archive, final ConfigPersistence seedPersistence)
      throws IOException, JsonValidationException {
    final Path sourceRoot = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive");
    try {
      // 1. Unzip source
      Archives.extractArchive(archive.toPath(), sourceRoot);

      // 2. dry run
      try {
        checkImport(targetVersion, sourceRoot);
        importConfigsFromArchive(sourceRoot, true);
      } catch (final Exception e) {
        LOGGER.error("Dry run failed.", e);
        throw e;
      }

      // 4. Import Configs and update connector definitions
      importConfigsFromArchive(sourceRoot, false);
      configRepository.loadDataNoSecrets(seedPersistence);

      // 5. Set DB version
      LOGGER.info("Setting the DB Airbyte version to : " + targetVersion);
      jobPersistence.setVersion(targetVersion.serialize());

      // 6. check db version
      checkDBVersion(targetVersion);
    } finally {
      FileUtils.deleteDirectory(sourceRoot.toFile());
      FileUtils.deleteQuietly(archive);
    }

    // identify this instance as the new customer id.
    configRepository.listStandardWorkspaces(true).forEach(workspace -> TrackingClientSingleton.get().identify(workspace.getWorkspaceId()));
  }

  private void checkImport(final AirbyteVersion targetVersion, final Path tempFolder) throws IOException {
    final Path versionFile = tempFolder.resolve(VERSION_FILE_NAME);
    final AirbyteVersion importVersion = new AirbyteVersion(Files
        .readString(versionFile, Charset.defaultCharset())
        .replace("\n", "")
        .strip());
    LOGGER.info(String.format("Checking Airbyte Version to import %s", importVersion));
    if (!AirbyteVersion.isCompatible(targetVersion, importVersion)) {
      throw new IOException(String
          .format("Imported VERSION (%s) is incompatible with current Airbyte version (%s).\n" +
              "Please upgrade your Airbyte Archive, see more at https://docs.airbyte.com/operator-guides/upgrading-airbyte\n",
              importVersion, targetVersion));
    }
  }

  // Config
  private List<String> listDirectories(final Path sourceRoot) throws IOException {
    try (final Stream<Path> files = Files.list(sourceRoot.resolve(CONFIG_FOLDER_NAME))) {
      return files.map(c -> c.getFileName().toString())
          .collect(Collectors.toList());
    }
  }

  private void importConfigsFromArchive(final Path sourceRoot, final boolean dryRun) throws IOException {
    final List<String> directories = listDirectories(sourceRoot);
    final Map<AirbyteConfig, Stream<?>> data = new LinkedHashMap<>();

    for (final String directory : directories) {
      final Optional<ConfigSchema> configSchemaOptional = Enums.toEnum(directory.replace(".yaml", ""), ConfigSchema.class);

      if (configSchemaOptional.isEmpty()) {
        continue;
      }

      final ConfigSchema configSchema = configSchemaOptional.get();
      data.put(configSchema, readConfigsFromArchive(sourceRoot, configSchema));
    }
    secretsRepositoryWriter.replaceAllConfigs(data, dryRun);
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
            } catch (final JsonValidationException e) {
              throw new RuntimeException(e);
            }
          });

    } else {
      throw new FileNotFoundException(
          String.format("Airbyte Configuration %s was not found in the archive", schemaType));
    }
  }

  private <T> void validateJson(final T config, final ConfigSchema configType) throws JsonValidationException {
    final JsonNode schema = JsonSchemaValidator.getSchema(configType.getConfigSchemaFile());
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

  protected static Path buildConfigPath(final Path storageRoot, final ConfigSchema schemaType) {
    return storageRoot.resolve(CONFIG_FOLDER_NAME)
        .resolve(String.format("%s.yaml", schemaType.name()));
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
  static Stream<JsonNode> replaceDeploymentMetadata(final JobPersistence postgresPersistence,
                                                    final Stream<JsonNode> metadataTableStream)
      throws IOException {
    // filter out the deployment record from the import data, if it exists.
    Stream<JsonNode> stream = metadataTableStream
        .filter(record -> !DefaultJobPersistence.DEPLOYMENT_ID_KEY.equals(record.get(DefaultJobPersistence.METADATA_KEY_COL).asText()));

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

  private void checkDBVersion(final AirbyteVersion airbyteVersion) throws IOException {
    final Optional<AirbyteVersion> airbyteDatabaseVersion = jobPersistence.getVersion().map(AirbyteVersion::new);
    airbyteDatabaseVersion
        .ifPresent(dbVersion -> AirbyteVersion.assertIsCompatible(airbyteVersion, dbVersion));
  }

  public UploadRead uploadArchiveResource(final File archive) {
    try {
      final UUID resourceId = UUID.randomUUID();
      FileUtils.moveFile(archive, TMP_AIRBYTE_STAGED_RESOURCES.resolve(resourceId.toString()).toFile());
      return new UploadRead()
          .status(UploadRead.StatusEnum.SUCCEEDED)
          .resourceId(resourceId);
    } catch (final IOException e) {
      LOGGER.error("Failed to upload archive resource", e);
      return new UploadRead().status(UploadRead.StatusEnum.FAILED);
    }
  }

  public File getArchiveResource(final UUID resourceId) {
    final File archive = TMP_AIRBYTE_STAGED_RESOURCES.resolve(resourceId.toString()).toFile();
    if (!archive.exists()) {
      throw new IdNotFoundKnownException("Archive Resource not found", resourceId.toString());
    }
    return archive;
  }

  public void deleteArchiveResource(final UUID resourceId) {
    final File archive = getArchiveResource(resourceId);
    FileUtils.deleteQuietly(archive);
  }

  public void importIntoWorkspace(final AirbyteVersion targetVersion, final UUID workspaceId, final File archive)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final Path sourceRoot = Files.createTempDirectory(Path.of("/tmp"), "airbyte_archive");
    try {
      // 1. Unzip source
      Archives.extractArchive(archive.toPath(), sourceRoot);

      // TODO: Auto-migrate archive?

      // 2. dry run
      try {
        checkImport(targetVersion, sourceRoot);
        importConfigsIntoWorkspace(sourceRoot, workspaceId, true);
      } catch (final Exception e) {
        LOGGER.error("Dry run failed.", e);
        throw e;
      }

      // 3. import configs
      importConfigsIntoWorkspace(sourceRoot, workspaceId, false);
    } finally {
      FileUtils.deleteDirectory(sourceRoot.toFile());
    }
  }

  private <T> void importConfigsIntoWorkspace(final Path sourceRoot, final UUID workspaceId, final boolean dryRun)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    // Keep maps of any re-assigned ids
    final Map<UUID, UUID> sourceIdMap = new HashMap<>();
    final Map<UUID, UUID> destinationIdMap = new HashMap<>();
    final Map<UUID, UUID> operationIdMap = new HashMap<>();

    final List<String> directories = listDirectories(sourceRoot);
    // We sort the directories because we want to process SOURCE_CONNECTION after
    // STANDARD_SOURCE_DEFINITION and DESTINATION_CONNECTION after STANDARD_DESTINATION_DEFINITION
    // so that we can identify which connectors should not be imported because the definitions are not
    // existing
    directories.sort(Comparator.reverseOrder());
    Stream<T> standardSyncs = null;

    for (final String directory : directories) {
      final Optional<ConfigSchema> configSchemaOptional = Enums.toEnum(directory.replace(".yaml", ""), ConfigSchema.class);

      if (configSchemaOptional.isEmpty()) {
        continue;
      }
      final ConfigSchema configSchema = configSchemaOptional.get();
      final Stream<T> configs = readConfigsFromArchive(sourceRoot, configSchema);

      if (dryRun) {
        continue;
      }

      switch (configSchema) {
        case STANDARD_SOURCE_DEFINITION -> {
          if (canImportDefinitions()) {
            importSourceDefinitionIntoWorkspace(configs);
          }
        }
        case SOURCE_CONNECTION -> sourceIdMap.putAll(importIntoWorkspace(
            ConfigSchema.SOURCE_CONNECTION,
            configs.map(c -> (SourceConnection) c),
            configRepository::listSourceConnection,
            (sourceConnection) -> !workspaceId.equals(sourceConnection.getWorkspaceId()),
            (sourceConnection, sourceId) -> {
              sourceConnection.setSourceId(sourceId);
              sourceConnection.setWorkspaceId(workspaceId);
              return sourceConnection;
            },
            (sourceConnection) -> {
              // make sure connector definition exists
              try {
                final StandardSourceDefinition sourceDefinition =
                    configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId());
                if (sourceDefinition == null) {
                  return;
                }
                if (sourceDefinition.getTombstone() != null && sourceDefinition.getTombstone()) {
                  return;
                }
                secretsRepositoryWriter.writeSourceConnection(sourceConnection, sourceDefinition.getSpec());
              } catch (final ConfigNotFoundException e) {
                return;
              }
            }));
        case STANDARD_DESTINATION_DEFINITION -> {
          if (canImportDefinitions()) {
            importDestinationDefinitionIntoWorkspace(configs);
          }
        }
        case DESTINATION_CONNECTION -> destinationIdMap.putAll(importIntoWorkspace(
            ConfigSchema.DESTINATION_CONNECTION,
            configs.map(c -> (DestinationConnection) c),
            configRepository::listDestinationConnection,
            (destinationConnection) -> !workspaceId.equals(destinationConnection.getWorkspaceId()),
            (destinationConnection, destinationId) -> {
              destinationConnection.setDestinationId(destinationId);
              destinationConnection.setWorkspaceId(workspaceId);
              return destinationConnection;
            },
            (destinationConnection) -> {
              // make sure connector definition exists
              try {
                final StandardDestinationDefinition destinationDefinition = configRepository.getStandardDestinationDefinition(
                    destinationConnection.getDestinationDefinitionId());
                if (destinationDefinition == null) {
                  return;
                }
                if (destinationDefinition.getTombstone() != null && destinationDefinition.getTombstone()) {
                  return;
                }
                secretsRepositoryWriter.writeDestinationConnection(destinationConnection, destinationDefinition.getSpec());
              } catch (final ConfigNotFoundException e) {
                return;
              }
            }));
        case STANDARD_SYNC -> standardSyncs = configs;
        case STANDARD_SYNC_OPERATION -> operationIdMap.putAll(importIntoWorkspace(
            ConfigSchema.STANDARD_SYNC_OPERATION,
            configs.map(c -> (StandardSyncOperation) c),
            configRepository::listStandardSyncOperations,
            (operation) -> !workspaceId.equals(operation.getWorkspaceId()),
            (operation, operationId) -> {
              operation.setOperationId(operationId);
              operation.setWorkspaceId(workspaceId);
              return operation;
            },
            configRepository::writeStandardSyncOperation));
        default -> {}
      }
    }

    if (standardSyncs != null) {
      // we import connections (standard sync) last to update reference to modified ids
      importIntoWorkspace(
          ConfigSchema.STANDARD_SYNC,
          standardSyncs.map(c -> (StandardSync) c),
          configRepository::listStandardSyncs,
          (standardSync) -> {
            try {
              return !workspaceId.equals(workspaceHelper.getWorkspaceForConnection(standardSync.getSourceId(), standardSync.getDestinationId()));
            } catch (final JsonValidationException | ConfigNotFoundException e) {
              return true;
            }
          },
          (standardSync, connectionId) -> {
            standardSync.setConnectionId(connectionId);
            standardSync.setSourceId(sourceIdMap.get(standardSync.getSourceId()));
            standardSync.setDestinationId(destinationIdMap.get(standardSync.getDestinationId()));
            standardSync.setOperationIds(standardSync.getOperationIds()
                .stream()
                .map(operationIdMap::get)
                .collect(Collectors.toList()));
            return standardSync;
          },
          (standardSync) -> {
            // make sure connectors definition exists
            try {
              if (configRepository.getSourceConnection(standardSync.getSourceId()) == null ||
                  configRepository.getDestinationConnection(standardSync.getDestinationId()) == null) {
                return;
              }
              for (final UUID operationId : standardSync.getOperationIds()) {
                if (configRepository.getStandardSyncOperation(operationId) == null) {
                  return;
                }
              }
            } catch (final ConfigNotFoundException e) {
              return;
            }
            configRepository.writeStandardSync(standardSync);
          });
    }
  }

  /**
   * Method that @return if this importer will import standard connector definitions or not
   */
  public boolean canImportDefinitions() {
    return importDefinitions;
  }

  protected <T> void importSourceDefinitionIntoWorkspace(final Stream<T> configs)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    importIntoWorkspace(
        ConfigSchema.STANDARD_SOURCE_DEFINITION,
        configs.map(c -> (StandardSourceDefinition) c),
        () -> configRepository.listStandardSourceDefinitions(false),
        (config) -> true,
        (config, id) -> {
          if (id.equals(config.getSourceDefinitionId())) {
            return config;
          } else {
            // a newId has been generated for this definition as it is in conflict with an existing one
            // here we return null, so we don't do anything to the old definition
            return null;
          }
        },
        (config) -> {
          if (config != null) {
            configRepository.writeStandardSourceDefinition(config);
          }
        });
  }

  protected <T> void importDestinationDefinitionIntoWorkspace(final Stream<T> configs)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    importIntoWorkspace(
        ConfigSchema.STANDARD_DESTINATION_DEFINITION,
        configs.map(c -> (StandardDestinationDefinition) c),
        () -> configRepository.listStandardDestinationDefinitions(false),
        (config) -> true,
        (config, id) -> {
          if (id.equals(config.getDestinationDefinitionId())) {
            return config;
          } else {
            // a newId has been generated for this definition as it is in conflict with an existing one
            // here we return null, so we don't do anything to the old definition
            return null;
          }
        },
        (config) -> {
          if (config != null) {
            configRepository.writeStandardDestinationDefinition(config);
          }
        });
  }

  private <T> Map<UUID, UUID> importIntoWorkspace(final ConfigSchema configSchema,
                                                  final Stream<T> configs,
                                                  final ListConfigCall<T> listConfigCall,
                                                  final Function<T, Boolean> filterConfigCall,
                                                  final MutateConfigCall<T> mutateConfig,
                                                  final PersistConfigCall<T> persistConfig)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final Map<UUID, UUID> idsMap = new HashMap<>();
    // To detect conflicts, we retrieve ids already in use by others for this ConfigSchema (ids from the
    // current workspace can be safely updated)
    final Set<UUID> idsInUse = listConfigCall.apply()
        .stream()
        .filter(filterConfigCall::apply)
        .map(configSchema::getId)
        .map(UUID::fromString)
        .collect(Collectors.toSet());
    for (T config : configs.collect(Collectors.toList())) {
      final UUID configId = UUID.fromString(configSchema.getId(config));
      final UUID configIdToPersist = idsInUse.contains(configId) ? UUID.randomUUID() : configId;
      config = mutateConfig.apply(config, configIdToPersist);
      if (config != null) {
        idsMap.put(configId, UUID.fromString(configSchema.getId(config)));
        persistConfig.apply(config);
      } else {
        idsMap.put(configId, configId);
      }
    }
    return idsMap;
  }

  /**
   * List all configurations of type @param &lt;T&gt; that already exists (we'll be using this to know
   * which ids are already in use)
   */
  public interface ListConfigCall<T> {

    Collection<T> apply() throws IOException, JsonValidationException, ConfigNotFoundException;

  }

  /**
   * Apply some modifications to the configuration with new ids
   */
  public interface MutateConfigCall<T> {

    T apply(T config, UUID newId) throws IOException, JsonValidationException, ConfigNotFoundException;

  }

  /**
   * Persist the configuration
   */
  public interface PersistConfigCall<T> {

    void apply(T config) throws JsonValidationException, IOException;

  }

}
