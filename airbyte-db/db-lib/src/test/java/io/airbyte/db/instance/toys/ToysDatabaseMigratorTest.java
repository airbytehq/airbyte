/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.Database;
import io.airbyte.db.check.DatabaseAvailabilityCheck;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.AbstractDatabaseTest;
import io.airbyte.db.instance.DatabaseConstants;
import io.airbyte.db.instance.DatabaseMigrator;
import java.io.IOException;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.junit.jupiter.api.Test;

class ToysDatabaseMigratorTest extends AbstractDatabaseTest {

  private static final String PRE_MIGRATION_SCHEMA_DUMP = "toys_database/pre_migration_schema.txt";
  private static final String POST_MIGRATION_SCHEMA_DUMP = "toys_database/schema_dump.txt";

  @Override
  public Database getDatabase(final DataSource dataSource, final DSLContext dslContext) throws IOException {
    return new Database(dslContext);
  }

  @Test
  void testMigration() throws Exception {
    final DataSource dataSource = getDataSource();

    initializeDatabase(getDslContext());

    final Flyway flyway = FlywayFactory.create(dataSource, getClass().getSimpleName(), ToysDatabaseMigrator.DB_IDENTIFIER,
        ToysDatabaseMigrator.MIGRATION_FILE_LOCATION);
    final DatabaseMigrator migrator = new ToysDatabaseMigrator(database, flyway);

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

  private void initializeDatabase(final DSLContext dslContext) throws DatabaseInitializationException, IOException {
    final String initialSchema = MoreResources.readResource(ToysDatabaseConstants.SCHEMA_PATH);
    final DatabaseAvailabilityCheck availabilityCheck = new ToysDatabaseAvailabilityCheck(dslContext,
        DatabaseConstants.DEFAULT_CONNECTION_TIMEOUT_MS);
    new ToysDatabaseInitializer(availabilityCheck, dslContext, initialSchema).initialize();
  }

}
