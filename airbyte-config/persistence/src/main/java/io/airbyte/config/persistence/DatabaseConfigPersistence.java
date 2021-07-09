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

import static org.jooq.impl.DSL.asterisk;
import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.inline;
import static org.jooq.impl.DSL.select;
import static org.jooq.impl.DSL.table;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.Field;
import org.jooq.JSONB;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.Table;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DatabaseConfigPersistence implements ConfigPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(DatabaseConfigPersistence.class);

  private static final Table<Record> AIRBYTE_CONFIGS = table("airbyte_configs");
  private static final Field<String> CONFIG_ID = field("config_id", String.class);
  private static final Field<String> CONFIG_TYPE = field("config_type", String.class);
  private static final Field<JSONB> CONFIG_BLOB = field("config_blob", JSONB.class);
  private static final Field<Timestamp> CREATED_AT = field("created_at", Timestamp.class);
  private static final Field<Timestamp> UPDATED_AT = field("updated_at", Timestamp.class);

  private final ExceptionWrappingDatabase database;

  public DatabaseConfigPersistence(Database database) {
    this.database = new ExceptionWrappingDatabase(database);
  }

  /**
   * Initialize the {@code airbyte_configs} table with configs from the file system config
   * persistence. Only do so table if the table is empty. Otherwise, we assume that it has been
   * initialized.
   */
  public void initialize(ConfigPersistence seedConfigPersistence) throws IOException {
    database.transaction(ctx -> {
      boolean isInitialized = ctx.fetchExists(AIRBYTE_CONFIGS);
      if (isInitialized) {
        LOGGER.info("Config database is not empty, and initialization is skipped");
        return null;
      }

      LOGGER.info("Initializing config database with configs from the file system...");
      Map<ConfigSchema, Stream<JsonNode>> seedConfigs;
      try {
        seedConfigs = seedConfigPersistence.dumpConfigs()
            .entrySet().stream()
            .collect(Collectors.toMap(e -> ConfigSchema.valueOf(e.getKey()), Entry::getValue));
      } catch (IOException e) {
        throw new SQLException(e);
      }
      Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));
      seedConfigs.forEach((configType, value) -> value.forEach(node -> {
        Object config = Jsons.object(node, configType.getClassName());
        ctx.insertInto(AIRBYTE_CONFIGS)
            .set(CONFIG_ID, configType.getId(config))
            .set(CONFIG_TYPE, inline(configType.name()))
            .set(CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(node)))
            .set(CREATED_AT, timestamp)
            .set(UPDATED_AT, timestamp)
            .execute();
      }));

      LOGGER.info("Config database initialization completed");
      return null;
    });
  }

  @Override
  public <T> T getConfig(ConfigSchema configType, String configId, Class<T> clazz)
      throws ConfigNotFoundException, JsonValidationException, IOException {
    Result<Record> result = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .where(CONFIG_TYPE.eq(inline(configType.name())), CONFIG_ID.eq(configId))
        .fetch());

    if (result.isEmpty()) {
      throw new ConfigNotFoundException(configType, configId);
    } else if (result.size() > 1) {
      throw new IllegalStateException(String.format("Multiple %s configs found for ID %s: %s", configType, configId, result));
    }

    return Jsons.deserialize(result.get(0).get(CONFIG_BLOB).data(), clazz);
  }

  @Override
  public <T> List<T> listConfigs(ConfigSchema configType, Class<T> clazz) throws IOException {
    Result<Record> results = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .where(CONFIG_TYPE.eq(inline(configType.name())))
        .orderBy(CONFIG_TYPE, CONFIG_ID)
        .fetch());
    return results.stream()
        .map(record -> Jsons.deserialize(record.get(CONFIG_BLOB).data(), clazz))
        .collect(Collectors.toList());
  }

  @Override
  public <T> void writeConfig(ConfigSchema configType, String configId, T config) throws IOException {
    database.transaction(ctx -> {
      boolean isExistingConfig = ctx.fetchExists(select()
          .from(AIRBYTE_CONFIGS)
          .where(CONFIG_TYPE.eq(inline(configType.name())), CONFIG_ID.eq(configId)));

      Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));

      if (isExistingConfig) {
        int updateCount = ctx.update(AIRBYTE_CONFIGS)
            .set(CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(config)))
            .set(UPDATED_AT, timestamp)
            .where(CONFIG_TYPE.eq(inline(configType.name())), CONFIG_ID.eq(configId))
            .execute();
        LOGGER.info("{} config {} has been updated (updated record count: {})", configType, configId, updateCount);

        return null;
      }

      int insertionCount = ctx.insertInto(AIRBYTE_CONFIGS)
          .set(CONFIG_ID, configId)
          .set(CONFIG_TYPE, inline(configType.name()))
          .set(CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(config)))
          .set(CREATED_AT, timestamp)
          .set(UPDATED_AT, timestamp)
          .execute();
      if (insertionCount != 1) {
        throw new IllegalStateException("Inserted record count is not 1");
      }
      LOGGER.info("New {} config {} has been inserted", configType, configId);

      return null;
    });
  }

  @Override
  public <T> void replaceAllConfigs(Map<ConfigSchema, Stream<T>> configs, boolean dryRun) throws IOException {
    if (dryRun) {
      return;
    }

    Timestamp timestamp = Timestamp.from(Instant.ofEpochMilli(System.currentTimeMillis()));

    database.transaction(ctx -> {
      ctx.truncate(AIRBYTE_CONFIGS).restartIdentity().execute();
      configs.forEach((configType, value) -> value.forEach(config -> ctx.insertInto(AIRBYTE_CONFIGS)
          .set(CONFIG_ID, configType.getId(config))
          .set(CONFIG_TYPE, inline(configType.name()))
          .set(CONFIG_BLOB, JSONB.valueOf(Jsons.serialize(config)))
          .set(CREATED_AT, timestamp)
          .set(UPDATED_AT, timestamp)
          .execute()));
      return null;
    });
  }

  @Override
  public Map<String, Stream<JsonNode>> dumpConfigs() throws IOException {
    Map<String, Result<Record>> results = database.query(ctx -> ctx.select(asterisk())
        .from(AIRBYTE_CONFIGS)
        .orderBy(CONFIG_TYPE, CONFIG_ID)
        .fetchGroups(CONFIG_TYPE));
    return results.entrySet().stream().collect(Collectors.toMap(
        Entry::getKey,
        e -> e.getValue().stream().map(r -> Jsons.deserialize(r.get(CONFIG_BLOB).data()))));
  }

}
