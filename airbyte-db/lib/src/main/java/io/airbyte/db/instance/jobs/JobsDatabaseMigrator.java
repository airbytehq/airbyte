/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.FlywayDatabaseMigrator;

public class JobsDatabaseMigrator extends FlywayDatabaseMigrator {

  public static final String DB_IDENTIFIER = "jobs";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/jobs/migrations";

  public JobsDatabaseMigrator(Database database, String migrationRunner) {
    super(database, DB_IDENTIFIER, migrationRunner, MIGRATION_FILE_LOCATION);
  }

}
