package io.airbyte.db.instance.development;

import java.io.IOException;

/**
 * This interface defines all the methods needed for migration development.
 */
public interface MigrationDevCenter {

  /**
   * 1. Run this method to create a new migration file.
   */
  void createMigration() throws IOException;

  /**
   * 2. Run this method to test the new migration.
   */
  void runLastMigration() throws IOException;

  /**
   * 3. This method performs the following to integration the latest migration changes:
   * <li>Update the schema dump.</li>
   * <li>Update jOOQ-generated code.</li>
   *
   * Please make sure to check in the changes after running this method.
   */
  void integrateMigration() throws Exception;

}
