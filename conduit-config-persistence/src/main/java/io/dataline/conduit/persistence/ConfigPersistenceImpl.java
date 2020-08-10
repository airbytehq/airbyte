package io.dataline.conduit.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.networknt.schema.*;
import io.dataline.conduit.conduit_config.ConfigSchema;
import io.dataline.conduit.conduit_config.StandardScheduleConfiguration;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Optional;
import java.util.Set;
import java.util.stream.Collectors;

public class ConfigPersistenceImpl implements ConfigPersistence {
  private static final String CONFIG_STORAGE_ROOT = "data/config/";
  private static final String CONFIG_SCHEMA_ROOT = "conduit-config/src/main/resources/json/";

  private final ObjectMapper objectMapper;
  private final SchemaValidatorsConfig schemaValidatorsConfig;
  private final JsonSchemaFactory jsonSchemaFactory;

  public ConfigPersistenceImpl() {
    objectMapper = new ObjectMapper();
    schemaValidatorsConfig = new SchemaValidatorsConfig();
    jsonSchemaFactory = JsonSchemaFactory.getInstance(SpecVersion.VersionFlag.V7);
  }

  @Override
  public <T> T getConfig(
      PersistenceConfigType persistenceConfigType, String configId, Class<T> clazz) {
    // find file
    File configFile = getFileOrThrow(persistenceConfigType, configId);

    // validate file with schema
    validateJson(configFile, persistenceConfigType, configId);

    // cast file to type
    return fileToPojo(configFile, clazz);
  }

  @Override
  public <T> Set<T> getConfigs(PersistenceConfigType persistenceConfigType, Class<T> clazz) {
    return getConfigIds(persistenceConfigType).stream()
        .map(configId -> getConfig(persistenceConfigType, configId, clazz))
        .collect(Collectors.toSet());
  }

  @Override
  public <T> void writeConfig(
      PersistenceConfigType persistenceConfigType, String configId, T config, Class<T> clazz) {
    try {
      objectMapper.writeValue(new File(getConfigPath(persistenceConfigType, configId)), config);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }

  private JsonSchema getSchema(PersistenceConfigType persistenceConfigType) {
    String configSchemaFilename =
        standardConfigTypeToConfigSchema(persistenceConfigType).getSchemaFilename();
    File schemaFile = new File(String.format("%s/%s", CONFIG_SCHEMA_ROOT, configSchemaFilename));
    JsonNode schema;
    try {
      schema = objectMapper.readTree(schemaFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
    return jsonSchemaFactory.getSchema(schema, schemaValidatorsConfig);
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
      case SOURCE_CONNECTION_CONFIGURATION:
        return ConfigSchema.SOURCE_CONNECTION_CONFIGURATION;
      case STANDARD_CONNECTION_STATUS:
        return ConfigSchema.STANDARD_CONNECTION_STATUS;
      case STANDARD_DISCOVERY_OUTPUT:
        return ConfigSchema.STANDARD_DISCOVERY_OUTPUT;
      case DESTINATION_CONNECTION_CONFIGURATION:
        return ConfigSchema.DESTINATION_CONNECTION_CONFIGURATION;
      case STANDARD_SYNC_CONFIGURATION:
        return ConfigSchema.STANDARD_SYNC_CONFIGURATION;
      case STANDARD_SYNC_SUMMARY:
        return ConfigSchema.STANDARD_SYNC_SUMMARY;
      case STANDARD_SYNC_STATE:
        return ConfigSchema.STANDARD_SYNC_STATE;
      case STATE:
        return ConfigSchema.STATE;
      case STANDARD_SYNC_SCHEDULE:
        return ConfigSchema.STANDARD_SYNC_SCHEDULE;
      default:
        throw new RuntimeException(
            String.format(
                "No mapping from StandardConfigType to ConfigSchema for %s",
                persistenceConfigType));
    }
  }

  private void validateJson(
      File configFile, PersistenceConfigType persistenceConfigType, String configId) {
    JsonNode configJson;
    try {
      configJson = objectMapper.readTree(configFile);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }

    JsonSchema schema = getSchema(persistenceConfigType);
    Set<ValidationMessage> validationMessages = schema.validate(configJson);
    if (validationMessages.size() > 0) {
      throw new IllegalStateException(
          String.format(
              "json schema validation failed. type: %s id: %s \n errors: %s \n schema: \n%s \n object: \n%s",
              persistenceConfigType,
              configId,
              validationMessages.stream()
                  .map(ValidationMessage::toString)
                  .collect(Collectors.joining(",")),
              schema.getSchemaNode().toPrettyString(),
              configJson.toPrettyString()));
    }
  }

  private File getFileOrThrow(PersistenceConfigType persistenceConfigType, String configId) {
    return getFile(persistenceConfigType, configId)
        .map(Path::toFile)
        .orElseThrow(
            () ->
                new RuntimeException(
                    String.format("config %s %s not found", persistenceConfigType, configId)));
  }

  private <T> T fileToPojo(File file, Class<T> clazz) {
    try {
      return objectMapper.readValue(file, clazz);
    } catch (IOException e) {
      throw new RuntimeException(e);
    }
  }
}
