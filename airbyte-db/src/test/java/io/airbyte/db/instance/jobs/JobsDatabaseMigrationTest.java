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
import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Path;
import org.junit.Ignore;
import org.junit.jupiter.api.Test;

class JobsDatabaseMigrationTest extends AbstractJobsDatabaseTest {

  /**
   * This method generates a schema dump for the jobs database. The purpose is to ensure that the
   * latest schema is checked into the codebase after all migrations are executed.
   */
  @Test
  public void testSchemaDump() throws Exception {
    String schemaDump = MoreResources.readResource("jobs_database/schema_dump.txt").strip();
    DatabaseMigrator migrator = new JobsDatabaseMigrator(database, JobsDatabaseMigrationTest.class.getSimpleName());
    migrator.migrate();
    String newSchemaDump = migrator.dumpSchemaToFile();
    assertEquals(schemaDump, newSchemaDump);
  }

  @Ignore
  @Test
  public void createMigration() throws IOException {
    String dbName = "jobs";
    String version = "0_29_10";
    String id = "002";
    String description = "New_migration";

    String template = MoreResources.readResource("migration_template.txt");
    String newMigration = template.replace("<db-name>", dbName)
        .replace("<version>", version)
        .replace("<id>", id)
        .replace("<description>", description)
        .strip();

    String fileName = String.format("V%s_%s__%s.java", version, id, description);
    String filePath = String.format("src/main/java/io/airbyte/db/instance/%s/migrations/%s", dbName, fileName);

    try (PrintWriter writer = new PrintWriter(new File(Path.of(filePath).toUri()))) {
      writer.println(newMigration);
    } catch (FileNotFoundException e) {
      throw new IOException(e);
    }
  }

  // Run this method to test your migration.
  @Ignore
  @Test
  public void runMigration() throws IOException {
    DatabaseMigrator migrator = new JobsDatabaseMigrator(database, JobsDatabaseMigrationTest.class.getSimpleName());
    runMigration(migrator);
  }

}
