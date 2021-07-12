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

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.Configs;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import java.io.IOException;
import java.nio.file.Path;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigPersistenceFactory {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigPersistenceFactory.class);
  private static final String SCHEMA_TEMPLATE_FILE = "config_database_schema.sql";

  /**
   * When USE_CONFIG_DATABASE is truthy, create the database config persistence, and initialize it
   * with data from the file system config persistence. Otherwise, just return the file system config
   * persistence.
   *
   * @param setupDatabase - initialize the database and load data
   */
  public static ConfigPersistence create(Configs configs, boolean setupDatabase) throws IOException {
    Path configRoot = configs.getConfigRoot();
    ConfigPersistence fsConfigPersistence = FileSystemConfigPersistence.createWithValidation(configRoot);

    if (!configs.useConfigDatabase()) {
      LOGGER.info("Use file system config persistence (config root: {})", configRoot);
      return fsConfigPersistence;
    }

    LOGGER.info("Use database config persistence");

    // When initialization is needed, the database is ready when the connection is alive.
    // Otherwise, the database is ready when data has been loaded into it.
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
      dbConfigPersistence.initialize(MoreResources.readResource(SCHEMA_TEMPLATE_FILE));
      dbConfigPersistence.loadData(fsConfigPersistence);
    }

    return new ValidatingConfigPersistence(dbConfigPersistence);
  }

}
