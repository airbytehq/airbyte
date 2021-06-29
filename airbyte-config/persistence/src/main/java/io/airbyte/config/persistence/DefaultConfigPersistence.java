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

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// we force all interaction with disk storage to be effectively single threaded.
public class DefaultConfigPersistence implements ConfigPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultConfigPersistence.class);
  private static final String CONFIG_DIR = "config";

  private static final Object lock = new Object();

  private final JsonSchemaValidator jsonSchemaValidator;
  private final Path storageRootWithConfigDirectory;
  private final Path storageRoot;

  public DefaultConfigPersistence(final Path storageRoot) {
    this(storageRoot, new JsonSchemaValidator());
  }

  public DefaultConfigPersistence(final Path storageRoot, final JsonSchemaValidator schemaValidator) {
    this.storageRoot = storageRoot;
    this.storageRootWithConfigDirectory = storageRoot.resolve(CONFIG_DIR);
    this.jsonSchemaValidator = schemaValidator;
  }

  @Override
  public <T> T getConfig(final ConfigSchema configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    synchronized (lock) {
      return getConfigInternal(configType, configId, clazz);
    }
  }

  @Override
  public <T> List<T> listConfigs(ConfigSchema configType, Class<T> clazz) throws JsonValidationException, IOException {
    synchronized (lock) {
      return listConfigsInternal(configType, clazz);
    }
  }

  @Override
  public <T> void writeConfig(ConfigSchema configType, String configId, T config) throws JsonValidationException, IOException {
    synchronized (lock) {
      writeConfigInternal(configType, configId, config, storageRootWithConfigDirectory);
    }
  }

  private <T> void writeConfig(ConfigSchema configType, String configId, T config, Path rootOverride) throws JsonValidationException, IOException {
    writeConfigInternal(configType, configId, config, rootOverride);
  }

  private <T> void writeConfigs(ConfigSchema configType, Stream<T> configs, Path rootOverride) {
    configs.forEach(config -> {
      String id = configType.getId(config);
      try {
        writeConfig(configType, id, config, rootOverride);
      } catch (JsonValidationException | IOException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    final Map<String, Stream<JsonNode>> configs = new HashMap<>();

    final List<String> directories = listDirectories();
    for (String directory : directories) {
      final List<JsonNode> configList = listConfig(directory);
      configs.put(directory, configList.stream());
    }
    return configs;
  }

  private List<String> listDirectories() throws IOException {
    try (Stream<Path> files = Files.list(storageRootWithConfigDirectory)) {
      return files.map(c -> c.getFileName().toString()).collect(Collectors.toList());
    }
  }

  private List<JsonNode> listConfig(String configType) throws IOException {
    final Path configTypePath = storageRootWithConfigDirectory.resolve(configType);
    if (!Files.exists(configTypePath)) {
      return Collections.emptyList();
    }
    try (Stream<Path> files = Files.list(configTypePath)) {
      final List<String> ids = files
          .filter(p -> !p.endsWith(".json"))
          .map(p -> p.getFileName().toString().replace(".json", ""))
          .collect(Collectors.toList());

      final List<JsonNode> configs = Lists.newArrayList();
      for (String id : ids) {
        try {
          final Path configPath = storageRootWithConfigDirectory.resolve(configType).resolve(String.format("%s.json", id));
          if (!Files.exists(configPath)) {
            throw new RuntimeException("Config NotFound");
          }

          final JsonNode config = Jsons.deserialize(Files.readString(configPath), JsonNode.class);
          configs.add(config);
        } catch (RuntimeException e) {
          throw new IOException(e);
        }
      }

      return configs;
    }
  }

  @Override
  public <T> void replaceAllConfigs(Map<ConfigSchema, Stream<T>> configs, boolean dryRun)
      throws IOException {
    // create a new folder
    String importDirectory = CONFIG_DIR + UUID.randomUUID().toString();
    Path rootOverride = storageRoot.resolve(importDirectory);
    Files.createDirectories(rootOverride);

    // write everything
    for (Map.Entry<ConfigSchema, Stream<T>> config : configs.entrySet()) {
      writeConfigs(config.getKey(), config.getValue(), rootOverride);
    }

    if (dryRun) {
      FileUtils.deleteDirectory(rootOverride.toFile());
      return;
    }

    boolean configToDeprecated = storageRootWithConfigDirectory.toFile().renameTo(storageRoot.resolve("config_deprecated").toFile());
    if (configToDeprecated) {
      LOGGER.info("Renamed config to config_deprecated successfully");
    }
    boolean newConfig = rootOverride.toFile().renameTo(storageRootWithConfigDirectory.toFile());
    if (newConfig) {
      LOGGER.info("Renamed " + importDirectory + " to config successfully");
    }

    LOGGER.info("Deleting config_deprecated");
    FileUtils.deleteDirectory(storageRoot.resolve("config_deprecated").toFile());

  }

  private <T> Optional<T> getConfigInternalWithoutValidation(ConfigSchema configType, String configId, Class<T> clazz) throws IOException {
    // validate file with schema
    final Path configPath = buildConfigPath(configType, configId, storageRootWithConfigDirectory);
    if (!Files.exists(configPath)) {
      return Optional.empty();
    } else {
      return Optional.of(Jsons.deserialize(Files.readString(configPath), clazz));
    }
  }

  private <T> T getConfigInternal(ConfigSchema configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final T config = getConfigInternalWithoutValidation(configType, configId, clazz)
        .orElseThrow(() -> new ConfigNotFoundException(configType, configId));

    validateJson(config, configType);

    return config;
  }

  private <T> List<T> listConfigsInternal(ConfigSchema configType, Class<T> clazz) throws JsonValidationException, IOException {
    final Path configTypePath = buildTypePath(configType, storageRootWithConfigDirectory);
    if (!Files.exists(configTypePath)) {
      return Collections.emptyList();
    }

    try (Stream<Path> files = Files.list(configTypePath)) {
      final List<String> ids = files
          .filter(p -> !p.endsWith(".json"))
          .map(p -> p.getFileName().toString().replace(".json", ""))
          .collect(Collectors.toList());

      final List<T> configs = Lists.newArrayList();
      for (String id : ids) {
        try {
          configs.add(getConfig(configType, id, clazz));
        } catch (ConfigNotFoundException e) {
          // should not happen since we just read the ids from disk.
          throw new IOException(e);
        }
      }

      return configs;
    }
  }

  private <T> void writeConfigInternal(ConfigSchema configType, String configId, T config, Path storageRootWithConfigDirectory)
      throws JsonValidationException, IOException {
    // validate config with schema
    validateJson(Jsons.jsonNode(config), configType);

    final Path configPath = buildConfigPath(configType, configId, storageRootWithConfigDirectory);
    Files.createDirectories(configPath.getParent());

    Files.writeString(configPath, Jsons.serialize(config));
  }

  private static Path buildConfigPath(ConfigSchema type, String configId, Path storageRootWithConfigDirectory) {
    return buildTypePath(type, storageRootWithConfigDirectory).resolve(String.format("%s.json", configId));
  }

  private static Path buildTypePath(ConfigSchema type, Path storageRootWithConfigDirectory) {
    return storageRootWithConfigDirectory.resolve(type.toString());
  }

  private <T> void validateJson(T config, ConfigSchema configType) throws JsonValidationException {
    JsonNode schema = JsonSchemaValidator.getSchema(configType.getFile());
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

}
