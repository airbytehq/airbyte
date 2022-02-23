/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseInstance;
import io.airbyte.db.instance.DatabaseInstance;
import java.io.IOException;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobsDatabaseInstance extends BaseDatabaseInstance implements DatabaseInstance {

  private static final Logger LOGGER = LoggerFactory.getLogger(JobsDatabaseInstance.class);

  private static final String DATABASE_LOGGING_NAME = "airbyte jobs";
  private static final String SCHEMA_PATH = "jobs_database/schema.sql";
  private static final Function<Database, Boolean> IS_JOBS_DATABASE_READY = database -> {
    try {
      LOGGER.info("Testing if jobs database is ready...");
      return database.query(ctx -> JobsDatabaseSchema.getTableNames().stream().allMatch(table -> hasTable(ctx, table)));
    } catch (Exception e) {
      return false;
    }
  };

  @VisibleForTesting
  public JobsDatabaseInstance(final String username, final String password, final String connectionString, final String schema) {
    super(username, password, connectionString, schema, DATABASE_LOGGING_NAME, JobsDatabaseSchema.getTableNames(), IS_JOBS_DATABASE_READY);
  }

  public JobsDatabaseInstance(final String username, final String password, final String connectionString) throws IOException {
    this(username, password, connectionString, MoreResources.readResource(SCHEMA_PATH));
  }

}
