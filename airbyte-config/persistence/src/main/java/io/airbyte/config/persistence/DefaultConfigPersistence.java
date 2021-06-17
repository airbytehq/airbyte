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
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Consumer;
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

  public DefaultConfigPersistence(final Path storageRootConfig) {
    this(storageRootConfig, new JsonSchemaValidator());
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
      writeConfigInternal(configType, configId, config, Optional.empty());
    }
  }

  private <T> void writeConfig(ConfigSchema configType, String configId, T config, Path source) throws JsonValidationException, IOException {
    writeConfigInternal(configType, configId, config, Optional.of(source));
  }

  private <T> void writeConfigs(ConfigSchema configType, Stream<T> configs, Path source) {
    configs.forEach(config -> {
      String id = configType.getId(config);
      try {
        writeConfig(configType, id, config, source);
      } catch (JsonValidationException | IOException e) {
        throw new RuntimeException(e);
      }
    });
  }

  private <T> void validateConfigs(ConfigSchema configType, Stream<T> configs) {
    configs.forEach(config -> {
      try {
        validateJson(config, configType);
      } catch (JsonValidationException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public <T> void atomicConfigImport(Map<ConfigSchema, Stream<T>> configs,
                                     boolean dryRun,
                                     Consumer<Path> prePopulate)
      throws IOException {
    if (dryRun) {
      for (Map.Entry<ConfigSchema, Stream<T>> config : configs.entrySet()) {
        validateConfigs(config.getKey(), config.getValue());
      }
      return;
    }

    // create a new folder
    String importDirectory = CONFIG_DIR + UUID.randomUUID().toString();
    Path importInto = storageRoot.resolve(importDirectory);
    Files.createDirectories(importInto);

    // pre populate new folder with data
    prePopulate.accept(importInto);

    // write everything
    for (Map.Entry<ConfigSchema, Stream<T>> config : configs.entrySet()) {
      writeConfigs(config.getKey(), config.getValue(), importInto);
    }

    boolean configToDeprecated = storageRootWithConfigDirectory.toFile().renameTo(storageRoot.resolve("config_deprecated").toFile());
    if (configToDeprecated) {
      LOGGER.info("Renamed config to config_deprecated successfully");
    }
    boolean newConfig = importInto.toFile().renameTo(storageRootWithConfigDirectory.toFile());
    if (newConfig) {
      LOGGER.info("Renamed " + importDirectory + " to config successfully");
    }

    LOGGER.info("Deleting config_deprecated");
    FileUtils.deleteDirectory(storageRoot.resolve("config_deprecated").toFile());

  }

  private <T> T getConfigInternal(ConfigSchema configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    // validate file with schema
    final Path configPath = buildConfigPath(configType, configId, Optional.empty());
    if (!Files.exists(configPath)) {
      throw new ConfigNotFoundException(configType, configId);
    }

    final T config = Jsons.deserialize(Files.readString(configPath), clazz);
    validateJson(config, configType);

    return config;
  }

  private <T> List<T> listConfigsInternal(ConfigSchema configType, Class<T> clazz) throws JsonValidationException, IOException {
    final Path configTypePath = buildTypePath(configType, Optional.empty());
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

  private <T> void writeConfigInternal(ConfigSchema configType, String configId, T config, Optional<Path> source)
      throws JsonValidationException, IOException {
    // validate config with schema
    validateJson(Jsons.jsonNode(config), configType);

    final Path configPath = buildConfigPath(configType, configId, source);
    Files.createDirectories(configPath.getParent());

    Files.writeString(configPath, Jsons.serialize(config));
  }

  private Path buildConfigPath(ConfigSchema type, String configId, Optional<Path> source) {
    return buildTypePath(type, source).resolve(String.format("%s.json", configId));
  }

  private Path buildTypePath(ConfigSchema type, Optional<Path> source) {
    return source.map(path -> path.resolve(type.toString()))
        .orElseGet(() -> storageRootWithConfigDirectory.resolve(type.toString()));
  }

  private <T> void validateJson(T config, ConfigSchema configType) throws JsonValidationException {
    JsonNode schema = JsonSchemaValidator.getSchema(configType.getFile());
    jsonSchemaValidator.ensure(schema, Jsons.jsonNode(config));
  }

}
