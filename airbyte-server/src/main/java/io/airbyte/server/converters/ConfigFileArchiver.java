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

package io.airbyte.server.converters;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.lang.Exceptions;
import io.airbyte.commons.yaml.Yamls;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncSchedule;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Iterator;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigFileArchiver {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigFileArchiver.class);
  private static final String CONFIG_FOLDER_NAME = "airbyte_config";

  private final ConfigRepository configRepository;
  private final JsonSchemaValidator jsonSchemaValidator;

  public ConfigFileArchiver(final ConfigRepository configRepository, final JsonSchemaValidator jsonSchemaValidator) {
    this.configRepository = configRepository;
    this.jsonSchemaValidator = jsonSchemaValidator;
  }

  public ConfigFileArchiver(final ConfigRepository configRepository) {
    this(configRepository, new JsonSchemaValidator());
  }

  public void exportConfigsToArchive(final Path storageRoot) throws ConfigNotFoundException, IOException, JsonValidationException {
    writeConfigsToArchive(storageRoot, ConfigSchema.STANDARD_WORKSPACE, configRepository.listStandardWorkspaces(true));
    writeConfigsToArchive(storageRoot, ConfigSchema.STANDARD_SOURCE_DEFINITION, configRepository.listStandardSources());
    writeConfigsToArchive(storageRoot, ConfigSchema.STANDARD_DESTINATION_DEFINITION, configRepository.listStandardDestinationDefinitions());
    writeConfigsToArchive(storageRoot, ConfigSchema.SOURCE_CONNECTION, configRepository.listSourceConnection());
    writeConfigsToArchive(storageRoot, ConfigSchema.DESTINATION_CONNECTION, configRepository.listDestinationConnection());
    final List<StandardSync> standardSyncs = configRepository.listStandardSyncs();
    writeConfigsToArchive(storageRoot, ConfigSchema.STANDARD_SYNC, standardSyncs);
    final List<StandardSyncSchedule> standardSchedules = standardSyncs
        .stream()
        .map(config -> Exceptions.toRuntime(() -> configRepository.getStandardSyncSchedule(config.getConnectionId())))
        .filter(Objects::nonNull)
        .collect(Collectors.toList());
    writeConfigsToArchive(storageRoot, ConfigSchema.STANDARD_SYNC_SCHEDULE, standardSchedules);
  }

  /**
   * Takes configuration objects from @param configList with schema @param schemaType and serializes
   * them into a single archive file stored in YAML. Objects will be ordered by their String
   * representation in the archive.
   */
  private <T> void writeConfigsToArchive(final Path storageRoot, final ConfigSchema schemaType, final List<T> configList) throws IOException {
    final Path configPath = buildConfigPath(storageRoot, schemaType);
    Files.createDirectories(configPath.getParent());
    if (!configList.isEmpty()) {
      final List<T> sortedConfigs = configList.stream().sorted(Comparator.comparing(T::toString)).collect(Collectors.toList());
      Files.writeString(configPath, Yamls.serialize(sortedConfigs));
      LOGGER.debug(String.format("Successful export of airbyte config %s", schemaType));
    } else {
      // Create empty file
      Files.createFile(configPath);
    }
  }

  public void importConfigsFromArchive(final Path storageRoot, final boolean dryRun)
      throws IOException, JsonValidationException {
    Exceptions.toRuntime(() -> {
      if (dryRun) {
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class);
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
        readConfigsFromArchive(storageRoot, ConfigSchema.SOURCE_CONNECTION, SourceConnection.class);
        readConfigsFromArchive(storageRoot, ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class);
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_SYNC, StandardSync.class);
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_SYNC_SCHEDULE, StandardSyncSchedule.class);
      } else {
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_WORKSPACE, StandardWorkspace.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardWorkspace(config)));
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSource(config)));
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardDestinationDefinition(config)));
        readConfigsFromArchive(storageRoot, ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeSourceConnection(config)));
        readConfigsFromArchive(storageRoot, ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeDestinationConnection(config)));
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_SYNC, StandardSync.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSync(config)));
        readConfigsFromArchive(storageRoot, ConfigSchema.STANDARD_SYNC_SCHEDULE, StandardSyncSchedule.class)
            .forEach(config -> Exceptions.toRuntime(() -> configRepository.writeStandardSchedule(config)));
        LOGGER.debug("Successful import of airbyte configs");
      }
    });
  }

  /**
   * Reads a YAML configuration archive file and deserializes them into a list of configuration
   * objects. The objects will be validated against the current version of Airbyte server's JSON
   * Schema @param schemaType.
   */
  private <T> List<T> readConfigsFromArchive(final Path storageRoot, final ConfigSchema schemaType, final Class<T> clazz)
      throws IOException, JsonValidationException {
    final List<T> results = new ArrayList<>();
    final Path configPath = buildConfigPath(storageRoot, schemaType);
    if (configPath.toFile().exists()) {
      final String configStr = Files.readString(configPath);
      final JsonNode node = Yamls.deserialize(configStr);
      final Iterator<JsonNode> it = node.elements();
      while (it.hasNext()) {
        final JsonNode element = it.next();
        final T config = Jsons.object(element, clazz);
        validateJson(config, schemaType);
        results.add(config);
      }
      LOGGER.debug(String.format("Successful read of airbyte config %s from archive", schemaType));
    } else {
      throw new FileNotFoundException(String.format("Airbyte Configuration %s was not found in the archive", schemaType));
    }
    return results;
  }

  private <T> void validateJson(final T config, final ConfigSchema configType) throws JsonValidationException {
    JsonNode schema = JsonSchemaValidator.getSchema(configType.getFile());
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

  protected static Path buildConfigPath(final Path storageRoot, final ConfigSchema schemaType) {
    return storageRoot.resolve(CONFIG_FOLDER_NAME)
        .resolve(String.format("%s.yaml", schemaType.name()));
  }

}
