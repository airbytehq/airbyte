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
import io.airbyte.commons.io.Archives;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.CloseableConsumer;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
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
import java.util.Map.Entry;
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
  private static final String DB_FOLDER_NAME = "airbyte_db";
  private static final String VERSION_FILE_NAME = "VERSION";
  private final ConfigRepository configRepository;
  private final JobPersistence jobPersistence;
  private final WorkspaceHelper workspaceHelper;

  public ConfigDumpExporter(ConfigRepository configRepository, JobPersistence jobPersistence, WorkspaceHelper workspaceHelper) {
    this.configRepository = configRepository;
    this.jobPersistence = jobPersistence;
    this.workspaceHelper = workspaceHelper;
  }

  public File dump() {
    try {
      final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), ARCHIVE_FILE_NAME);
      final File dump = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz").toFile();
      exportVersionFile(tempFolder);
      dumpConfigsDatabase(tempFolder);
      dumpJobsDatabase(tempFolder);

      Archives.createArchive(tempFolder, dump.toPath());
      return dump;
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  private void exportVersionFile(Path tempFolder) throws IOException {
    final String version = jobPersistence.getVersion().orElseThrow();
    final File versionFile = Files.createFile(tempFolder.resolve(VERSION_FILE_NAME)).toFile();
    FileUtils.writeStringToFile(versionFile, version, Charset.defaultCharset());
  }

  private void dumpJobsDatabase(Path parentFolder) throws Exception {
    final Map<String, Stream<JsonNode>> tables = jobPersistence.exportDatabase().entrySet().stream()
        .collect(Collectors.toMap(e -> e.getKey().name(), Entry::getValue));
    Files.createDirectories(parentFolder.resolve(DB_FOLDER_NAME));
    for (Map.Entry<String, Stream<JsonNode>> table : tables.entrySet()) {
      final Path tablePath = buildTablePath(parentFolder, table.getKey());
      writeTableToArchive(tablePath, table.getValue());
    }
  }

  private void writeTableToArchive(final Path tablePath, final Stream<JsonNode> tableStream) throws Exception {
    Files.createDirectories(tablePath.getParent());
    final BufferedWriter recordOutputWriter = new BufferedWriter(new FileWriter(tablePath.toFile()));
    final CloseableConsumer<JsonNode> recordConsumer = Yamls.listWriter(recordOutputWriter);
    tableStream.forEach(row -> Exceptions.toRuntime(() -> recordConsumer.accept(row)));
    recordConsumer.close();
  }

  protected static Path buildTablePath(final Path storageRoot, final String tableName) {
    return storageRoot
        .resolve(DB_FOLDER_NAME)
        .resolve(String.format("%s.yaml", tableName.toUpperCase()));
  }

  private void dumpConfigsDatabase(Path parentFolder) throws IOException {
    for (Map.Entry<String, Stream<JsonNode>> configEntry : configRepository.dumpConfigs().entrySet()) {
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

  public File exportWorkspace(UUID workspaceId) throws JsonValidationException, IOException, ConfigNotFoundException {
    final Path tempFolder = Files.createTempDirectory(Path.of("/tmp"), ARCHIVE_FILE_NAME);
    final File dump = Files.createTempFile(ARCHIVE_FILE_NAME, ".tar.gz").toFile();
    exportVersionFile(tempFolder);
    exportConfigsDatabase(tempFolder, workspaceId);

    Archives.createArchive(tempFolder, dump.toPath());
    return dump;
  }

  private void exportConfigsDatabase(Path parentFolder, UUID workspaceId) throws IOException, JsonValidationException, ConfigNotFoundException {
    final Collection<SourceConnection> sourceConnections = writeConfigsToArchive(
        parentFolder,
        ConfigSchema.SOURCE_CONNECTION.name(),
        configRepository::listSourceConnection,
        (sourceConnection) -> workspaceId.equals(sourceConnection.getWorkspaceId()));
    writeConfigsToArchive(parentFolder, ConfigSchema.STANDARD_SOURCE_DEFINITION.name(),
        () -> listSourceDefinition(sourceConnections),
        (config) -> true);

    final Collection<DestinationConnection> destinationConnections = writeConfigsToArchive(
        parentFolder,
        ConfigSchema.DESTINATION_CONNECTION.name(),
        configRepository::listDestinationConnection,
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
    for (StandardSync standardSync : configRepository.listStandardSyncs()) {
      if (workspaceHelper != null &&
          workspaceId.equals(workspaceHelper.getWorkspaceForConnection(standardSync.getSourceId(), standardSync.getDestinationId()))) {
        standardSyncs.add(standardSync);
      }
    }
    writeConfigsToArchive(parentFolder, ConfigSchema.STANDARD_SYNC.name(), standardSyncs.stream().map(Jsons::jsonNode));
  }

  private <T> Collection<T> writeConfigsToArchive(Path parentFolder,
                                                  String configSchemaName,
                                                  ListConfigCall<T> listConfigCall,
                                                  Function<T, Boolean> filterConfigCall)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final Collection<T> configs = listConfigCall.apply().stream().filter(filterConfigCall::apply).collect(Collectors.toList());
    writeConfigsToArchive(parentFolder, configSchemaName, configs.stream().map(Jsons::jsonNode));
    return configs;
  }

  private Collection<StandardSourceDefinition> listSourceDefinition(Collection<SourceConnection> sourceConnections)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final Map<UUID, StandardSourceDefinition> sourceDefinitionMap = new HashMap<>();
    for (SourceConnection sourceConnection : sourceConnections) {
      if (!sourceDefinitionMap.containsKey(sourceConnection.getSourceDefinitionId())) {
        sourceDefinitionMap
            .put(sourceConnection.getSourceDefinitionId(),
                configRepository.getStandardSourceDefinition(sourceConnection.getSourceDefinitionId()));
      }
    }
    return sourceDefinitionMap.values();
  }

  private Collection<StandardDestinationDefinition> listDestinationDefinition(Collection<DestinationConnection> destinationConnections)
      throws JsonValidationException, ConfigNotFoundException, IOException {
    final Map<UUID, StandardDestinationDefinition> destinationDefinitionMap = new HashMap<>();
    for (DestinationConnection destinationConnection : destinationConnections) {
      if (!destinationDefinitionMap.containsKey(destinationConnection.getDestinationDefinitionId())) {
        destinationDefinitionMap
            .put(destinationConnection.getDestinationDefinitionId(),
                configRepository.getStandardDestinationDefinition(destinationConnection.getDestinationDefinitionId()));
      }
    }
    return destinationDefinitionMap.values();
  }

  /**
   * List all configurations of type @param <T> that already exists
   */
  public interface ListConfigCall<T> {

    Collection<T> apply() throws IOException, JsonValidationException, ConfigNotFoundException;

  }

}
