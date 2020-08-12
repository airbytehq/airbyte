package io.dataline.config.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.config.ConfigSchema;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashSet;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

// we force all interaction with disk storage to be effectively single threaded.
public class ConfigPersistenceImpl implements ConfigPersistence {
  private static final Object lock = new Object();
  private static final String CONFIG_STORAGE_ROOT = "data/config/";
  private static final String CONFIG_SCHEMA_ROOT = "dataline-config/src/main/resources/json/";

  private final ObjectMapper objectMapper;
  final JsonSchemaValidation jsonSchemaValidation;

  public ConfigPersistenceImpl() {
    jsonSchemaValidation = JsonSchemaValidation.getInstance();
    objectMapper = new ObjectMapper();
  }

  @Override
  public <T> T getConfig(
      PersistenceConfigType persistenceConfigType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException {
    synchronized (lock) {
      return getConfigInternal(persistenceConfigType, configId, clazz);
    }
  }

  private <T> T getConfigInternal(
      PersistenceConfigType persistenceConfigType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException {
    // find file
    File configFile = getFileOrThrow(persistenceConfigType, configId);

    // validate file with schema
    validateJson(configFile, persistenceConfigType);

    // cast file to type
    return fileToPojo(configFile, clazz);
  }

  @Override
  public <T> Set<T> getConfigs(PersistenceConfigType persistenceConfigType, Class<T> clazz)
      throws JsonValidationException {
    synchronized (lock) {
      final Set<T> configs = new HashSet<>();
      for (String configId : getConfigIds(persistenceConfigType)) {
        try {
          configs.add(getConfig(persistenceConfigType, configId, clazz));
          // this should not happen, because we just looked up these ids.
        } catch (ConfigNotFoundException e) {
          throw new RuntimeException(e);
        }
      }
      return configs;
    }
  }

  @Override
  public <T> void writeConfig(
      PersistenceConfigType persistenceConfigType, String configId, T config) {
    synchronized (lock) {
      try {
        objectMapper.writeValue(new File(getConfigPath(persistenceConfigType, configId)), config);
      } catch (IOException e) {
        throw new RuntimeException(e);
      }
    }
  }

  private JsonNode getSchema(PersistenceConfigType persistenceConfigType) {
    String configSchemaFilename =
        standardConfigTypeToConfigSchema(persistenceConfigType).getSchemaFilename();
    File schemaFile = new File(String.format("%s/%s", CONFIG_SCHEMA_ROOT, configSchemaFilename));
    try {
      return objectMapper.readTree(schemaFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private Set<Path> getFiles(PersistenceConfigType persistenceConfigType) {
    String configDirPath = getConfigDirectory(persistenceConfigType);
    try {
      return Files.list(new File(configDirPath).toPath()).collect(Collectors.toSet());
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private String getConfigDirectory(PersistenceConfigType persistenceConfigType) {
    return String.format("%s/%s", CONFIG_STORAGE_ROOT, persistenceConfigType.toString());
  }

  private String getConfigPath(PersistenceConfigType persistenceConfigType, String configId) {
    return String.format("%s/%s", getConfigDirectory(persistenceConfigType), getFilename(configId));
  }

  private Set<String> getConfigIds(PersistenceConfigType persistenceConfigType) {
    return getFiles(persistenceConfigType).stream()
        .map(path -> path.getFileName().toString().replace(".json", ""))
        .collect(Collectors.toSet());
  }

  private Optional<Path> getFile(PersistenceConfigType persistenceConfigType, String id) {
    String configPath = getConfigPath(persistenceConfigType, id);
    final Path path = Paths.get(configPath);
    if (Files.exists(path)) {
      return Optional.of(path);
    } else {
      return Optional.empty();
    }
  }

  private String getFilename(String id) {
    return String.format("%s.json", id);
  }

  private ConfigSchema standardConfigTypeToConfigSchema(
      PersistenceConfigType persistenceConfigType) {
    switch (persistenceConfigType) {
      case STANDARD_WORKSPACE:
        return ConfigSchema.STANDARD_WORKSPACE;
      case STANDARD_SOURCE:
        return ConfigSchema.STANDARD_SOURCE;
      case SOURCE_CONNECTION_SPECIFICATION:
        return ConfigSchema.SOURCE_CONNECTION_SPECIFICATION;
      case SOURCE_CONNECTION_IMPLEMENTATION:
        return ConfigSchema.SOURCE_CONNECTION_IMPLEMENTATION;
      case STANDARD_DESTINATION:
        return ConfigSchema.STANDARD_DESTINATION;
      case DESTINATION_CONNECTION_SPECIFICATION:
        return ConfigSchema.DESTINATION_CONNECTION_SPECIFICATION;
      case DESTINATION_CONNECTION_IMPLEMENTATION:
        return ConfigSchema.DESTINATION_CONNECTION_IMPLEMENTATION;
      case STANDARD_CONNECTION_STATUS:
        return ConfigSchema.STANDARD_CONNECTION_STATUS;
      case STANDARD_DISCOVERY_OUTPUT:
        return ConfigSchema.STANDARD_DISCOVERY_OUTPUT;
      case STANDARD_SYNC:
        return ConfigSchema.STANDARD_SYNC;
      case STANDARD_SYNC_SUMMARY:
        return ConfigSchema.STANDARD_SYNC_SUMMARY;
      case STANDARD_SYNC_SCHEDULE:
        return ConfigSchema.STANDARD_SYNC_SCHEDULE;
      case STATE:
        return ConfigSchema.STATE;
      default:
        throw new RuntimeException(
            String.format(
                "No mapping from StandardConfigType to ConfigSchema for %s",
                persistenceConfigType));
    }
  }

  private void validateJson(File configFile, PersistenceConfigType persistenceConfigType)
      throws JsonValidationException {
    JsonNode configJson;
    try {
      configJson = objectMapper.readTree(configFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    JsonNode schema = getSchema(persistenceConfigType);
    jsonSchemaValidation.validateThrow(schema, configJson);
  }

  private File getFileOrThrow(PersistenceConfigType persistenceConfigType, String configId)
      throws ConfigNotFoundException {
    return getFile(persistenceConfigType, configId)
        .map(Path::toFile)
        .orElseThrow(
            () ->
                new ConfigNotFoundException(
                    String.format(
                        "config type: %s id: %s not found", persistenceConfigType, configId)));
  }

  private <T> T fileToPojo(File file, Class<T> clazz) {
    try {
      return objectMapper.readValue(file, clazz);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
}
