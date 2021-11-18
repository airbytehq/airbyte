/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static io.airbyte.db.instance.configs.jooq.Tables.AIRBYTE_CONFIGS;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.select;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.MoreIterators;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigSchemaMigrationSupport;
import io.airbyte.config.ConfigWithMetadata;
import io.airbyte.config.Configs;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import javax.annotation.Nullable;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Record1;
import org.jooq.Result;
import org.jooq.impl.SQLDataType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseConfigPersistence implements ConfigPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseConfigPersistence.class);

  private final ExceptionWrappingDatabase database;

  public DatabaseConfigPersistence(final Database database) {
    this.database = new ExceptionWrappingDatabase(database);
  }

  /**
   * If this is a migration deployment from an old version that relies on file system config
   * persistence, copy the existing configs from local files.
   */
  public DatabaseConfigPersistence migrateFileConfigs(final Configs serverConfigs) throws IOException {
    database.transaction(ctx -> {
      final boolean isInitialized = ctx.fetchExists(AIRBYTE_CONFIGS);
      if (isInitialized) {
        return null;
      }

      final boolean hasExistingFileConfigs = FileSystemConfigPersistence.hasExistingConfigs(serverConfigs.getConfigRoot());
      if (hasExistingFileConfigs) {
        LOGGER.info("Load existing local config directory into configs database");
        final ConfigPersistence fileSystemPersistence = new FileSystemConfigPersistence(serverConfigs.getConfigRoot());
        copyConfigsFromSeed(ctx, fileSystemPersistence);
      }

      return null;
    });

    return this;
  }

  @Override
  public void loadData(final ConfigPersistence seedConfigPersistence) throws IOException {
    database.transaction(ctx -> {
      updateConfigsFromSeed(ctx, seedConfigPersistence);
      return null;
    });
  }

  public Set<String> getInUseConnectorDockerImageNames() throws IOException {
    return database.transaction(this::getConnectorRepositoriesInUse);
  }

  public ValidatingConfigPersistence withValidation() {
    return new ValidatingConfigPersistence(this);
  }

  @Override
  public <T> T getConfig(final AirbyteConfig configType, final String configId, final Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    final Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()), AIRBYTE_CONFIGS.CONFIG_ID.eq(configId))
        .fetch());

    if (result.isEmpty()) {
      throw new ConfigNotFoundException(configType, configId);
    } else if (result.size() > 1) {
      throw new IllegalStateException(String.format("Multiple %s configs found for ID %s: %s", configType, configId, result));
    }

    return Jsons.deserialize(result.get(0).get(AIRBYTE_CONFIGS.CONFIG_BLOB).data(), clazz);
  }

  @Override
  public <T> List<T> listConfigs(final AirbyteConfig configType, final Class<T> clazz) throws IOException {
    final Result<Record> results = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()))
        .orderBy(AIRBYTE_CONFIGS.CONFIG_TYPE, AIRBYTE_CONFIGS.CONFIG_ID)
        .fetch());
    return results.stream()
        .map(record -> Jsons.deserialize(record.get(AIRBYTE_CONFIGS.CONFIG_BLOB).data(), clazz))
        .collect(Collectors.toList());
  }

  @Override
  public <T> List<ConfigWithMetadata<T>> listConfigsWithMetadata(final AirbyteConfig configType, final Class<T> clazz) throws IOException {
    final Result<Record> results = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()))
        .orderBy(AIRBYTE_CONFIGS.CONFIG_TYPE, AIRBYTE_CONFIGS.CONFIG_ID)
        .fetch());
    return results.stream()
        .map(record -> new ConfigWithMetadata<>(
            record.get(AIRBYTE_CONFIGS.CONFIG_ID),
            record.get(AIRBYTE_CONFIGS.CONFIG_TYPE),
            record.get(AIRBYTE_CONFIGS.CREATED_AT).toInstant(),
            record.get(AIRBYTE_CONFIGS.UPDATED_AT).toInstant(),
            Jsons.deserialize(record.get(AIRBYTE_CONFIGS.CONFIG_BLOB).data(), clazz)))
        .collect(Collectors.toList());
  }

  @Override
  public <T> void writeConfig(final AirbyteConfig configType, final String configId, final T config) throws IOException {
    final Map<String, T> configIdToConfig = new HashMap<>() {

      {
        put(configId, config);
      }

    };
    writeConfigs(configType, configIdToConfig);
  }

  @Override
  public <T> void writeConfigs(final AirbyteConfig configType, final Map<String, T> configs) throws IOException {
    database.transaction(ctx -> {
      final OffsetDateTime timestamp = OffsetDateTime.now();
      configs.forEach((configId, config) -> {
        final boolean isExistingConfig = ctx.fetchExists(select()
            .from(AIRBYTE_CONFIGS)
            .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()), AIRBYTE_CONFIGS.CONFIG_ID.eq(configId)));

        if (isExistingConfig) {
          updateConfigRecord(ctx, timestamp, configType.name(), Jsons.jsonNode(config), configId);
        } else {
          insertConfigRecord(ctx, timestamp, configType.name(), Jsons.jsonNode(config),
              configType.getIdFieldName());
        }
      });

      return null;
    });
  }

  @Override
  public void deleteConfig(final AirbyteConfig configType, final String configId) throws IOException {
    database.transaction(ctx -> {
      final boolean isExistingConfig = ctx.fetchExists(select()
          .from(AIRBYTE_CONFIGS)
          .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()), AIRBYTE_CONFIGS.CONFIG_ID.eq(configId)));

      if (isExistingConfig) {
        ctx.deleteFrom(AIRBYTE_CONFIGS)
            .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()), AIRBYTE_CONFIGS.CONFIG_ID.eq(configId))
            .execute();
        return null;
      }
      return null;
    });
  }

  @Override
  public void replaceAllConfigs(final Map<AirbyteConfig, Stream<?>> configs, final boolean dryRun) throws IOException {
    if (dryRun) {
      return;
    }

    LOGGER.info("Replacing all configs");

    final OffsetDateTime timestamp = OffsetDateTime.now();
    final int insertionCount = database.transaction(ctx -> {
      ctx.truncate(AIRBYTE_CONFIGS).restartIdentity().execute();

      return configs.entrySet().stream().map(entry -> {
        final AirbyteConfig configType = entry.getKey();
        return entry.getValue()
            .map(configObject -> insertConfigRecord(ctx, timestamp, configType.name(), Jsons.jsonNode(configObject), configType.getIdFieldName()))
            .reduce(0, Integer::sum);
      }).reduce(0, Integer::sum);
    });

    LOGGER.info("Config database is reset with {} records", insertionCount);
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    LOGGER.info("Exporting all configs...");

    final Map<String, Result<Record>> results = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .orderBy(AIRBYTE_CONFIGS.CONFIG_TYPE, AIRBYTE_CONFIGS.CONFIG_ID)
        .fetchGroups(AIRBYTE_CONFIGS.CONFIG_TYPE));
    return results.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        e -> e.getValue().stream().map(r -> Jsons.deserialize(r.get(AIRBYTE_CONFIGS.CONFIG_BLOB).data()))));
  }

  /**
   * @return the number of inserted records for convenience, which is always 1.
   */
  @VisibleForTesting
  int insertConfigRecord(
                         final DSLContext ctx,
                         final OffsetDateTime timestamp,
                         final String configType,
                         final JsonNode configJson,
                         @Nullable final String idFieldName) {
    final String configId = idFieldName == null
        ? UUID.randomUUID().toString()
        : configJson.get(idFieldName).asText();
    LOGGER.info("Inserting {} record {}", configType, configId);

    final int insertionCount = ctx.insertInto(AIRBYTE_CONFIGS)
        .set(AIRBYTE_CONFIGS.CONFIG_ID, configId)
        .set(AIRBYTE_CONFIGS.CONFIG_TYPE, configType)
        .set(AIRBYTE_CONFIGS.CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(configJson)))
        .set(AIRBYTE_CONFIGS.CREATED_AT, timestamp)
        .set(AIRBYTE_CONFIGS.UPDATED_AT, timestamp)
        .onConflict(AIRBYTE_CONFIGS.CONFIG_TYPE, AIRBYTE_CONFIGS.CONFIG_ID)
        .doNothing()
        .execute();
    if (insertionCount != 1) {
      LOGGER.warn("{} config {} already exists (insertion record count: {})", configType, configId, insertionCount);
    }
    return insertionCount;
  }

  /**
   * @return the number of updated records.
   */
  @VisibleForTesting
  int updateConfigRecord(final DSLContext ctx,
                         final OffsetDateTime timestamp,
                         final String configType,
                         final JsonNode configJson,
                         final String configId) {
    LOGGER.info("Updating {} record {}", configType, configId);

    final int updateCount = ctx.update(AIRBYTE_CONFIGS)
        .set(AIRBYTE_CONFIGS.CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(configJson)))
        .set(AIRBYTE_CONFIGS.UPDATED_AT, timestamp)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType), AIRBYTE_CONFIGS.CONFIG_ID.eq(configId))
        .execute();
    if (updateCount != 1) {
      LOGGER.warn("{} config {} is not updated (updated record count: {})", configType, configId, updateCount);
    }
    return updateCount;
  }

  @VisibleForTesting
  void copyConfigsFromSeed(final DSLContext ctx, final ConfigPersistence seedConfigPersistence) throws SQLException {
    LOGGER.info("Loading seed data to config database...");

    final Map<String, Stream<JsonNode>> seedConfigs;
    try {
      seedConfigs = seedConfigPersistence.dumpConfigs();
    } catch (final IOException e) {
      throw new SQLException(e);
    }

    final OffsetDateTime timestamp = OffsetDateTime.now();
    final int insertionCount = seedConfigs.entrySet().stream().map(entry -> {
      final String configType = entry.getKey();
      return entry.getValue().map(configJson -> {
        final String idFieldName = ConfigSchemaMigrationSupport.CONFIG_SCHEMA_ID_FIELD_NAMES.get(configType);
        return insertConfigRecord(ctx, timestamp, configType, configJson, idFieldName);
      }).reduce(0, Integer::sum);
    }).reduce(0, Integer::sum);

    LOGGER.info("Config database data loading completed with {} records", insertionCount);
  }

  static class ConnectorInfo {

    final String definitionId;
    final JsonNode definition;
    final String dockerRepository;
    final String dockerImageTag;

    ConnectorInfo(final String definitionId, final JsonNode definition) {
      this.definitionId = definitionId;
      this.definition = definition;
      this.dockerRepository = definition.get("dockerRepository").asText();
      this.dockerImageTag = definition.get("dockerImageTag").asText();
    }

    @Override
    public String toString() {
      return String.format("%s: %s (%s)", dockerRepository, dockerImageTag, definitionId);
    }

  }

  private static class ConnectorCounter {

    private final int newCount;
    private final int updateCount;

    private ConnectorCounter(final int newCount, final int updateCount) {
      this.newCount = newCount;
      this.updateCount = updateCount;
    }

  }

  @VisibleForTesting
  void updateConfigsFromSeed(final DSLContext ctx, final ConfigPersistence seedConfigPersistence) throws SQLException {
    LOGGER.info("Updating connector definitions from the seed if necessary...");

    try {
      final Set<String> connectorRepositoriesInUse = getConnectorRepositoriesInUse(ctx);
      LOGGER.info("Connectors in use: {}", connectorRepositoriesInUse);

      final Map<String, ConnectorInfo> connectorRepositoryToInfoMap = getConnectorRepositoryToInfoMap(ctx);
      LOGGER.info("Current connector versions: {}", connectorRepositoryToInfoMap.values());

      final OffsetDateTime timestamp = OffsetDateTime.now();
      int newConnectorCount = 0;
      int updatedConnectorCount = 0;

      final List<StandardSourceDefinition> latestSources = seedConfigPersistence.listConfigs(
          ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
      final ConnectorCounter sourceConnectorCounter = updateConnectorDefinitions(ctx, timestamp, ConfigSchema.STANDARD_SOURCE_DEFINITION,
          latestSources, connectorRepositoriesInUse, connectorRepositoryToInfoMap);
      newConnectorCount += sourceConnectorCounter.newCount;
      updatedConnectorCount += sourceConnectorCounter.updateCount;

      final List<StandardDestinationDefinition> latestDestinations = seedConfigPersistence.listConfigs(
          ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
      final ConnectorCounter destinationConnectorCounter = updateConnectorDefinitions(ctx, timestamp, ConfigSchema.STANDARD_DESTINATION_DEFINITION,
          latestDestinations, connectorRepositoriesInUse, connectorRepositoryToInfoMap);
      newConnectorCount += destinationConnectorCounter.newCount;
      updatedConnectorCount += destinationConnectorCounter.updateCount;

      LOGGER.info("Connector definitions have been updated ({} new connectors, and {} updates)", newConnectorCount, updatedConnectorCount);
    } catch (final IOException | JsonValidationException e) {
      throw new SQLException(e);
    }
  }

  /**
   * @param connectorRepositoriesInUse when a connector is used in any standard sync, its definition
   *        will not be updated. This is necessary because the new connector version may not be
   *        backward compatible.
   */
  @VisibleForTesting
  <T> ConnectorCounter updateConnectorDefinitions(final DSLContext ctx,
                                                  final OffsetDateTime timestamp,
                                                  final AirbyteConfig configType,
                                                  final List<T> latestDefinitions,
                                                  final Set<String> connectorRepositoriesInUse,
                                                  final Map<String, ConnectorInfo> connectorRepositoryToIdVersionMap)
      throws IOException {
    int newCount = 0;
    int updatedCount = 0;

    for (final T definition : latestDefinitions) {
      final JsonNode latestDefinition = Jsons.jsonNode(definition);
      final String repository = latestDefinition.get("dockerRepository").asText();

      // Add new connector
      if (!connectorRepositoryToIdVersionMap.containsKey(repository)) {
        LOGGER.info("Adding new connector {}: {}", repository, latestDefinition);
        newCount += insertConfigRecord(ctx, timestamp, configType.name(), latestDefinition, configType.getIdFieldName());
        continue;
      }

      final ConnectorInfo connectorInfo = connectorRepositoryToIdVersionMap.get(repository);
      final JsonNode currentDefinition = connectorInfo.definition;

      // todo (lmossman) - this logic to remove the "spec" field is temporary; it is necessary to avoid
      // breaking users who are actively using an old connector version, otherwise specs from the most
      // recent connector versions may be inserted into the db which could be incompatible with the
      // version they are actually using.
      // Once the faux major version bump has been merged, this "new field" logic will be removed
      // entirely.
      final Set<String> newFields = Sets.difference(getNewFields(currentDefinition, latestDefinition), Set.of("spec"));

      // Process connector in use
      if (connectorRepositoriesInUse.contains(repository)) {
        if (newFields.size() == 0) {
          LOGGER.info("Connector {} is in use and has all fields; skip updating", repository);
        } else {
          // Add new fields to the connector definition
          final JsonNode definitionToUpdate = getDefinitionWithNewFields(currentDefinition, latestDefinition, newFields);
          LOGGER.info("Connector {} has new fields: {}", repository, String.join(", ", newFields));
          updatedCount += updateConfigRecord(ctx, timestamp, configType.name(), definitionToUpdate, connectorInfo.definitionId);
        }
        continue;
      }

      // Process unused connector
      final String latestImageTag = latestDefinition.get("dockerImageTag").asText();
      if (hasNewVersion(connectorInfo.dockerImageTag, latestImageTag)) {
        // Update connector to the latest version
        LOGGER.info("Connector {} needs update: {} vs {}", repository, connectorInfo.dockerImageTag, latestImageTag);
        updatedCount += updateConfigRecord(ctx, timestamp, configType.name(), latestDefinition, connectorInfo.definitionId);
      } else if (newFields.size() > 0) {
        // Add new fields to the connector definition
        final JsonNode definitionToUpdate = getDefinitionWithNewFields(currentDefinition, latestDefinition, newFields);
        LOGGER.info("Connector {} has new fields: {}", repository, String.join(", ", newFields));
        updatedCount += updateConfigRecord(ctx, timestamp, configType.name(), definitionToUpdate, connectorInfo.definitionId);
      } else {
        LOGGER.info("Connector {} does not need update: {}", repository, connectorInfo.dockerImageTag);
      }
    }

    return new ConnectorCounter(newCount, updatedCount);
  }

  static boolean hasNewVersion(final String currentVersion, final String latestVersion) {
    try {
      return new AirbyteVersion(latestVersion).patchVersionCompareTo(new AirbyteVersion(currentVersion)) > 0;
    } catch (final Exception e) {
      LOGGER.error("Failed to check version: {} vs {}", currentVersion, latestVersion);
      return false;
    }
  }

  /**
   * @return new fields from the latest definition
   */
  static Set<String> getNewFields(final JsonNode currentDefinition, final JsonNode latestDefinition) {
    final Set<String> currentFields = MoreIterators.toSet(currentDefinition.fieldNames());
    final Set<String> latestFields = MoreIterators.toSet(latestDefinition.fieldNames());
    return Sets.difference(latestFields, currentFields);
  }

  /**
   * @return a clone of the current definition with the new fields from the latest definition.
   */
  static JsonNode getDefinitionWithNewFields(final JsonNode currentDefinition, final JsonNode latestDefinition, final Set<String> newFields) {
    final ObjectNode currentClone = (ObjectNode) Jsons.clone(currentDefinition);
    newFields.forEach(field -> currentClone.set(field, latestDefinition.get(field)));
    return currentClone;
  }

  /**
   * @return A map about current connectors (both source and destination). It maps from connector
   *         repository to its definition id and docker image tag. We identify a connector by its
   *         repository name instead of definition id because connectors can be added manually by
   *         users, and are not always the same as those in the seed.
   */
  @VisibleForTesting
  Map<String, ConnectorInfo> getConnectorRepositoryToInfoMap(final DSLContext ctx) {
    final Field<JSONB> configField = field("config_blob", SQLDataType.JSONB).as("definition");
    final Field<String> repoField = field("config_blob ->> 'dockerRepository'", SQLDataType.VARCHAR).as("repository");
    return ctx.select(AIRBYTE_CONFIGS.CONFIG_ID, repoField, configField)
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.in(ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()))
        .fetch().stream()
        .collect(Collectors.toMap(
            row -> row.getValue(repoField),
            row -> new ConnectorInfo(row.getValue(AIRBYTE_CONFIGS.CONFIG_ID), Jsons.deserialize(row.getValue(configField).data())),
            // when there are duplicated connector definitions, return the latest one
            (c1, c2) -> {
              final AirbyteVersion v1 = new AirbyteVersion(c1.dockerImageTag);
              final AirbyteVersion v2 = new AirbyteVersion(c2.dockerImageTag);
              LOGGER.warn("Duplicated connector version found for {}: {} ({}) vs {} ({})",
                  c1.dockerRepository, c1.dockerImageTag, c1.definitionId, c2.dockerImageTag, c2.definitionId);
              final int comparison = v1.patchVersionCompareTo(v2);
              if (comparison >= 0) {
                return c1;
              } else {
                return c2;
              }
            }));
  }

  /**
   * @return A set of connectors (both source and destination) that are already used in standard
   *         syncs. We identify connectors by its repository name instead of definition id because
   *         connectors can be added manually by users, and their config ids are not always the same
   *         as those in the seed.
   */
  private Set<String> getConnectorRepositoriesInUse(final DSLContext ctx) {
    final Set<String> usedConnectorDefinitionIds = new HashSet<>();
    // query for used source definitions
    usedConnectorDefinitionIds.addAll(ctx
        .select(field("config_blob ->> 'sourceDefinitionId'", SQLDataType.VARCHAR))
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(ConfigSchema.SOURCE_CONNECTION.name()))
        .fetch().stream()
        .flatMap(row -> Stream.of(row.value1()))
        .collect(Collectors.toSet()));
    // query for used destination definitions
    usedConnectorDefinitionIds.addAll(ctx
        .select(field("config_blob ->> 'destinationDefinitionId'", SQLDataType.VARCHAR))
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(ConfigSchema.DESTINATION_CONNECTION.name()))
        .fetch().stream()
        .flatMap(row -> Stream.of(row.value1()))
        .collect(Collectors.toSet()));

    return ctx.select(field("config_blob ->> 'dockerRepository'", SQLDataType.VARCHAR))
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_ID.in(usedConnectorDefinitionIds))
        .fetch().stream()
        .map(Record1::value1)
        .collect(Collectors.toSet());
  }

}
