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

import static io.airbyte.db.instance.configs.jooq.Tables.AIRBYTE_CONFIGS;
import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.select;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.AirbyteConfig;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.ConfigSchemaMigrationSupport;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.time.OffsetDateTime;
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

  public DatabaseConfigPersistence(Database database) {
    this.database = new ExceptionWrappingDatabase(database);
  }

  /**
   * Load or update the configs from the seed.
   */
  @Override
  public void loadData(ConfigPersistence seedConfigPersistence) throws IOException {
    database.transaction(ctx -> {
      boolean isInitialized = ctx.fetchExists(select().from(AIRBYTE_CONFIGS).where());
      if (isInitialized) {
        updateConfigsFromSeed(ctx, seedConfigPersistence);
      } else {
        copyConfigsFromSeed(ctx, seedConfigPersistence);
      }
      return null;
    });
  }

  public ValidatingConfigPersistence withValidation() {
    return new ValidatingConfigPersistence(this);
  }

  @Override
  public <T> T getConfig(AirbyteConfig configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    Result<Record> result = database.query(ctx -> ctx.select(asterisk())
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
  public <T> List<T> listConfigs(AirbyteConfig configType, Class<T> clazz) throws IOException {
    Result<Record> results = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()))
        .orderBy(AIRBYTE_CONFIGS.CONFIG_TYPE, AIRBYTE_CONFIGS.CONFIG_ID)
        .fetch());
    return results.stream()
        .map(record -> Jsons.deserialize(record.get(AIRBYTE_CONFIGS.CONFIG_BLOB).data(), clazz))
        .collect(Collectors.toList());
  }

  @Override
  public <T> void writeConfig(AirbyteConfig configType, String configId, T config) throws IOException {
    database.transaction(ctx -> {
      boolean isExistingConfig = ctx.fetchExists(select()
          .from(AIRBYTE_CONFIGS)
          .where(AIRBYTE_CONFIGS.CONFIG_TYPE.eq(configType.name()), AIRBYTE_CONFIGS.CONFIG_ID.eq(configId)));

      OffsetDateTime timestamp = OffsetDateTime.now();

      if (isExistingConfig) {
        updateConfigRecord(ctx, timestamp, configType.name(), Jsons.jsonNode(config), configId);
      } else {
        insertConfigRecord(ctx, timestamp, configType.name(), Jsons.jsonNode(config), configType.getIdFieldName());
      }

      return null;
    });
  }

  @Override
  public void deleteConfig(AirbyteConfig configType, String configId) throws IOException {
    database.transaction(ctx -> {
      boolean isExistingConfig = ctx.fetchExists(select()
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
  public void replaceAllConfigs(Map<AirbyteConfig, Stream<?>> configs, boolean dryRun) throws IOException {
    if (dryRun) {
      return;
    }

    LOGGER.info("Replacing all configs");

    OffsetDateTime timestamp = OffsetDateTime.now();
    int insertionCount = database.transaction(ctx -> {
      ctx.truncate(AIRBYTE_CONFIGS).restartIdentity().execute();

      return configs.entrySet().stream().map(entry -> {
        AirbyteConfig configType = entry.getKey();
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

    Map<String, Result<Record>> results = database.query(ctx -> ctx.select(asterisk())
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
  int insertConfigRecord(DSLContext ctx, OffsetDateTime timestamp, String configType, JsonNode configJson, @Nullable String idFieldName) {
    String configId = idFieldName == null
        ? UUID.randomUUID().toString()
        : configJson.get(idFieldName).asText();
    LOGGER.info("Inserting {} record {}", configType, configId);

    int insertionCount = ctx.insertInto(AIRBYTE_CONFIGS)
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
  int updateConfigRecord(DSLContext ctx, OffsetDateTime timestamp, String configType, JsonNode configJson, String configId) {
    LOGGER.info("Updating {} record {}", configType, configId);

    int updateCount = ctx.update(AIRBYTE_CONFIGS)
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
  void copyConfigsFromSeed(DSLContext ctx, ConfigPersistence seedConfigPersistence) throws SQLException {
    LOGGER.info("Loading data to config database...");

    Map<String, Stream<JsonNode>> seedConfigs;
    try {
      seedConfigs = seedConfigPersistence.dumpConfigs();
    } catch (IOException e) {
      throw new SQLException(e);
    }

    OffsetDateTime timestamp = OffsetDateTime.now();
    int insertionCount = seedConfigs.entrySet().stream().map(entry -> {
      String configType = entry.getKey();
      return entry.getValue().map(configJson -> {
        String idFieldName = ConfigSchemaMigrationSupport.CONFIG_SCHEMA_ID_FIELD_NAMES.get(configType);
        return insertConfigRecord(ctx, timestamp, configType, configJson, idFieldName);
      }).reduce(0, Integer::sum);
    }).reduce(0, Integer::sum);

    LOGGER.info("Config database data loading completed with {} records", insertionCount);
  }

  static class ConnectorInfo {

    final String dockerRepository;
    final String connectorDefinitionId;
    final String dockerImageTag;

    private ConnectorInfo(String dockerRepository, String connectorDefinitionId, String dockerImageTag) {
      this.dockerRepository = dockerRepository;
      this.connectorDefinitionId = connectorDefinitionId;
      this.dockerImageTag = dockerImageTag;
    }

    @Override
    public String toString() {
      return String.format("%s: %s (%s)", dockerRepository, dockerImageTag, connectorDefinitionId);
    }

  }

  private static class ConnectorCounter {

    private final int newCount;
    private final int updateCount;

    private ConnectorCounter(int newCount, int updateCount) {
      this.newCount = newCount;
      this.updateCount = updateCount;
    }

  }

  @VisibleForTesting
  void updateConfigsFromSeed(DSLContext ctx, ConfigPersistence seedConfigPersistence) throws SQLException {
    LOGGER.info("Config database has been initialized; updating connector definitions from the seed if necessary...");

    try {
      Set<String> connectorRepositoriesInUse = getConnectorRepositoriesInUse(ctx);
      LOGGER.info("Connectors in use: {}", connectorRepositoriesInUse);

      Map<String, ConnectorInfo> connectorRepositoryToInfoMap = getConnectorRepositoryToInfoMap(ctx);
      LOGGER.info("Current connector versions: {}", connectorRepositoryToInfoMap.values());

      OffsetDateTime timestamp = OffsetDateTime.now();
      int newConnectorCount = 0;
      int updatedConnectorCount = 0;

      List<StandardSourceDefinition> latestSources = seedConfigPersistence.listConfigs(
          ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class);
      ConnectorCounter sourceConnectorCounter = updateConnectorDefinitions(ctx, timestamp, ConfigSchema.STANDARD_SOURCE_DEFINITION,
          latestSources, connectorRepositoriesInUse, connectorRepositoryToInfoMap);
      newConnectorCount += sourceConnectorCounter.newCount;
      updatedConnectorCount += sourceConnectorCounter.updateCount;

      List<StandardDestinationDefinition> latestDestinations = seedConfigPersistence.listConfigs(
          ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class);
      ConnectorCounter destinationConnectorCounter = updateConnectorDefinitions(ctx, timestamp, ConfigSchema.STANDARD_DESTINATION_DEFINITION,
          latestDestinations, connectorRepositoriesInUse, connectorRepositoryToInfoMap);
      newConnectorCount += destinationConnectorCounter.newCount;
      updatedConnectorCount += destinationConnectorCounter.updateCount;

      LOGGER.info("Connector definitions have been updated ({} new connectors, and {} updates)", newConnectorCount, updatedConnectorCount);
    } catch (IOException | JsonValidationException e) {
      throw new SQLException(e);
    }
  }

  /**
   * @param connectorRepositoriesInUse when a connector is used in any standard sync, its definition
   *        will not be updated. This is necessary because the new connector version may not be
   *        backward compatible.
   */
  private <T> ConnectorCounter updateConnectorDefinitions(DSLContext ctx,
                                                          OffsetDateTime timestamp,
                                                          AirbyteConfig configType,
                                                          List<T> latestDefinitions,
                                                          Set<String> connectorRepositoriesInUse,
                                                          Map<String, ConnectorInfo> connectorRepositoryToIdVersionMap)
      throws IOException {
    int newCount = 0;
    int updatedCount = 0;
    for (T latestDefinition : latestDefinitions) {
      JsonNode configJson = Jsons.jsonNode(latestDefinition);
      String repository = configJson.get("dockerRepository").asText();
      if (connectorRepositoriesInUse.contains(repository)) {
        LOGGER.info("Connector {} is in use; skip updating", repository);
        continue;
      }

      if (!connectorRepositoryToIdVersionMap.containsKey(repository)) {
        LOGGER.info("Adding new connector {}: {}", repository, configJson);
        newCount += insertConfigRecord(ctx, timestamp, configType.name(), configJson, configType.getIdFieldName());
        continue;
      }

      ConnectorInfo connectorInfo = connectorRepositoryToIdVersionMap.get(repository);
      String latestImageTag = configJson.get("dockerImageTag").asText();
      if (!latestImageTag.equals(connectorInfo.dockerImageTag)) {
        LOGGER.info("Connector {} needs update: {} vs {}", repository, connectorInfo.dockerImageTag, latestImageTag);
        updatedCount += updateConfigRecord(ctx, timestamp, configType.name(), configJson, connectorInfo.connectorDefinitionId);
      } else {
        LOGGER.info("Connector {} does not need update: {}", repository, connectorInfo.dockerImageTag);
      }
    }
    return new ConnectorCounter(newCount, updatedCount);
  }

  /**
   * @return A map about current connectors (both source and destination). It maps from connector
   *         repository to its definition id and docker image tag. We identify a connector by its
   *         repository name instead of definition id because connectors can be added manually by
   *         users, and are not always the same as those in the seed.
   */
  @VisibleForTesting
  Map<String, ConnectorInfo> getConnectorRepositoryToInfoMap(DSLContext ctx) {
    Field<String> repoField = field("config_blob ->> 'dockerRepository'", SQLDataType.VARCHAR).as("repository");
    Field<String> versionField = field("config_blob ->> 'dockerImageTag'", SQLDataType.VARCHAR).as("version");
    return ctx.select(AIRBYTE_CONFIGS.CONFIG_ID, repoField, versionField)
        .from(AIRBYTE_CONFIGS)
        .where(AIRBYTE_CONFIGS.CONFIG_TYPE.in(ConfigSchema.STANDARD_SOURCE_DEFINITION.name(), ConfigSchema.STANDARD_DESTINATION_DEFINITION.name()))
        .fetch().stream()
        .collect(Collectors.toMap(
            row -> row.getValue(repoField),
            row -> new ConnectorInfo(row.getValue(repoField), row.getValue(AIRBYTE_CONFIGS.CONFIG_ID), row.getValue(versionField)),
            // when there are duplicated connector definitions, return the latest one
            (c1, c2) -> {
              AirbyteVersion v1 = new AirbyteVersion(c1.dockerImageTag);
              AirbyteVersion v2 = new AirbyteVersion(c2.dockerImageTag);
              LOGGER.warn("Duplicated connector version found for {}: {} ({}) vs {} ({})",
                  c1.dockerRepository, c1.dockerImageTag, c1.connectorDefinitionId, c2.dockerImageTag, c2.connectorDefinitionId);
              int comparison = v1.patchVersionCompareTo(v2);
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
  private Set<String> getConnectorRepositoriesInUse(DSLContext ctx) {
    Set<String> usedConnectorDefinitionIds = new HashSet<>();
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
