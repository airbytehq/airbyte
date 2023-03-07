/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.io.IOs;
import io.airbyte.db.instance.DatabaseConstants;
import io.airbyte.db.instance.development.MigrationDevCenter;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;

class JobsDatabaseMigrationDevCenterTest {

  /**
   * This test ensures that the dev center is working correctly end-to-end. If it fails, it means
   * either the migration is not run properly, or the database initialization is incorrect.
   */
  @Test
  void testSchemaDump() {
    final MigrationDevCenter devCenter = new JobsDatabaseMigrationDevCenter();
    final String schemaDump = IOs.readFile(Path.of(DatabaseConstants.JOBS_SCHEMA_DUMP_PATH));
    assertEquals(schemaDump.trim(), devCenter.dumpSchema(false));
  }

}
