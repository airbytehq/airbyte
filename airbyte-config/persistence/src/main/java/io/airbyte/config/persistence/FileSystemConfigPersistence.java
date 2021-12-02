/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.api.client.util.Preconditions;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.io.FileUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// we force all interaction with disk storage to be effectively single threaded.
public class FileSystemConfigPersistence implements ConfigPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(FileSystemConfigPersistence.class);
  public static final String CONFIG_DIR = "config";
  private static final String TMP_DIR = "tmp_storage";

  private static final Object lock = new Object();

  // root of the file system persistence
  private final Path storageRoot;
  // root for where configs are stored
  private final Path configRoot;

  /**
   * Check if there are existing configs under the storage root. Previously the seed container copies
   * the configs to the storage root, it may take some time for the operation to complete and for the
   * CONFIG_DIR to show up. So we cannot infer anything based on the existence of this directory. Now
   * this seed generation step has been removed. So we can tell immediately whether CONFIG_DIR exists
   * or not. If CONFIG_DIR exists, it means the user has just migrated Airbyte from an old version
   * that uses this file system config persistence.
   */
  public static boolean hasExistingConfigs(final Path storageRoot) {
    return Files.exists(storageRoot.resolve(CONFIG_DIR));
  }

  public static ConfigPersistence createWithValidation(final Path storageRoot) {
    LOGGER.info("Constructing file system config persistence (root: {})", storageRoot);
    final Path configRoot = storageRoot.resolve(CONFIG_DIR);
    Preconditions.checkArgument(Files.exists(configRoot), "CONFIG_DIR does not exist under the storage root: %s", configRoot);
    return new ValidatingConfigPersistence(new FileSystemConfigPersistence(storageRoot));
  }

  public FileSystemConfigPersistence(final Path storageRoot) {
    this.storageRoot = storageRoot;
    this.configRoot = storageRoot.resolve(CONFIG_DIR);
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    synchronized (lock) {
      return getConfigInternal(configType, configId, clazz);
    }
  }

  @Override
  public <T> List<T> listConfigs(final AirbyteConfig configType, final Class<T> clazz) throws JsonValidationException, IOException {
    synchronized (lock) {
      return listConfigsInternal(configType, clazz);
    }
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig configType, final Class<T> clazz)
      throws JsonValidationException, IOException {
    throw new UnsupportedOperationException("File Persistence doesn't support metadata");
  }

  @Override
  public <T> void writeConfig(final AirbyteConfig configType, final String configId, final T config) throws IOException {
    synchronized (lock) {
      writeConfigInternal(configType, configId, config);
    }
  }

  @Override
  public <T> void writeConfigs(final AirbyteConfig configType, final Map<String, T> configs) throws IOException {
    synchronized (lock) {
      for (final Map.Entry<String, T> config : configs.entrySet()) {
        writeConfigInternal(configType, config.getKey(), config.getValue());
      }
    }
  }

  private <T> void writeConfigs(final AirbyteConfig configType, final Stream<T> configs, final Path rootOverride) {
    configs.forEach(config -> {
      final String configId = configType.getId(config);
      try {
        writeConfigInternal(configType, configId, config, rootOverride);
      } catch (final IOException e) {
        throw new RuntimeException(e);
      }
    });
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    final Map<String, Stream<JsonNode>> configs = new HashMap<>();

    final List<String> directories = listDirectories();
    for (final String directory : directories) {
      final List<JsonNode> configList = listConfig(directory);
      configs.put(directory, configList.stream());
    }
    return configs;
  }

  private List<String> listDirectories() throws IOException {
    if (!configRoot.toFile().exists()) {
      return new ArrayList<String>();
    }
    try (final Stream<Path> files = Files.list(configRoot)) {
      return files.map(c -> c.getFileName().toString()).collect(Collectors.toList());
    }
  }

  private List<JsonNode> listConfig(final String configType) throws IOException {
    final Path configTypePath = configRoot.resolve(configType);
    if (!Files.exists(configTypePath)) {
      return Collections.emptyList();
    }
    try (final Stream<Path> files = Files.list(configTypePath)) {
      final List<String> ids = files
          .filter(p -> !p.endsWith(".json"))
          .map(p -> p.getFileName().toString().replace(".json", ""))
          .collect(Collectors.toList());

      final List<JsonNode> configs = Lists.newArrayList();
      for (final String id : ids) {
        try {
          final Path configPath = configRoot.resolve(configType).resolve(String.format("%s.json", id));
          if (!Files.exists(configPath)) {
            throw new RuntimeException("Config NotFound");
          }

          final JsonNode config = Jsons.deserialize(Files.readString(configPath), JsonNode.class);
          configs.add(config);
        } catch (final RuntimeException e) {
          throw new IOException(e);
        }
      }

      return configs;
    }
  }

  @Override
  public void deleteConfig(final AirbyteConfig configType, final String configId) throws IOException {
    synchronized (lock) {
      deleteConfigInternal(configType, configId);
    }
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    final String oldConfigsDir = "config_deprecated";
    // create a new folder
    final String importDirectory = TMP_DIR + UUID.randomUUID();
    final Path rootOverride = storageRoot.resolve(importDirectory);
    Files.createDirectories(rootOverride);

    // write everything
    for (final Map.Entry<AirbyteConfig, Stream<?>> config : configs.entrySet()) {
      writeConfigs(config.getKey(), config.getValue(), rootOverride);
    }

    if (dryRun) {
      FileUtils.deleteDirectory(rootOverride.toFile());
      return;
    }
    if (configRoot.toFile().exists()) {
      FileUtils.moveDirectory(configRoot.toFile(), storageRoot.resolve(oldConfigsDir).toFile());
      LOGGER.info("Renamed config to {} successfully", oldConfigsDir);
    }

    FileUtils.moveDirectory(rootOverride.toFile(), configRoot.toFile());
    LOGGER.info("Renamed " + importDirectory + " to config successfully");

    FileUtils.deleteDirectory(storageRoot.resolve(oldConfigsDir).toFile());
    LOGGER.info("Deleted {}", oldConfigsDir);
  }

  @Override
  public void loadData(final ConfigPersistence seedPersistence) throws IOException {
    // this method is not supported in this implementation, but needed in tests; do nothing
  }

  private <T> T getConfigInternal(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, IOException {
    // validate file with schema
    final Path configPath = buildConfigPath(configType, configId, configRoot);
    if (!Files.exists(configPath)) {
      throw new ConfigNotFoundException(configType, configId);
    } else {
      return Jsons.deserialize(Files.readString(configPath), clazz);
    }
  }

  private <T> List<T> listConfigsInternal(final AirbyteConfig configType, final Class<T> clazz) throws JsonValidationException, IOException {
    final Path configTypePath = buildTypePath(configType, configRoot);
    if (!Files.exists(configTypePath)) {
      return Collections.emptyList();
    }

    try (final Stream<Path> files = Files.list(configTypePath)) {
      final List<String> ids = files
          .filter(p -> !p.endsWith(".json"))
          .map(p -> p.getFileName().toString().replace(".json", ""))
          .collect(Collectors.toList());

      final List<T> configs = Lists.newArrayList();
      for (final String id : ids) {
        try {
          configs.add(getConfig(configType, id, clazz));
        } catch (final ConfigNotFoundException e) {
          // should not happen since we just read the ids from disk.
          throw new IOException(e);
        }
      }

      return configs;
    }
  }

  private <T> void writeConfigInternal(final AirbyteConfig configType, final String configId, final T config) throws IOException {
    writeConfigInternal(configType, configId, config, configRoot);
  }

  private <T> void writeConfigInternal(final AirbyteConfig configType, final String configId, final T config, final Path storageRoot)
      throws IOException {
    final Path configPath = buildConfigPath(configType, configId, storageRoot);
    Files.createDirectories(configPath.getParent());

    Files.writeString(configPath, Jsons.serialize(config));
  }

  private void deleteConfigInternal(final AirbyteConfig configType, final String configId) throws IOException {
    deleteConfigInternal(configType, configId, configRoot);
  }

  private void deleteConfigInternal(final AirbyteConfig configType, final String configId, final Path storageRoot) throws IOException {
    final Path configPath = buildConfigPath(configType, configId, storageRoot);
    Files.delete(configPath);
  }

  private static Path buildConfigPath(final AirbyteConfig configType, final String configId, final Path storageRoot) {
    return buildTypePath(configType, storageRoot).resolve(String.format("%s.json", configId));
  }

  private static Path buildTypePath(final AirbyteConfig configType, final Path storageRoot) {
    return storageRoot.resolve(configType.toString());
  }

}
