/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.migrate.migrations;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.migrate.Migrations;
import org.junit.jupiter.api.Test;

class MigrationV0_30_0Test {

  @Test
  void testMigration() {
    // standard sync state does not exist before migration v0.30.0
    assertFalse(Migrations.MIGRATION_V_0_29_0.getOutputSchema().containsKey(MigrationV0_30_0.STANDARD_SYNC_STATE_RESOURCE_ID));
    assertTrue(Migrations.MIGRATION_V_0_30_0.getOutputSchema().containsKey(MigrationV0_30_0.STANDARD_SYNC_STATE_RESOURCE_ID));
  }

}
