/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseInstance;
import java.io.IOException;
import java.util.Collections;
import java.util.function.Function;

/**
 * A database instance for testing purposes only.
 */
public class ToysDatabaseInstance extends BaseDatabaseInstance {

  public static final String DATABASE_LOGGING_NAME = "toys";
  public static final String TABLE_NAME = "toy_cars";
  public static final String SCHEMA_PATH = "toys_database/schema.sql";
  public static final Function<Database, Boolean> IS_DATABASE_READY = database -> {
    try {
      return database.query(ctx -> hasTable(ctx, TABLE_NAME));
    } catch (Exception e) {
      return false;
    }
  };

  protected ToysDatabaseInstance(final String username, final String password, final String connectionString) throws IOException {
    super(username, password, connectionString, MoreResources.readResource(SCHEMA_PATH), DATABASE_LOGGING_NAME, Collections.singleton(TABLE_NAME),
        IS_DATABASE_READY);
  }

}
