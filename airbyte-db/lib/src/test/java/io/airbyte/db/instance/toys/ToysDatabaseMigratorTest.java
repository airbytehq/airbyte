/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.instance.AbstractDatabaseTest;
import io.airbyte.db.instance.DatabaseMigrator;
import java.io.IOException;
import org.junit.jupiter.api.Test;

class ToysDatabaseMigratorTest extends AbstractDatabaseTest {

  private static final String PRE_MIGRATION_SCHEMA_DUMP = "toys_database/pre_migration_schema.txt";
  private static final String POST_MIGRATION_SCHEMA_DUMP = "toys_database/schema_dump.txt";

  @Override
  public Database getDatabase() throws IOException {
    return new ToysDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
  }

  @Test
  public void testMigration() throws Exception {
    final DatabaseMigrator migrator = new ToysDatabaseMigrator(database, ToysDatabaseMigratorTest.class.getSimpleName());

    // Compare pre migration baseline schema
    migrator.createBaseline();
    final String preMigrationSchema = MoreResources.readResource(PRE_MIGRATION_SCHEMA_DUMP).strip();
    final String actualPreMigrationSchema = migrator.dumpSchema();
    assertEquals(preMigrationSchema, actualPreMigrationSchema, "The pre migration schema dump has changed");

    // Compare post migration schema
    migrator.migrate();
    final String postMigrationSchema = MoreResources.readResource(POST_MIGRATION_SCHEMA_DUMP).strip();
    final String actualPostMigrationSchema = migrator.dumpSchema();
    assertEquals(postMigrationSchema, actualPostMigrationSchema, "The post migration schema dump has changed");
  }

}
