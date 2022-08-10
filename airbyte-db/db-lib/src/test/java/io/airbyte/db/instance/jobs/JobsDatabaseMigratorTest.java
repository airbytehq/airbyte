/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import java.io.IOException;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class JobsDatabaseMigratorTest extends AbstractJobsDatabaseTest {

  private static final String SCHEMA_DUMP_FILE = "src/main/resources/jobs_database/schema_dump.txt";

  @Test
  void dumpSchema() throws IOException {
    final Flyway flyway = FlywayFactory.create(getDataSource(), getClass().getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
        JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    final DatabaseMigrator migrator = new JobsDatabaseMigrator(database, flyway);
    migrator.migrate();
    final String schema = migrator.dumpSchema();
    MigrationDevHelper.dumpSchema(schema, SCHEMA_DUMP_FILE, false);
  }

}
