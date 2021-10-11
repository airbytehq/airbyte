/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.development.MigrationDevHelper;
import java.io.IOException;
import org.junit.jupiter.api.Test;

public class ConfigsDatabaseMigratorTest extends AbstractConfigsDatabaseTest {

  private static final String SCHEMA_DUMP_FILE = "src/main/resources/configs_database/schema_dump.txt";

  @Test
  public void dumpSchema() throws IOException {
    DatabaseMigrator migrator = new ConfigsDatabaseMigrator(database, ConfigsDatabaseMigratorTest.class.getSimpleName());
    migrator.migrate();
    String schema = migrator.dumpSchema();
    MigrationDevHelper.dumpSchema(schema, SCHEMA_DUMP_FILE, false);
  }

}
