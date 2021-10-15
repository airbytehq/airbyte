/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.instance.DatabaseMigrator;
import org.junit.jupiter.api.Test;

class ToysDatabaseMigratorTest extends AbstractToysDatabaseTest {

  private static final String PRE_MIGRATION_SCHEMA_DUMP = "toys_database/pre_migration_schema.txt";
  private static final String POST_MIGRATION_SCHEMA_DUMP = "toys_database/schema_dump.txt";

  @Test
  public void testMigration() throws Exception {
    DatabaseMigrator migrator = new ToysDatabaseMigrator(database, ToysDatabaseMigratorTest.class.getSimpleName());

    // Compare pre migration baseline schema
    migrator.createBaseline();
    String preMigrationSchema = MoreResources.readResource(PRE_MIGRATION_SCHEMA_DUMP).strip();
    String actualPreMigrationSchema = migrator.dumpSchema();
    assertEquals(preMigrationSchema, actualPreMigrationSchema, "The pre migration schema dump has changed");

    // Compare post migration schema
    migrator.migrate();
    String postMigrationSchema = MoreResources.readResource(POST_MIGRATION_SCHEMA_DUMP).strip();
    String actualPostMigrationSchema = migrator.dumpSchema();
    assertEquals(postMigrationSchema, actualPostMigrationSchema, "The post migration schema dump has changed");
  }

}
