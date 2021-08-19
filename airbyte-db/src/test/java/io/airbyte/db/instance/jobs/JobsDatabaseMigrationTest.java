/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db.instance.jobs;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.resources.MoreResources;
import io.airbyte.db.instance.DatabaseMigrator;
import io.airbyte.db.instance.MigrationHelper;
import java.io.IOException;
import java.util.List;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.output.MigrateResult;
import org.junit.Ignore;
import org.junit.jupiter.api.Test;

class JobsDatabaseMigrationTest extends AbstractJobsDatabaseTest {

  /**
   * This method generates a schema dump for the jobs database. The purpose is to ensure that the latest
   * schema is checked into the codebase after all migrations are executed.
   */
  @Test
  public void testSchemaDump() throws Exception {
    String schemaDump = MoreResources.readResource("jobs_database/schema_dump.txt").strip();
    DatabaseMigrator migrator = new JobsDatabaseMigrator(database, JobsDatabaseMigrationTest.class.getSimpleName());
    migrator.migrate();
    String newSchemaDump = migrator.dumpSchemaToFile();
    assertEquals(schemaDump, newSchemaDump);
  }

  /**
   * This method is used for migration development for the jobs database. Run it to see how your migration
   * changes the database schema.
   */
  @Ignore
  @Test
  public void runMigration() throws IOException {
    DatabaseMigrator migrator = new JobsDatabaseMigrator(database, JobsDatabaseMigrationTest.class.getSimpleName());
    migrator.baseline();

    List<MigrationInfo> preMigrationInfoList = migrator.info();
    System.out.println("\n==== Pre Migration Info ====\n" + MigrationHelper.format(preMigrationInfoList));
    System.out.println("\n==== Pre Migration Schema ====\n" + migrator.dumpSchema() + "\n");

    MigrateResult migrateResult = migrator.migrate();
    System.out.println("\n==== Migration Result ====\n" + MigrationHelper.format(migrateResult));

    List<MigrationInfo> postMigrationInfoList = migrator.info();
    System.out.println("\n==== Post Migration Info ====\n" + MigrationHelper.format(postMigrationInfoList));
    System.out.println("\n==== Post Migration Schema ====\n" + migrator.dumpSchema() + "\n");
  }

}
