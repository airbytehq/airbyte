/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.File;
import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.Function;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.io.FileUtils;

// TODO: Write a test case which compares the output dump with the output of ArchiveHandler export
// for the same data

/**
 * This class acts like export method of ArchiveHandler but the difference is 1. It takes a full
 * dump of whatever is available in the config directory without any schema validation. We dont want
 * schema validation because in case of automatic migration, the code that is going to do the schema
 * validation is from new version but the data in the config files is old. Thus schema validation
 * would fail. 2. Unlike ArchiveHandler, this doesn't take the dump of specific files but looks at
 * the config directory and takes the full dump of whatever is available
 */
public class ConfigDumpExporter {

  private static final String ARCHIVE_FILE_NAME = "airbyte_config_dump";
  private static final String CONFIG_FOLDER_NAME = "airbyte_config";
  private static final String VERSION_FILE_NAME = "VERSION";
  private final ConfigRepository configRepository;
  private final SecretsRepositoryReader secretsRepositoryReader;
  private final JobPersistence jobPersistence;
  private final WorkspaceHelper workspaceHelper;

  public ConfigDumpExporter(final ConfigRepository configRepository,
                            final SecretsRepositoryReader secretsRepositoryReader,
                            final JobPersistence jobPersistence,
                            final WorkspaceHelper workspaceHelper) {
    this.configRepository = configRepository;
    this.secretsRepositoryReader = secretsRepositoryReader;
    this.jobPersistence = jobPersistence;
    this.workspaceHelper = workspaceHelper;
  }

  public File dump() {
    try {
      final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), ARCHIVE_FILE_NAME);
      final File dump = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz").toFile();
      exportVersionFile(tempFolder);
      dumpConfigsDatabase(tempFolder);

      Archives.createArchive(tempFolder, dump.toPath());
      return dump;
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void exportVersionFile(final Path tempFolder) throws IOException {
    final String version = jobPersistence.getVersion().orElseThrow();
    final File versionFile = Files.createFile(tempFolder.resolve(VERSION_FILE_NAME)).toFile();
    FileUtils.writeStringToFile(versionFile, version, Charset.defaultCharset());
  }

  private void dumpConfigsDatabase(final Path parentFolder) throws IOException {
    for (final Map.Entry<String, Stream<JsonNode>> configEntry : secretsRepositoryReader.dumpConfigsWithSecrets().entrySet()) {
      writeConfigsToArchive(parentFolder, configEntry.getKey(), configEntry.getValue());
    }
  }

  private static void writeConfigsToArchive(final Path storageRoot,
                                            final String schemaType,
                                            final Stream<JsonNode> configs)
      throws IOException {
    writeConfigsToArchive(storageRoot, schemaType, configs.collect(Collectors.toList()));
  }

  private static void writeConfigsToArchive(final Path storageRoot,
                                            final String schemaType,
                                            final List<JsonNode> configList)
      throws IOException {
    final Path configPath = buildConfigPath(storageRoot, schemaType);
    Files.createDirectories(configPath.getParent());
    if (!configList.isEmpty()) {
      final List<JsonNode> sortedConfigs = configList.stream()
          .sorted(Comparator.comparing(JsonNode::toString)).collect(
              Collectors.toList());
      Files.writeString(configPath, Yamls.serialize(sortedConfigs));
    } else {
      // Create empty file
      Files.createFile(configPath);
    }
  }

  private static Path buildConfigPath(final Path storageRoot, final String schemaType) {
    return storageRoot.resolve(CONFIG_FOLDER_NAME)
        .resolve(String.format("%s.yaml", schemaType));
  }

  public File exportWorkspace(final UUID workspaceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), ARCHIVE_FILE_NAME);
    final File dump = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz").toFile();
    exportVersionFile(tempFolder);
    exportConfigsDatabase(tempFolder, workspaceId);

    Archives.createArchive(tempFolder, dump.toPath());
    return dump;
  }

  private void exportConfigsDatabase(final Path parentFolder, final UUID workspaceId)
      throws IOException, JsonValidationException, ConfigNotFoundException {
    final Collection<SourceConnection> sourceConnections = writeConfigsToArchive(
        parentFolder,
        ConfigSchema.SOURCE_CONNECTION.name(),
        secretsRepositoryReader::listSourceConnectionWithSecrets,
        (sourceConnection) -> workspaceId.equals(sourceConnection.getWorkspaceId()));
    writeConfigsToArchive(parentFolder, ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        () -> listSourceDefinition(sourceConnections),
        (config) -> true);

    final Collection<DestinationConnection> destinationConnections = writeConfigsToArchive(
        parentFolder,
        ConfigSchema.DESTINATION_CONNECTION.name(),
        secretsRepositoryReader::listDestinationConnectionWithSecrets,
        (destinationConnection) -> workspaceId.equals(destinationConnection.getWorkspaceId()));
    writeConfigsToArchive(parentFolder, ConfigSchema.STANDARD_DESTINATION_DEFINITION.name(),
        () -> listDestinationDefinition(destinationConnections),
        (config) -> true);

    writeConfigsToArchive(
        parentFolder,
        ConfigSchema.STANDARD_SYNC_OPERATION.name(),
        configRepository::listStandardSyncOperations,
        (operation) -> workspaceId.equals(operation.getWorkspaceId()));

    final List<StandardSync> standardSyncs = new ArrayList<>();
    for (final StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (workspaceHelper != null &&
          workspaceId.equals(workspaceHelper.getWorkspaceForConnection(standardSync.getSourceId(), standardSync.getDestinationId()))) {
        standardSyncs.add(standardSync);
      }
    }
    writeConfigsToArchive(parentFolder, ConfigSchema.STANDARD_SYNC.name(), standardSyncs.stream().map(Jsons::jsonNode));
  }

  private <T> Collection<T> writeConfigsToArchive(final Path parentFolder,
                                                  final String configSchemaName,
                                                  final ListConfigCall<T> listConfigCall,
                                                  final Function<T, Boolean> filterConfigCall)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final Collection<T> configs = listConfigCall.apply().stream().filter(filterConfigCall::apply).collect(Collectors.toList());
    writeConfigsToArchive(parentFolder, configSchemaName, configs.stream().map(Jsons::jsonNode));
    return configs;
  }

  private Collection<StandardSourceDefinition> listSourceDefinition(final Collection<SourceConnection> sourceConnections)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final Map<UUID, StandardSourceDefinition> sourceDefinitionMap = new HashMap<>();
    for (final SourceConnection sourceConnection : sourceConnections) {
      if (!sourceDefinitionMap.containsKey(sourceConnection.getSourceDefinitionId())) {
        sourceDefinitionMap
            .put(sourceConnection.getSourceDefinitionId(),
                configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId()));
      }
    }
    return sourceDefinitionMap.values();
  }

  private Collection<StandardDestinationDefinition> listDestinationDefinition(final Collection<DestinationConnection> destinationConnections)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final Map<UUID, StandardDestinationDefinition> destinationDefinitionMap = new HashMap<>();
    for (final DestinationConnection destinationConnection : destinationConnections) {
      if (!destinationDefinitionMap.containsKey(destinationConnection.getDestinationDefinitionId())) {
        destinationDefinitionMap
            .put(destinationConnection.getDestinationDefinitionId(),
                configRepository.getStandardDestinationDefinition(destinationConnection.getDestinationDefinitionId()));
      }
    }
    return destinationDefinitionMap.values();
  }

  /**
   * List all configurations of type @param &lt;T&gt; that already exists
   */
  public interface ListConfigCall<T> {

    Collection<T> apply() throws IOException, JsonValidationException, ConfigNotFoundException;

  }

}
