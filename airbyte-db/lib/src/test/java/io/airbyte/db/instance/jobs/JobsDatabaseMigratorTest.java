/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.instance.development.MigrationDevHelper;
import java.io.IOException;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;

public class JobsDatabaseMigratorTest extends AbstractJobsDatabaseTest {

  private static final String SCHEMA_DUMP_FILE = "src/main/resources/jobs_database/schema_dump.txt";

  @Test
  public void dumpSchema() throws IOException {
    final Flyway migrator = MigrationDevHelper.createMigrator(dataSource, MigrationDevHelper.JOBS_DB_IDENTIFIER);
    migrator.migrate();
    final String schema = MigrationDevHelper.dumpSchema(database);
    MigrationDevHelper.dumpSchema(schema, SCHEMA_DUMP_FILE, false);
  }

}
