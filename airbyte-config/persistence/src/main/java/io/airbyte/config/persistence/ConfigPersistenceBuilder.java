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

import io.airbyte.config.Configs;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * By default, this factory returns a database config persistence. it can still return a file system
 * config persistence for testing purpose. This legacy feature should be removed after the file to
 * database migration is completely done.
 */
public class ConfigPersistenceBuilder {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigPersistenceBuilder.class);

  private final Configs configs;
  private final boolean setupDatabase;

  ConfigPersistenceBuilder(Configs configs, boolean setupDatabase) {
    this.configs = configs;
    this.setupDatabase = setupDatabase;
  }

  /**
   * Create a db config persistence and setup the database, including table creation and data loading.
   */
  public static ConfigPersistence getAndInitializeDbPersistence(Configs configs) throws IOException, InterruptedException {
    return new ConfigPersistenceBuilder(configs, true).create();
  }

  /**
   * Create a db config persistence without setting up the database.
   */
  public static ConfigPersistence getDbPersistence(Configs configs) throws IOException, InterruptedException {
    return new ConfigPersistenceBuilder(configs, false).create();
  }

  /**
   * Create a database config persistence based on the configs. If config root is defined, create a
   * database config persistence and copy the configs from the file-based config persistence.
   * Otherwise, seed the database from the yaml files.
   */
  ConfigPersistence create() throws IOException, InterruptedException {
    if (FileSystemConfigPersistence.hasExistingConfigs(configs.getConfigRoot())) {
      LOGGER.info("There is existing local config directory");
      return getDbPersistenceWithFileSeed();
    } else {
      LOGGER.info("There is no existing local config directory");
      return getDbPersistenceWithYamlSeed();
    }
  }

  /**
   * Create the database config persistence and load it with the initial seed from the YAML seed files
   * if the database should be initialized.
   */
  ConfigPersistence getDbPersistenceWithYamlSeed() throws IOException {
    LOGGER.info("Creating db-based config persistence, and loading initial seed from YAML files");
    ConfigPersistence seedConfigPersistence = YamlSeedConfigPersistence.get();
    return getDbPersistence(seedConfigPersistence);
  }

  /**
   * Create the database config persistence and load it with the existing configs from the file system
   * config persistence if the database should be initialized.
   */
  ConfigPersistence getDbPersistenceWithFileSeed() throws IOException, InterruptedException {
    LOGGER.info("Creating db-based config persistence, and loading seed and existing data from files");
    ConfigPersistence fsConfigPersistence = FileSystemConfigPersistence.createWithValidation(configs.getConfigRoot());
    return getDbPersistence(fsConfigPersistence);
  }

  /**
   * Create the database config persistence and load it with configs from the
   * {@code seedConfigPersistence} if database should be initialized.
   */
  ConfigPersistence getDbPersistence(ConfigPersistence seedConfigPersistence) throws IOException {
    LOGGER.info("Use database config persistence.");

    DatabaseConfigPersistence dbConfigPersistence;
    if (setupDatabase) {
      Database database = new ConfigsDatabaseInstance(
          configs.getConfigDatabaseUser(),
          configs.getConfigDatabasePassword(),
          configs.getConfigDatabaseUrl())
              .getAndInitialize();
      dbConfigPersistence = new DatabaseConfigPersistence(database)
          .loadData(seedConfigPersistence);
    } else {
      Database database = new ConfigsDatabaseInstance(
          configs.getConfigDatabaseUser(),
          configs.getConfigDatabasePassword(),
          configs.getConfigDatabaseUrl())
              .getInitialized();
      dbConfigPersistence = new DatabaseConfigPersistence(database);
    }

    return new ValidatingConfigPersistence(dbConfigPersistence);
  }

}
