/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseInstance;
import io.airbyte.db.instance.DatabaseInstance;
import java.io.IOException;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ConfigsDatabaseInstance extends BaseDatabaseInstance implements DatabaseInstance {

  private static final Logger LOGGER = LoggerFactory.getLogger(ConfigsDatabaseInstance.class);

  private static final String DATABASE_LOGGING_NAME = "airbyte configs";
  private static final String SCHEMA_PATH = "configs_database/schema.sql";
  private static final Function<Database, Boolean> IS_CONFIGS_DATABASE_READY = database -> {
    try {
      LOGGER.info("Testing if airbyte_configs has been created and seeded...");
      return database.query(ctx -> hasData(ctx, "airbyte_configs"));
    } catch (Exception e) {
      return false;
    }
  };

  @VisibleForTesting
  public ConfigsDatabaseInstance(String username, String password, String connectionString, String schema) {
    super(username, password, connectionString, schema, DATABASE_LOGGING_NAME, ConfigsDatabaseSchema.getTableNames(), IS_CONFIGS_DATABASE_READY);
  }

  public ConfigsDatabaseInstance(String username, String password, String connectionString) throws IOException {
    this(username, password, connectionString, MoreResources.readResource(SCHEMA_PATH));
  }

}
