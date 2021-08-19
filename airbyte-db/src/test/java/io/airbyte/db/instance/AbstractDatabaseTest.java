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

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import java.io.IOException;
import java.util.List;
import org.flywaydb.core.api.MigrationInfo;
import org.flywaydb.core.api.output.MigrateResult;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.testcontainers.containers.PostgreSQLContainer;

public abstract class AbstractDatabaseTest {

  protected static PostgreSQLContainer<?> container;

  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer<>("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();
  }

  @AfterAll
  public static void dbDown() {
    container.close();
  }

  protected Database database;

  @BeforeEach
  public void setup() throws Exception {
    database = getAndInitializeDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @AfterEach
  void tearDown() throws Exception {
    database.close();
  }

  /**
   * Create an initialized database. The downstream implementation should do it by calling
   * {@link DatabaseInstance#getAndInitialize}.
   */
  public abstract Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException;

  /**
   * This method is used for migration development. Run it to see how your migration changes the
   * database schema.
   */
  public void runMigration(DatabaseMigrator migrator) throws IOException {
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
