/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate;

import static org.junit.jupiter.api.Assertions.assertEquals;

import org.junit.jupiter.api.Test;

public class MigrationCurrentSchemaTest {

  @Test
  public void testLastMigration() {
    final Migration lastMigration = Migrations.MIGRATIONS.get(Migrations.MIGRATIONS.size() - 1);
    assertEquals(Migrations.MIGRATION_V_0_30_0.getVersion(), lastMigration.getVersion(),
        "The file-based migration is deprecated. Please do not write a new migration this way. Use Flyway instead.");
  }

}
