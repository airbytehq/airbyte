package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.BaseDatabaseMigrator;

public class JobsDatabaseMigrator extends BaseDatabaseMigrator {

  public static final String DB_IDENTIFIER = "jobs";
  public static final String MIGRATION_FILE_LOCATION = "classpath:io/airbyte/db/instance/jobs/migrations";
  public static final String DB_SCHEMA_DUMP = "src/main/resources/jobs_database/schema_dump.txt";

  public JobsDatabaseMigrator(Database database, String migrationRunner) {
    super(database, DB_IDENTIFIER, migrationRunner, MIGRATION_FILE_LOCATION, DB_SCHEMA_DUMP);
  }

}
