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

import static io.airbyte.config.persistence.AirbyteConfigsTable.AIRBYTE_CONFIGS_TABLE_SCHEMA;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Configs;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import java.io.IOException;
import java.nio.file.Path;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * By default, this factory returns a database config persistence. it can still
 * return a file system config persistence for testing purpose. This legacy feature
 * should be removed after the file to database migration is completely done.
 */
public class ConfigPersistenceFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigPersistenceFactory.class);

  private final Configs configs;
  private final boolean setupDatabase;
  private final boolean useConfigDatabase;

  /**
   * @param setupDatabase initialize the database and load data; this is necessary because this method
   *        has multiple callers, and we want to setup the database only once to prevent race
   *        conditions.
   */
  private ConfigPersistenceFactory(Configs configs, boolean setupDatabase, boolean useConfigDatabase) {
    this.configs = configs;
    this.setupDatabase = setupDatabase;
    this.useConfigDatabase = useConfigDatabase;
  }

  public static Builder build(Configs configs) {
    return new Builder(configs);
  }

  public static class Builder {
    private final Configs configs;
    private boolean setupDatabase = true;
    private boolean useConfigDatabase = true;

    private Builder(Configs configs) {
      this.configs = configs;
    }

    public Builder setupDatabase(boolean setupDatabase) {
      this.setupDatabase = setupDatabase;
      return this;
    }

    public Builder useConfigDatabase(boolean useConfigDatabase) {
      this.useConfigDatabase = useConfigDatabase;
      return this;
    }

    public ConfigPersistenceFactory get() {
      return new ConfigPersistenceFactory(configs, setupDatabase, useConfigDatabase);
    }
  }

  /**
   * Create a config persistence based on the configs.
   * <p/>
   * If config root is defined, create a database config persistence and copy the configs from the
   * file-based config persistence. Otherwise, seed the database from the yaml files.
   *
   */
  public ConfigPersistence create() throws IOException {
    if (!useConfigDatabase) {
      Path configRoot = configs.getConfigRoot();
      LOGGER.info("Use file system config persistence (root: {})", configRoot);
      return FileSystemConfigPersistence.createWithValidation(configRoot);
    }

    if (configs.getConfigRoot() == null) {
      // This branch will only be true in a future Airbyte version, in which
      // the config root is no longer required and everything lives in the database.
      return createDbPersistenceWithYamlSeed();
    }
    return createDbPersistenceWithFileSeed();
  }

  ConfigPersistence createDbPersistenceWithYamlSeed() throws IOException {
    ConfigPersistence seedConfigPersistence = new YamlSeedConfigPersistence();
    return createDbPersistence(seedConfigPersistence);
  }

  ConfigPersistence createDbPersistenceWithFileSeed() throws IOException {
    Path configRoot = configs.getConfigRoot();
    ConfigPersistence fsConfigPersistence = FileSystemConfigPersistence.createWithValidation(configRoot);
    return createDbPersistence(fsConfigPersistence);
  }

  ConfigPersistence createDbPersistence(ConfigPersistence seedConfigPersistence) throws IOException {
    LOGGER.info("Use database config persistence.");

    // When setupDatabase is true, it means the database will be initialized after we
    // connect to the database. So the database itself is considered ready as long as
    // the connection is alive. Otherwise, the database is expected to have full data.
    Function<Database, Boolean> isReady = setupDatabase
        ? Databases.IS_CONFIG_DATABASE_CONNECTED
        : Databases.IS_CONFIG_DATABASE_LOADED_WITH_DATA;

    Database database = Databases.createPostgresDatabaseWithRetry(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl(),
        isReady);

    DatabaseConfigPersistence dbConfigPersistence = new DatabaseConfigPersistence(database);
    if (setupDatabase) {
      dbConfigPersistence.initialize(MoreResources.readResource(AIRBYTE_CONFIGS_TABLE_SCHEMA));
      dbConfigPersistence.loadData(seedConfigPersistence);
    }

    return new ValidatingConfigPersistence(dbConfigPersistence);
  }

}
