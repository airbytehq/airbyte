/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import java.io.IOException;
import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;

public class ConfigsDatabaseMigratorTest extends AbstractConfigsDatabaseTest {

  private static final String SCHEMA_DUMP_FILE = "src/main/resources/configs_database/schema_dump.txt";

  @Test
  public void dumpSchema() throws IOException {
    final Flyway flyway = FlywayFactory.create(getDataSource(), getClass().getSimpleName(), ConfigsDatabaseMigrator.DB_IDENTIFIER,
        ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
    final DatabaseMigrator migrator = new ConfigsDatabaseMigrator(database, flyway);
    migrator.migrate();
    final String schema = migrator.dumpSchema();
    MigrationDevHelper.dumpSchema(schema, SCHEMA_DUMP_FILE, false);
  }

}
